import os
import logging
import re
from crewai import Task
from utils.file_writer import write_output
from memory.shared_memory import shared_memory
from docx import Document
from docx.shared import Inches
import graphviz

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_and_create_requirements_doc(task_output: str, output_base_dir_param: str):
    logging.info(f"--- Bắt đầu xử lý output cho Tài liệu Yêu cầu ---")
    doc = Document()
    doc.add_heading('Tài liệu Yêu cầu Phần mềm (SRS)', level=1)

    # Tách các khối mã DOT (giả định Use Case Diagram)
    dot_blocks = re.findall(r'```dot\s*([\s\S]*?)\s*```', task_output)
    text_content = re.sub(r'```dot\s*[\s\S]*?```', '', task_output).strip()

    use_case_text = text_content # Giả định phần còn lại là văn bản Use Cases
    use_case_dot_code = ""

    if len(dot_blocks) >= 1:
        use_case_dot_code = dot_blocks[0]
        logging.info("Đã trích xuất mã DOT cho Use Case Diagram.")

    # Thêm nội dung văn bản Use Case
    if use_case_text:
        doc.add_heading('Các Trường hợp Sử dụng (Use Cases)', level=2)
        doc.add_paragraph(use_case_text)
    else:
        doc.add_paragraph("Không có nội dung Use Case dạng văn bản được tạo.")

    # Đảm bảo thư mục con tồn tại cho output của phase này
    # === THAY ĐỔI DÒNG NÀY ===
    phase_output_dir = os.path.join(output_base_dir_param, "2_requirements")
    # ==========================
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục đầu ra cho Phase 2: {phase_output_dir}")

    # Render Use Case Diagram
    if use_case_dot_code:
        try:
            graph_use_case = graphviz.Source(use_case_dot_code, format='png', engine='dot')
            use_case_img_path = os.path.join(phase_output_dir, "use_case_diagram.png")
            graph_use_case.render(use_case_img_path.rsplit('.', 1)[0], view=False, cleanup=True)
            doc.add_heading('Use Case Diagram', level=2)
            doc.add_picture(use_case_img_path, width=Inches(6.0))
            logging.info(f"Đã tạo và chèn Use Case Diagram vào tài liệu: {use_case_img_path}")
        except Exception as e:
            logging.error(f"Lỗi khi tạo Use Case Diagram: {e}", exc_info=True)
            doc.add_paragraph(f"Không thể tạo Use Case Diagram do lỗi: {e}\nMã DOT thất bại:\n```dot\n{use_case_dot_code}\n```")
    else:
        doc.add_paragraph("Agent không tạo ra mã DOT cho Use Case Diagram.")

    final_doc_path = os.path.join(phase_output_dir, "Use_Case_Document_with_Diagram.docx")
    doc.save(final_doc_path)
    logging.info(f"Đã lưu tài liệu Use_Case_Document_with_Diagram.docx vào {final_doc_path}")

    shared_memory.set("phase_2_requirements", "use_case_document_path", final_doc_path)
    logging.info(f"--- Hoàn thành xử lý output cho Tài liệu Yêu cầu ---")


def create_requirement_tasks(requirement_analyst_agent, project_manager_agent, researcher_agent, output_base_dir):
    """
    Tạo các task liên quan đến giai đoạn Yêu cầu.
    Args:
        requirement_analyst_agent: Agent chính cho Requirements.
        project_manager_agent, researcher_agent: Các agent chung.
        output_base_dir: Đường dẫn thư mục base.
    Returns:
        list: Danh sách các Task đã tạo.
    """
    project_plan_content = shared_memory.get("phase_1_planning", "project_plan")
    if not project_plan_content:
        logging.warning("Project Plan content missing for requirements tasks.")
        project_plan_content = "Không có tài liệu Project Plan."

    # Tạo thư mục con cho Phase 2 Requirements (nếu chưa có)
    # === THAY ĐỔI DÒNG NÀY ===
    phase_output_dir = os.path.join(output_base_dir, "2_requirements")
    # ==========================
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục đầu ra cho Phase 2: {phase_output_dir}")

    # Task: Business Requirements Document (BRD)
    brd_task = Task(
        description=(
            f"Dựa trên Project Plan và các thông tin từ giai đoạn trước (Vision, ConOps), "
            f"phát triển Tài liệu Yêu cầu Nghiệp vụ (BRD). "
            f"Tập trung vào các yêu cầu cấp cao từ góc độ kinh doanh và stakeholder, không đi sâu vào chi tiết kỹ thuật.\n"
            f"--- Project Plan: {project_plan_content}"
        ),
        expected_output="Tài liệu tiếng Việt 'Business_Requirements_Document.docx' đầy đủ và có cấu trúc.",
        agent=requirement_analyst_agent,
        callback=lambda output: (
            logging.info(f"--- Hoàn thành BRD Task ---"),
            write_output(os.path.join(phase_output_dir, "Business_Requirements_Document.docx"), str(output)),
            shared_memory.set("phase_2_requirements", "brd_document", str(output)),
            logging.info(f"Đã lưu Business_Requirements_Document.docx và cập nhật shared_memory.")
        )
    )

    # Task: Software Requirements Specification (SRS)
    srs_task = Task(
        description=(
            f"Từ BRD (có trong context), chi tiết hóa các yêu cầu thành Tài liệu Đặc tả Yêu cầu Phần mềm (SRS). "
            f"Bao gồm các yêu cầu chức năng, phi chức năng, giao diện, và các ràng buộc.\n"
            f"--- BRD: {brd_task.output.raw_output if brd_task.output else 'Chưa có BRD.'}"
        ),
        expected_output="Tài liệu tiếng Việt 'Software_Requirements_Specification.docx' chi tiết, bao gồm tất cả các loại yêu cầu.",
        agent=requirement_analyst_agent,
        context=[brd_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành SRS Task ---"),
            write_output(os.path.join(phase_output_dir, "Software_Requirements_Specification.docx"), str(output)),
            shared_memory.set("phase_2_requirements", "srs_document", str(output)),
            logging.info(f"Đã lưu Software_Requirements_Specification.docx và cập nhật shared_memory.")
        )
    )

    # Task: Use Case Document - Sẽ tạo diagram
    use_case_task = Task(
        description=(
            f"Dựa trên SRS (có trong context), phát triển các Use Case chi tiết. "
            f"Mỗi Use Case cần mô tả: tên, mục tiêu, các tác nhân, luồng sự kiện chính và luồng thay thế. "
            f"Bạn phải **tạo mã nguồn Graphviz DOT** để biểu diễn Use Case dưới dạng sơ đồ Use Case. "
            f"Cấu trúc đầu ra của bạn phải là văn bản mô tả Use Cases, sau đó là mã DOT cho Use Case Diagram "
            f"(trong '```dot\\n...\\n```').\n"
            f"--- SRS: {srs_task.output.raw_output if srs_task.output else 'Chưa có SRS.'}"
        ),
        expected_output=(
            "Một chuỗi văn bản (string) bao gồm:\n"
            "1. Phần mô tả các Use Cases.\n"
            "2. Tiếp theo là mã Graphviz DOT cho Use Case Diagram được bọc trong '```dot\\n...\\n```'.\n"
            "Đảm bảo mã DOT đúng cú pháp để có thể render thành hình ảnh."
        ),
        agent=requirement_analyst_agent,
        context=[srs_task],
        callback=lambda output: process_and_create_requirements_doc(str(output), output_base_dir)
    )

    # Task: Requirements Traceability Matrix (RTM)
    rtm_task = Task(
        description=(
            f"Xây dựng Ma trận Truy vết Yêu cầu (RTM) để liên kết các yêu cầu từ BRD đến SRS và Use Cases. "
            f"Đảm bảo mỗi yêu cầu được truy vết và không bị bỏ sót.\n"
            f"--- BRD: {brd_task.output.raw_output if brd_task.output else 'Chưa có BRD.'}\n"
            f"--- SRS: {srs_task.output.raw_output if srs_task.output else 'Chưa có SRS.'}\n"
            f"--- Use Cases: {use_case_task.output.raw_output if use_case_task.output else 'Chưa có Use Cases.'}"
        ),
        expected_output="Tài liệu tiếng Việt 'Requirements_Traceability_Matrix.xlsx' (hoặc markdown) thể hiện mối quan hệ truy vết.",
        agent=requirement_analyst_agent,
        context=[brd_task, srs_task, use_case_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành RTM Task ---"),
            write_output(os.path.join(phase_output_dir, "Requirements_Traceability_Matrix.md"), str(output)),
            shared_memory.set("phase_2_requirements", "rtm_document", str(output)),
            logging.info(f"Đã lưu Requirements_Traceability_Matrix.md và cập nhật shared_memory.")
        )
    )

    # Task: Requirements Validation (Project Manager's Quality Gate)
    requirements_validation_task = Task(
        description=(
            f"Đánh giá kỹ lưỡng các tài liệu yêu cầu (BRD, SRS, Use Cases, RTM). "
            f"Kiểm tra tính hoàn chỉnh, rõ ràng, nhất quán và khả thi. "
            f"Tạo báo cáo 'Validation_Report_Phase_2.md' tóm tắt kết quả đánh giá, "
            f"liệt kê các điểm cần cải thiện nếu có và xác nhận hoàn thành giai đoạn."
        ),
        expected_output="Tài liệu tiếng Việt 'Validation_Report_Phase_2.md' tóm tắt kết quả đánh giá giai đoạn yêu cầu.",
        agent=project_manager_agent,
        context=[brd_task, srs_task, use_case_task, rtm_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Requirements Validation Task ---"),
            write_output(os.path.join(phase_output_dir, "Validation_Report_Phase_2.md"), str(output)),
            shared_memory.set("phase_2_requirements", "validation_report", str(output)),
            logging.info(f"Đã lưu Validation_Report_Phase_2.md và cập nhật shared_memory.")
        )
    )

    # Task: Research Requirements Best Practices (Researcher)
    research_requirements_best_practices = Task(
        description=(
            f"Nghiên cứu các phương pháp hay nhất (best practices) và tiêu chuẩn ngành trong quản lý yêu cầu phần mềm "
            f"(ví dụ: IEEE, BABOK, MoSCoW, SMART requirements). Tổng hợp kiến thức hỗ trợ các agent khác.\n"
            f"--- SRS: {srs_task.output.raw_output if srs_task.output else 'Chưa có SRS.'}"
        ),
        expected_output="Tài liệu tiếng Việt 'Requirements_Research_Summary.md' tổng hợp các kiến thức nghiên cứu hữu ích.",
        agent=researcher_agent,
        context=[srs_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Research Requirements Best Practices Task ---"),
            write_output(os.path.join(phase_output_dir, "Requirements_Research_Summary.md"), str(output)),
            shared_memory.set("phase_2_requirements", "research_summary", str(output)),
            logging.info(f"Đã lưu Requirements_Research_Summary.md và cập nhật shared_memory.")
        )
    )

    return [
        brd_task,
        srs_task,
        use_case_task,
        rtm_task,
        requirements_validation_task,
        research_requirements_best_practices
    ]
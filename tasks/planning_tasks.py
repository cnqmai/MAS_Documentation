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

def process_and_create_planning_doc(task_output: str, output_base_dir_param: str):
    logging.info(f"--- Bắt đầu xử lý output cho Kế hoạch Dự án ---")
    doc = Document()
    doc.add_heading('Tài liệu Kế hoạch Dự án', level=1)

    # Tách các khối mã DOT (giả định WBS là một sơ đồ cây)
    dot_blocks = re.findall(r'```dot\s*([\s\S]*?)\s*```', task_output)
    text_content = re.sub(r'```dot\s*[\s\S]*?```', '', task_output).strip()

    wbs_text = text_content # Giả định phần còn lại là văn bản WBS
    wbs_dot_code = ""

    if len(dot_blocks) >= 1:
        wbs_dot_code = dot_blocks[0]
        logging.info("Đã trích xuất mã DOT cho WBS.")

    # Thêm nội dung văn bản WBS
    if wbs_text:
        doc.add_heading('Cấu trúc Phân chia Công việc (WBS)', level=2)
        doc.add_paragraph(wbs_text)
    else:
        doc.add_paragraph("Không có nội dung WBS dạng văn bản được tạo.")

    # Đảm bảo thư mục con tồn tại cho output của phase này
    # === THAY ĐỔI DÒNG NÀY: Từ "2_planning" thành "1_planning" ===
    phase_output_dir = os.path.join(output_base_dir_param, "1_planning")
    # =============================================================
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục đầu ra cho Phase 1: {phase_output_dir}")

    # Render WBS Diagram
    if wbs_dot_code:
        try:
            graph_wbs = graphviz.Source(wbs_dot_code, format='png', engine='dot')
            wbs_img_path = os.path.join(phase_output_dir, "wbs_diagram.png")
            graph_wbs.render(wbs_img_path.rsplit('.', 1)[0], view=False, cleanup=True)
            doc.add_heading('WBS Diagram', level=2)
            doc.add_picture(wbs_img_path, width=Inches(6.0))
            logging.info(f"Đã tạo và chèn WBS Diagram vào tài liệu: {wbs_img_path}")
        except Exception as e:
            logging.error(f"Lỗi khi tạo WBS Diagram: {e}", exc_info=True)
            doc.add_paragraph(f"Không thể tạo WBS Diagram do lỗi: {e}\nMã DOT thất bại:\n```dot\n{wbs_dot_code}\n```")
    else:
        doc.add_paragraph("Agent không tạo ra mã DOT cho WBS Diagram.")

    final_doc_path = os.path.join(phase_output_dir, "Work_Breakdown_Structure_with_Diagram.docx")
    doc.save(final_doc_path)
    logging.info(f"Đã lưu tài liệu Work_Breakdown_Structure_with_Diagram.docx vào {final_doc_path}")

    shared_memory.set("phase_1_planning", "wbs_document_path", final_doc_path)
    logging.info(f"--- Hoàn thành xử lý output cho Kế hoạch Dự án ---")


def create_planning_tasks(planning_orchestrator_agent, project_manager_agent, researcher_agent, output_base_dir):
    """
    Tạo các task liên quan đến lập kế hoạch dự án.
    Args:
        planning_orchestrator_agent: Agent chính cho Planning.
        project_manager_agent, researcher_agent: Các agent chung.
        output_base_dir: Đường dẫn thư mục base.
    Returns:
        list: Danh sách các Task đã tạo.
    """
    project_charter_content = shared_memory.get("phase_0_initiation", "project_charter")
    if not project_charter_content:
        logging.warning("Project Charter content missing for planning tasks.")
        project_charter_content = "Không có tài liệu Project Charter."

    # Tạo thư mục con cho Phase 1 Planning (nếu chưa có)
    # === THAY ĐỔI DÒNG NÀY: Từ "2_planning" thành "1_planning" ===
    phase_output_dir = os.path.join(output_base_dir, "1_planning")
    # =============================================================
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục đầu ra cho Phase 1: {phase_output_dir}")

    # Task: Project Plan Creation
    project_plan_task = Task(
        description=(
            f"Dựa trên Project Charter sau, phát triển một Project Plan (Kế hoạch Dự án) chi tiết. "
            f"Bao gồm các phần chính như: Mục tiêu chi tiết, Phạm vi dự án, Lịch trình (Timeline), "
            f"Nguồn lực (Resources), Ngân sách sơ bộ, Quản lý rủi ro, và Kế hoạch truyền thông.\n"
            f"--- Project Charter: {project_charter_content}"
        ),
        expected_output="Tài liệu tiếng Việt 'Project_Plan.docx' đầy đủ và có cấu trúc.",
        agent=planning_orchestrator_agent,
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Project Plan Task ---"),
            write_output(os.path.join(phase_output_dir, "Project_Plan.docx"), str(output)),
            shared_memory.set("phase_1_planning", "project_plan", str(output)),
            logging.info(f"Đã lưu Project_Plan.docx và cập nhật shared_memory.")
        )
    )

    # Task: Work Breakdown Structure (WBS) - Sẽ tạo diagram
    wbs_task = Task(
        description=(
            f"Dựa trên Project Plan đã tạo, chi tiết hóa các công việc thành một Cấu trúc Phân chia Công việc (WBS) "
            f"theo định dạng phân cấp. Xác định các gói công việc chính và các đầu việc con cho từng giai đoạn dự án. "
            f"Bạn phải **tạo mã nguồn Graphviz DOT** để biểu diễn WBS dưới dạng sơ đồ cây phân cấp. "
            f"Cấu trúc đầu ra của bạn phải là văn bản mô tả WBS, sau đó là mã DOT cho WBS Diagram "
            f"(trong '```dot\\n...\\n```').\n"
            f"--- Project Plan: {project_plan_task.output.raw_output if project_plan_task.output else 'Chưa có Project Plan.'}"
        ),
        expected_output=(
            "Một chuỗi văn bản (string) bao gồm:\n"
            "1. Phần mô tả Cấu trúc Phân chia Công việc (WBS).\n"
            "2. Tiếp theo là mã Graphviz DOT cho WBS Diagram được bọc trong '```dot\\n...\\n```'.\n"
            "Đảm bảo mã DOT đúng cú pháp để có thể render thành hình ảnh."
        ),
        agent=planning_orchestrator_agent,
        context=[project_plan_task],
        callback=lambda output: process_and_create_planning_doc(str(output), output_base_dir)
    )

    # Task: Risk Management Plan
    risk_plan_task = Task(
        description=(
            f"Dựa trên Project Plan và WBS, phát triển Kế hoạch Quản lý Rủi ro. "
            f"Xác định các rủi ro tiềm ẩn, phân tích tác động và khả năng xảy ra, và đề xuất các chiến lược giảm thiểu.\n"
            f"--- Project Plan: {project_plan_task.output.raw_output if project_plan_task.output else 'Chưa có Project Plan.'}\n"
            f"--- WBS (từ wbs_task): {wbs_task.output.raw_output if wbs_task.output else 'Chưa có WBS.'}"
        ),
        expected_output="Tài liệu tiếng Việt 'Risk_Management_Plan.docx' đầy đủ, bao gồm phân tích và chiến lược rủi ro.",
        agent=planning_orchestrator_agent,
        context=[project_plan_task, wbs_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Risk Management Plan Task ---"),
            write_output(os.path.join(phase_output_dir, "Risk_Management_Plan.docx"), str(output)),
            shared_memory.set("phase_1_planning", "risk_management_plan", str(output)),
            logging.info(f"Đã lưu Risk_Management_Plan.docx và cập nhật shared_memory.")
        )
    )

    # Task: Project Planning Validation (Project Manager's Quality Gate)
    project_planning_validation_task = Task(
        description=(
            f"Đánh giá kỹ lưỡng các tài liệu Kế hoạch Dự án (Project Plan, WBS, Risk Management Plan) vừa được tạo. "
            f"Kiểm tra tính hoàn chỉnh, khả thi, nhất quán với Project Charter và các yêu cầu ban đầu. "
            f"Tạo một báo cáo 'Validation_Report_Phase_1.md' tóm tắt kết quả đánh giá, "
            f"liệt kê các điểm cần cải thiện nếu có và xác nhận việc hoàn thành giai đoạn."
        ),
        expected_output="Tài liệu tiếng Việt 'Validation_Report_Phase_1.md' tóm tắt kết quả đánh giá giai đoạn lập kế hoạch.",
        agent=project_manager_agent,
        context=[project_plan_task, wbs_task, risk_plan_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Project Planning Validation Task ---"),
            write_output(os.path.join(phase_output_dir, "Validation_Report_Phase_1.md"), str(output)),
            shared_memory.set("phase_1_planning", "validation_report", str(output)),
            logging.info(f"Đã lưu Validation_Report_Phase_1.md và cập nhật shared_memory.")
        )
    )

    # Task: Research Planning Best Practices (Researcher)
    research_planning_best_practices = Task(
        description=(
            f"Nghiên cứu các phương pháp hay nhất (best practices) và tiêu chuẩn ngành liên quan đến giai đoạn lập kế hoạch dự án "
            f"để hỗ trợ các agent khác. Ví dụ: cấu trúc điển hình của WBS, ước tính, quản lý rủi ro trong kế hoạch dự án.\n"
            f"--- Project Plan: {project_plan_task.output.raw_output if project_plan_task.output else 'Chưa có Project Plan.'}"
        ),
        expected_output="Tài liệu tiếng Việt 'Planning_Research_Summary.md' tổng hợp các kiến thức nghiên cứu hữu ích.",
        agent=researcher_agent,
        context=[project_plan_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Research Planning Best Practices Task ---"),
            write_output(os.path.join(phase_output_dir, "Planning_Research_Summary.md"), str(output)),
            shared_memory.set("phase_1_planning", "research_summary", str(output)),
            logging.info(f"Đã lưu Planning_Research_Summary.md và cập nhật shared_memory.")
        )
    )

    return [
        project_plan_task,
        wbs_task,
        risk_plan_task,
        project_planning_validation_task,
        research_planning_best_practices
    ]
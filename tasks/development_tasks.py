# tasks/development_tasks.py (Đã sửa đổi)

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

def process_and_create_dev_guidelines_doc(task_output: str, output_base_dir_param: str):
    logging.info(f"--- Bắt đầu xử lý output cho Hướng dẫn Phát triển ---")
    doc = Document()
    doc.add_heading('Tài liệu Hướng dẫn Phát triển', level=1)

    dot_blocks = re.findall(r'```dot\s*([\s\S]*?)\s*```', task_output)
    text_content = re.sub(r'```dot\s*[\s\S]*?```', '', task_output).strip()

    guidelines_text = text_content # Giả định phần còn lại là văn bản
    component_diagram_dot_code = ""

    if len(dot_blocks) >= 1:
        component_diagram_dot_code = dot_blocks[0]
        logging.info("Đã trích xuất mã DOT cho Component Diagram.")

    # Thêm nội dung văn bản
    if guidelines_text:
        doc.add_heading('Tiêu chuẩn Mã hóa và Hướng dẫn Phát triển', level=2)
        doc.add_paragraph(guidelines_text)
    else:
        doc.add_paragraph("Không có nội dung hướng dẫn phát triển dạng văn bản được tạo.")

    # Đảm bảo thư mục con tồn tại cho output của phase này
    # FIX: Change "5_development" to "4_development" here
    phase_output_dir = os.path.join(output_base_dir_param, "4_development")
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục đầu ra cho Phase 4: {phase_output_dir}")

    # Render Component Diagram
    if component_diagram_dot_code:
        try:
            graph_component = graphviz.Source(component_diagram_dot_code, format='png', engine='dot')
            component_img_path = os.path.join(phase_output_dir, "component_diagram.png")
            graph_component.render(component_img_path.rsplit('.', 1)[0], view=False, cleanup=True)
            doc.add_heading('Component Diagram', level=2)
            doc.add_picture(component_img_path, width=Inches(6.0))
            logging.info(f"Đã tạo và chèn Component Diagram vào tài liệu: {component_img_path}")
        except Exception as e:
            logging.error(f"Lỗi khi tạo Component Diagram: {e}", exc_info=True)
            doc.add_paragraph(f"Không thể tạo Component Diagram do lỗi: {e}\nMã DOT thất bại:\n```dot\n{component_diagram_dot_code}\n```")
    else:
        doc.add_paragraph("Agent không tạo ra mã DOT cho Component Diagram.")

    final_doc_path = os.path.join(phase_output_dir, "Coding_Standards_and_Guidelines_with_Diagram.docx")
    doc.save(final_doc_path)
    logging.info(f"Đã lưu tài liệu Coding_Standards_and_Guidelines_with_Diagram.docx vào {final_doc_path}")

    shared_memory.set("phase_4_development", "coding_standards_document_path", final_doc_path)
    logging.info(f"--- Hoàn thành xử lý output cho Hướng dẫn Phát triển ---")


def create_development_tasks(lead_software_engineer_agent, project_manager_agent, researcher_agent, output_base_dir):
    """
    Tạo các task liên quan đến giai đoạn Phát triển.
    Args:
        lead_software_engineer_agent: Agent chính cho Development.
        project_manager_agent, researcher_agent: Các agent chung.
        output_base_dir: Đường dẫn thư mục base.
    Returns:
        list: Danh sách các Task đã tạo.
    """
    system_design_doc_path = shared_memory.get("phase_3_design", "system_design_doc_path")
    db_design_doc = shared_memory.get("phase_3_design", "db_design_document")
    api_design_doc = shared_memory.get("phase_3_design", "api_design_document")

    design_context_for_dev = f"System Design Document (Path): {system_design_doc_path}\n" \
                             f"Database Design (Content Snippet): {db_design_doc[:500] if db_design_doc else 'N/A'}\n" \
                             f"API Design (Content Snippet): {api_design_doc[:500] if api_design_doc else 'N/A'}"
    if not system_design_doc_path and not db_design_doc and not api_design_doc:
        logging.warning("Design documents missing for development tasks.")
        design_context_for_dev = "Không có tài liệu thiết kế nào được tìm thấy."


    # Tạo thư mục con cho Phase 4 Development (nếu chưa có)
    phase_output_dir = os.path.join(output_base_dir, "4_development")
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục đầu ra cho Phase 4: {phase_output_dir}")


    # Task: Coding Standards and Guidelines - Sẽ tạo diagram
    coding_standards_task = Task(
        description=(
            f"Dựa trên các tài liệu thiết kế, tạo ra một bộ tiêu chuẩn mã hóa (Coding Standards) và hướng dẫn phát triển (Development Guidelines) "
            f"cho dự án. Bao gồm quy tắc đặt tên, cấu trúc thư mục, quy ước comment, và các thực hành tốt nhất cho ngôn ngữ/framework được chọn. "
            f"Bạn cũng phải **tạo mã nguồn Graphviz DOT** cho một Component Diagram đơn giản minh họa các module chính hoặc layer của ứng dụng "
            f"dựa trên thiết kế đã có. "
            f"Cấu trúc đầu ra của bạn phải là văn bản hướng dẫn, sau đó là mã DOT cho Component Diagram "
            f"(trong '```dot\\n...\\n```').\n"
            f"--- Design Context: {design_context_for_dev}"
        ),
        expected_output=(
            "Một chuỗi văn bản (string) bao gồm:\n"
            "1. Phần mô tả Tiêu chuẩn Mã hóa và Hướng dẫn Phát triển.\n"
            "2. Tiếp theo là mã Graphviz DOT cho Component Diagram được bọc trong '```dot\\n...\\n```'.\n"
            "Đảm bảo mã DOT đúng cú pháp để có thể render thành hình ảnh."
        ),
        agent=lead_software_engineer_agent,
        callback=lambda output: process_and_create_dev_guidelines_doc(str(output), output_base_dir)
    )

    # Task: Source Control Strategy
    source_control_task = Task(
        description=(
            f"Phát triển chiến lược quản lý mã nguồn (Source Control Strategy) cho dự án. "
            f"Xác định công cụ (Git), quy trình branching (ví dụ: Gitflow), và quy tắc commit.\n"
            f"--- Design Context: {design_context_for_dev}"
        ),
        expected_output="Tài liệu tiếng Việt 'Source_Control_Strategy.md' mô tả chi tiết chiến lược quản lý mã nguồn.",
        agent=lead_software_engineer_agent,
        context=[coding_standards_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Source Control Task ---"),
            write_output(os.path.join(phase_output_dir, "Source_Control_Strategy.md"), str(output)),
            shared_memory.set("phase_4_development", "source_control_strategy", str(output)),
            logging.info(f"Đã lưu Source_Control_Strategy.md và cập nhật shared_memory.")
        )
    )

    # Task: Build and Deployment Process Definition
    build_deploy_task = Task(
        description=(
            f"Định nghĩa quy trình Build và Deployment (CI/CD) sơ bộ cho hệ thống. "
            f"Xác định các bước từ mã nguồn đến môi trường triển khai, các công cụ tự động hóa dự kiến.\n"
            f"--- Design Context: {design_context_for_dev}"
        ),
        expected_output="Tài liệu tiếng Việt 'Build_Deployment_Process_Definition.md' mô tả quy trình build và deploy.",
        agent=lead_software_engineer_agent,
        context=[source_control_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Build and Deployment Process Task ---"),
            write_output(os.path.join(phase_output_dir, "Build_Deployment_Process_Definition.md"), str(output)),
            shared_memory.set("phase_4_development", "build_deploy_process", str(output)),
            logging.info(f"Đã lưu Build_Deployment_Process_Definition.md và cập nhật shared_memory.")
        )
    )

    # Task: Development Quality Gate (Project Manager)
    development_validation_task = Task(
        description=(
            f"Đánh giá các tài liệu phát triển (Coding Standards, Source Control Strategy, Build/Deployment Process). "
            f"Kiểm tra tính hoàn chỉnh, khả thi, tuân thủ tiêu chuẩn và yêu cầu thiết kế. "
            f"Tạo báo cáo 'Validation_Report_Phase_4.md' tóm tắt kết quả đánh giá, "
            f"liệt kê các điểm cần cải thiện nếu có và xác nhận hoàn thành giai đoạn."
        ),
        expected_output="Tài liệu tiếng Việt 'Validation_Report_Phase_4.md' tóm tắt kết quả đánh giá giai đoạn phát triển.",
        agent=project_manager_agent,
        context=[coding_standards_task, source_control_task, build_deploy_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Development Validation Task ---"),
            write_output(os.path.join(phase_output_dir, "Validation_Report_Phase_4.md"), str(output)),
            shared_memory.set("phase_4_development", "validation_report", str(output)),
            logging.info(f"Đã lưu Validation_Report_Phase_4.md và cập nhật shared_memory.")
        )
    )

    # Task: Research Development Best Practices (Researcher)
    research_development_best_practices = Task(
        description=(
            f"Nghiên cứu các phương pháp hay nhất (best practices) trong phát triển phần mềm "
            f"(ví dụ: Clean Code, TDD, DDD, kiến trúc phần mềm, quản lý dependency). "
            f"Tổng hợp kiến thức hỗ trợ các agent khác.\n"
            f"--- Design Context: {design_context_for_dev}"
        ),
        expected_output="Tài liệu tiếng Việt 'Development_Research_Summary.md' tổng hợp các kiến thức nghiên cứu hữu ích.",
        agent=researcher_agent,
        context=[coding_standards_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Research Development Best Practices Task ---"),
            write_output(os.path.join(phase_output_dir, "Development_Research_Summary.md"), str(output)),
            shared_memory.set("phase_4_development", "research_summary", str(output)),
            logging.info(f"Đã lưu Development_Research_Summary.md và cập nhật shared_memory.")
        )
    )

    return [
        coding_standards_task,
        source_control_task,
        build_deploy_task,
        development_validation_task,
        research_development_best_practices
    ]
# tasks/deployment_tasks.py (Đã sửa đổi)

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

def process_and_create_deployment_doc(task_output: str, output_base_dir_param: str):
    logging.info(f"--- Bắt đầu xử lý output cho Kế hoạch Triển khai ---")
    doc = Document()
    doc.add_heading('Tài liệu Kế hoạch Triển khai', level=1)

    dot_blocks = re.findall(r'```dot\s*([\s\S]*?)\s*```', task_output)
    text_content = re.sub(r'```dot\s*[\s\S]*?```', '', task_output).strip()

    deployment_plan_text = text_content # Giả định phần còn lại là văn bản
    deployment_diagram_dot_code = ""

    if len(dot_blocks) >= 1:
        deployment_diagram_dot_code = dot_blocks[0]
        logging.info("Đã trích xuất mã DOT cho Deployment Diagram.")

    # Thêm nội dung văn bản
    if deployment_plan_text:
        doc.add_heading('Kế hoạch Triển khai (Deployment Plan)', level=2)
        doc.add_paragraph(deployment_plan_text)
    else:
        doc.add_paragraph("Không có nội dung kế hoạch triển khai dạng văn bản được tạo.")

    # Đảm bảo thư mục con tồn tại cho output của phase này
    phase_output_dir = os.path.join(output_base_dir_param, "6_deployment")
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục đầu ra cho Phase 6: {phase_output_dir}")

    # Render Deployment Diagram
    if deployment_diagram_dot_code:
        try:
            graph_deployment = graphviz.Source(deployment_diagram_dot_code, format='png', engine='dot')
            deployment_img_path = os.path.join(phase_output_dir, "deployment_diagram.png")
            graph_deployment.render(deployment_img_path.rsplit('.', 1)[0], view=False, cleanup=True)
            doc.add_heading('Deployment Diagram', level=2)
            doc.add_picture(deployment_img_path, width=Inches(6.0))
            logging.info(f"Đã tạo và chèn Deployment Diagram vào tài liệu: {deployment_img_path}")
        except Exception as e:
            logging.error(f"Lỗi khi tạo Deployment Diagram: {e}", exc_info=True)
            doc.add_paragraph(f"Không thể tạo Deployment Diagram do lỗi: {e}\nMã DOT thất bại:\n```dot\n{deployment_diagram_dot_code}\n```")
    else:
        doc.add_paragraph("Agent không tạo ra mã DOT cho Deployment Diagram.")

    final_doc_path = os.path.join(phase_output_dir, "Deployment_Plan_with_Diagram.docx")
    doc.save(final_doc_path)
    logging.info(f"Đã lưu tài liệu Deployment_Plan_with_Diagram.docx vào {final_doc_path}")

    shared_memory.set("phase_6_deployment", "deployment_plan_document_path", final_doc_path)
    logging.info(f"--- Hoàn thành xử lý output cho Kế hoạch Triển khai ---")


def create_deployment_tasks(devops_engineer_agent, project_manager_agent, researcher_agent, output_base_dir):
    """
    Tạo các task liên quan đến giai đoạn Triển khai.
    Args:
        devops_engineer_agent: Agent chính cho Deployment.
        project_manager_agent, researcher_agent: Các agent chung.
        output_base_dir: Đường dẫn thư mục base.
    Returns:
        list: Danh sách các Task đã tạo.
    """
    test_execution_report = shared_memory.get("phase_5_testing", "test_execution_report")
    build_deploy_process = shared_memory.get("phase_4_development", "build_deploy_process")

    deployment_context = f"Test Execution Report (Snippet): {test_execution_report[:500] if test_execution_report else 'N/A'}\n" \
                         f"Build/Deployment Process (Snippet): {build_deploy_process[:500] if build_deploy_process else 'N/A'}"
    if not test_execution_report and not build_deploy_process:
        logging.warning("Previous phase documents missing for deployment tasks.")
        deployment_context = "Không có tài liệu liên quan nào được tìm thấy."

    # Tạo thư mục con cho Phase 7 Deployment (nếu chưa có)
    phase_output_dir = os.path.join(output_base_dir, "7_deployment")
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục đầu ra cho Phase 7: {phase_output_dir}")

    # Task: Deployment Plan - Sẽ tạo diagram
    deployment_plan_task = Task(
        description=(
            f"Dựa trên các tài liệu thiết kế và quy trình build/deploy, tạo Kế hoạch Triển khai (Deployment Plan) chi tiết. "
            f"Bao gồm các bước triển khai lên môi trường sản xuất, rollback plan, yêu cầu về môi trường, và các bên liên quan. "
            f"Bạn cũng phải **tạo mã nguồn Graphviz DOT** cho một Deployment Diagram minh họa cấu trúc vật lý của hệ thống "
            f"và nơi các thành phần phần mềm sẽ được triển khai. "
            f"Cấu trúc đầu ra của bạn phải là văn bản kế hoạch, sau đó là mã DOT cho Deployment Diagram "
            f"(trong '```dot\\n...\\n```').\n"
            f"--- Context: {deployment_context}"
        ),
        expected_output=(
            "Một chuỗi văn bản (string) bao gồm:\n"
            "1. Phần mô tả Kế hoạch Triển khai.\n"
            "2. Tiếp theo là mã Graphviz DOT cho Deployment Diagram được bọc trong '```dot\\n...\\n```'.\n"
            "Đảm bảo mã DOT đúng cú pháp để có thể render thành hình ảnh."
        ),
        agent=devops_engineer_agent,
        callback=lambda output: process_and_create_deployment_doc(str(output), output_base_dir)
    )

    # Task: Production Turnover Document
    turnover_doc_task = Task(
        description=(
            f"Tạo Tài liệu Bàn giao Sản xuất (Production Turnover Document). "
            f"Tài liệu này cung cấp thông tin cần thiết cho đội vận hành để quản lý và hỗ trợ hệ thống sau triển khai. "
            f"Bao gồm kiến trúc hệ thống, cấu hình, thông tin đăng nhập, quy trình vận hành tiêu chuẩn (SOPs), và liên hệ hỗ trợ.\n"
            f"--- Deployment Plan: {deployment_plan_task.output.raw_output if deployment_plan_task.output else 'Chưa có Deployment Plan.'}"
        ),
        expected_output="Tài liệu tiếng Việt 'Production_Turnover_Document.docx' chi tiết cho đội vận hành.",
        agent=devops_engineer_agent,
        context=[deployment_plan_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Production Turnover Document Task ---"),
            write_output(os.path.join(phase_output_dir, "Production_Turnover_Document.docx"), str(output)),
            shared_memory.set("phase_6_deployment", "production_turnover_document", str(output)),
            logging.info(f"Đã lưu Production_Turnover_Document.docx và cập nhật shared_memory.")
        )
    )

    # Task: Monitoring and Alerting Strategy
    monitoring_strategy_task = Task(
        description=(
            f"Phát triển Chiến lược Giám sát và Cảnh báo (Monitoring and Alerting Strategy) cho hệ thống đã triển khai. "
            f"Xác định các chỉ số quan trọng (KPIs), công cụ giám sát, ngưỡng cảnh báo, và quy trình xử lý cảnh báo.\n"
            f"--- Deployment Plan: {deployment_plan_task.output.raw_output if deployment_plan_task.output else 'Chưa có Deployment Plan.'}"
        ),
        expected_output="Tài liệu tiếng Việt 'Monitoring_Alerting_Strategy.md' mô tả chiến lược giám sát.",
        agent=devops_engineer_agent,
        context=[deployment_plan_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Monitoring Strategy Task ---"),
            write_output(os.path.join(phase_output_dir, "Monitoring_Alerting_Strategy.md"), str(output)),
            shared_memory.set("phase_6_deployment", "monitoring_strategy", str(output)),
            logging.info(f"Đã lưu Monitoring_Alerting_Strategy.md và cập nhật shared_memory.")
        )
    )

    # Task: Deployment Quality Gate (Project Manager)
    deployment_validation_task = Task(
        description=(
            f"Đánh giá kỹ lưỡng các tài liệu triển khai (Deployment Plan, Production Turnover Document, Monitoring Strategy). "
            f"Kiểm tra tính hoàn chỉnh, khả thi, và rủi ro. "
            f"Tạo báo cáo 'Validation_Report_Phase_6.md' tóm tắt kết quả đánh giá, "
            f"liệt kê các điểm cần cải thiện nếu có và xác nhận hoàn thành giai đoạn."
        ),
        expected_output="Tài liệu tiếng Việt 'Validation_Report_Phase_6.md' tóm tắt kết quả đánh giá giai đoạn triển khai.",
        agent=project_manager_agent,
        context=[deployment_plan_task, turnover_doc_task, monitoring_strategy_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Deployment Validation Task ---"),
            write_output(os.path.join(phase_output_dir, "Validation_Report_Phase_6.md"), str(output)),
            shared_memory.set("phase_6_deployment", "validation_report", str(output)),
            logging.info(f"Đã lưu Validation_Report_Phase_6.md và cập nhật shared_memory.")
        )
    )

    # Task: Research Deployment Best Practices (Researcher)
    research_deployment_best_practices = Task(
        description=(
            f"Nghiên cứu các phương pháp hay nhất (best practices) trong triển khai và vận hành phần mềm "
            f"(ví dụ: CI/CD, Infrastructure as Code, Blue/Green Deployment, Canary Releases). "
            f"Tổng hợp kiến thức hỗ trợ các agent khác.\n"
            f"--- Deployment Plan: {deployment_plan_task.output.raw_output if deployment_plan_task.output else 'Chưa có Deployment Plan.'}"
        ),
        expected_output="Tài liệu tiếng Việt 'Deployment_Research_Summary.md' tổng hợp các kiến thức nghiên cứu hữu ích.",
        agent=researcher_agent,
        context=[deployment_plan_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Research Deployment Best Practices Task ---"),
            write_output(os.path.join(phase_output_dir, "Deployment_Research_Summary.md"), str(output)),
            shared_memory.set("phase_6_deployment", "research_summary", str(output)),
            logging.info(f"Đã lưu Deployment_Research_Summary.md và cập nhật shared_memory.")
        )
    )

    return [
        deployment_plan_task,
        turnover_doc_task,
        monitoring_strategy_task,
        deployment_validation_task,
        research_deployment_best_practices
    ]
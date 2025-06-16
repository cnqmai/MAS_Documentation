# tasks/maintenance_tasks.py

import os
import logging
from crewai import Task
from utils.file_writer import write_output
from memory.shared_memory import shared_memory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_maintenance_tasks(site_reliability_engineer_agent, project_manager_agent, researcher_agent, output_base_dir):
    """
    Tạo các task liên quan đến giai đoạn Bảo trì.
    Args:
        site_reliability_engineer_agent: Agent chính cho Maintenance.
        project_manager_agent, researcher_agent: Các agent chung.
        output_base_dir: Đường dẫn thư mục base.
    Returns:
        list: Danh sách các Task đã tạo.
    """
    production_turnover_doc = shared_memory.get("phase_6_deployment", "production_turnover_document")
    monitoring_strategy = shared_memory.get("phase_6_deployment", "monitoring_strategy")

    maintenance_context = f"Production Turnover Document (Snippet): {production_turnover_doc[:500] if production_turnover_doc else 'N/A'}\n" \
                          f"Monitoring Strategy (Snippet): {monitoring_strategy[:500] if monitoring_strategy else 'N/A'}"
    if not production_turnover_doc and not monitoring_strategy:
        logging.warning("Previous phase documents missing for maintenance tasks.")
        maintenance_context = "Không có tài liệu liên quan nào được tìm thấy."


    # Tạo thư mục con cho Phase 7 Maintenance (nếu chưa có)
    phase_output_dir = os.path.join(output_base_dir, "7_maintenance")
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục đầu ra cho Phase 7: {phase_output_dir}")


    # Task: Maintenance Plan
    maintenance_plan_task = Task(
        description=(
            f"Tạo Kế hoạch Bảo trì (Maintenance Plan) cho hệ thống đã triển khai. "
            f"Bao gồm các hoạt động bảo trì định kỳ, nâng cấp, vá lỗi, quản lý phiên bản, và hỗ trợ kỹ thuật.\n"
            f"--- Context: {maintenance_context}"
        ),
        expected_output="Tài liệu tiếng Việt 'Maintenance_Plan.docx' đầy đủ và có cấu trúc.",
        agent=site_reliability_engineer_agent,
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Maintenance Plan Task ---"),
            write_output(os.path.join(phase_output_dir, "Maintenance_Plan.docx"), str(output)),
            shared_memory.set("phase_7_maintenance", "maintenance_plan", str(output)),
            logging.info(f"Đã lưu Maintenance_Plan.docx và cập nhật shared_memory.")
        )
    )

    # Task: Feedback and Improvement Process
    feedback_process_task = Task(
        description=(
            f"Thiết lập quy trình thu thập phản hồi người dùng và quy trình cải tiến liên tục cho hệ thống. "
            f"Xác định các kênh phản hồi, cách phân tích phản hồi, và quy trình đưa ra các cải tiến/nâng cấp.\n"
            f"--- Maintenance Plan: {maintenance_plan_task.output.raw_output if maintenance_plan_task.output else 'Chưa có Maintenance Plan.'}"
        ),
        expected_output="Tài liệu tiếng Việt 'Feedback_Improvement_Process.md' mô tả quy trình phản hồi và cải tiến.",
        agent=site_reliability_engineer_agent,
        context=[maintenance_plan_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Feedback Process Task ---"),
            write_output(os.path.join(phase_output_dir, "Feedback_Improvement_Process.md"), str(output)),
            shared_memory.set("phase_7_maintenance", "feedback_process", str(output)),
            logging.info(f"Đã lưu Feedback_Improvement_Process.md và cập nhật shared_memory.")
        )
    )

    # Task: Post-Implementation Review (Project Manager)
    post_implementation_review_task = Task(
        description=(
            f"Tiến hành Đánh giá Sau Triển khai (Post-Implementation Review) của toàn bộ dự án. "
            f"Đánh giá mức độ thành công của dự án so với các mục tiêu ban đầu, bài học kinh nghiệm, "
            f"và các khuyến nghị cho các dự án tương lai. Tạo báo cáo 'Post_Implementation_Review.md'.\n"
            f"--- Context: Toàn bộ thông tin từ shared_memory về các giai đoạn trước." # PM có thể truy cập toàn bộ shared_memory
        ),
        expected_output="Tài liệu tiếng Việt 'Post_Implementation_Review.md' tóm tắt đánh giá sau triển khai.",
        agent=project_manager_agent,
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Post-Implementation Review Task ---"),
            write_output(os.path.join(phase_output_dir, "Post_Implementation_Review.md"), str(output)),
            shared_memory.set("phase_7_maintenance", "post_implementation_review", str(output)),
            logging.info(f"Đã lưu Post_Implementation_Review.md và cập nhật shared_memory.")
        )
    )

    # Task: Research Maintenance Best Practices (Researcher)
    research_maintenance_best_practices = Task(
        description=(
            f"Nghiên cứu các phương pháp hay nhất (best practices) trong bảo trì và vận hành hệ thống "
            f"(ví dụ: ITIL, Site Reliability Engineering (SRE) practices, incident management). "
            f"Tổng hợp kiến thức hỗ trợ các agent khác.\n"
            f"--- Maintenance Plan: {maintenance_plan_task.output.raw_output if maintenance_plan_task.output else 'Chưa có Maintenance Plan.'}"
        ),
        expected_output="Tài liệu tiếng Việt 'Maintenance_Research_Summary.md' tổng hợp các kiến thức nghiên cứu hữu ích.",
        agent=researcher_agent,
        context=[maintenance_plan_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Research Maintenance Best Practices Task ---"),
            write_output(os.path.join(phase_output_dir, "Maintenance_Research_Summary.md"), str(output)),
            shared_memory.set("phase_7_maintenance", "research_summary", str(output)),
            logging.info(f"Đã lưu Maintenance_Research_Summary.md và cập nhật shared_memory.")
        )
    )

    return [
        maintenance_plan_task,
        feedback_process_task,
        post_implementation_review_task,
        research_maintenance_best_practices
    ]
import os
import logging
from crewai import Task
from utils.file_writer import write_output
from memory.shared_memory import shared_memory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_initiation_tasks(vision_agent, conops_agent, charter_agent,
                            project_manager_agent, researcher_agent,
                            output_base_dir): # ĐÃ LOẠI BỎ input_base_dir
    """
    Tạo các task liên quan đến khởi tạo dự án.
    Args:
        vision_agent, conops_agent, charter_agent: Agents cụ thể cho Initiation.
        project_manager_agent, researcher_agent: Các agent chung.
        output_base_dir: Đường dẫn thư mục base cho output của giai đoạn này.
    Returns:
        list: Danh sách các Task đã tạo.
    """
    # Lấy system_request_summary từ shared_memory
    system_request_summary = shared_memory.get("phase_0_initiation", "system_request_summary")
    if not system_request_summary:
        logging.warning("Lỗi: Không tìm thấy 'system_request_summary' trong shared_memory['phase_0_initiation']. Sử dụng giá trị mặc định.")
        system_request_summary = "Thông tin yêu cầu hệ thống bị thiếu."

    # Tạo thư mục con cho Phase 0 Initiation (nếu chưa có)
    phase_output_dir = os.path.join(output_base_dir, "0_initiation")
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục đầu ra cho Phase 0 Initiation: {phase_output_dir}")

    vision_task = Task(
        description=(
            f"Phân tích tài liệu System Request Summary sau và tạo tài liệu Tầm nhìn (Vision Document) "
            f"rõ ràng và truyền cảm hứng. Bao gồm mục tiêu, phạm vi, người dùng chính, và các tính năng cấp cao.\n"
            f"--- System Request Summary: {system_request_summary}\n---"
        ),
        expected_output="Tài liệu tiếng Việt 'Vision_Document.docx' đầy đủ và có cấu trúc.",
        agent=vision_agent,
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Vision Task ---"),
            write_output(os.path.join(phase_output_dir, "Vision_Document.docx"), str(output)),
            shared_memory.set("phase_0_initiation", "vision_document", str(output)),
            logging.info(f"Đã lưu Vision_Document.docx và cập nhật shared_memory.")
        )
    )

    conops_task = Task(
        description=(
            f"Nghiên cứu System Request Summary và Vision Document (từ context) để tạo Concept of Operations (ConOps) đầy đủ. "
            f"Mô tả cách hệ thống sẽ được sử dụng trong thực tế, các kịch bản người dùng chính, và luồng công việc.\n"
            f"--- System Request Summary: {system_request_summary}\n---"
        ),
        expected_output="Tài liệu tiếng Việt 'Concept_of_Operations.docx' đầy đủ, mô tả cách thức vận hành của hệ thống.",
        agent=conops_agent,
        context=[vision_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành ConOps Task ---"),
            write_output(os.path.join(phase_output_dir, "Concept_of_Operations.docx"), str(output)),
            shared_memory.set("phase_0_initiation", "conops_document", str(output)),
            logging.info(f"Đã lưu Concept_of_Operations.docx và cập nhật shared_memory.")
        )
    )

    charter_task = Task(
        description=(
            f"Dựa trên System Request Summary, Vision Document và ConOps (từ context), xây dựng Project Charter đầy đủ, "
            f"xác định rõ mục tiêu dự án, phạm vi, các bên liên quan, quyền hạn, ngân sách sơ bộ, và các mốc thời gian chính.\n"
            f"--- System Request Summary: {system_request_summary}\n---"
        ),
        expected_output="Tài liệu tiếng Việt 'Project_Charter.docx' đầy đủ, xác định rõ mục tiêu dự án, phạm vi, các bên liên quan và quyền hạn.",
        agent=charter_agent,
        context=[vision_task, conops_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Charter Task ---"),
            write_output(os.path.join(phase_output_dir, "Project_Charter.docx"), str(output)),
            shared_memory.set("phase_0_initiation", "project_charter", str(output)),
            logging.info(f"Đã lưu Project_Charter.docx và cập nhật shared_memory.")
        )
    )

    project_initiation_validation_task = Task(
        description=(
            f"Đánh giá kỹ lưỡng các tài liệu được tạo ra trong Giai đoạn Khởi tạo (Vision Document, ConOps, Project Charter). "
            f"Kiểm tra tính hoàn chỉnh, rõ ràng, nhất quán và tuân thủ các yêu cầu ban đầu. "
            f"Tạo một báo cáo 'Validation_Report_Phase_0.md' tóm tắt kết quả đánh giá, "
            f"liệt kê các điểm cần cải thiện nếu có và xác nhận việc hoàn thành giai đoạn."
        ),
        expected_output="Tài liệu tiếng Việt 'Validation_Report_Phase_0.md' tóm tắt kết quả đánh giá giai đoạn khởi tạo.",
        agent=project_manager_agent,
        context=[vision_task, conops_task, charter_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Project Initiation Validation Task ---"),
            write_output(os.path.join(phase_output_dir, "Validation_Report_Phase_0.md"), str(output)),
            shared_memory.set("phase_0_initiation", "validation_report", str(output)),
            logging.info(f"Đã lưu Validation_Report_Phase_0.md và cập nhật shared_memory.")
        )
    )

    research_initiation_best_practices = Task(
        description=(
            f"Nghiên cứu các phương pháp hay nhất (best practices) và tiêu chuẩn ngành liên quan đến giai đoạn khởi tạo dự án "
            f"để hỗ trợ các agent khác. Ví dụ: cấu trúc điển hình của Vision Document, ConOps, Project Charter.\n"
            f"--- Yêu cầu chung của dự án: {system_request_summary}"
        ),
        expected_output="Tài liệu tiếng Việt 'Initiation_Research_Summary.md' tổng hợp các kiến thức nghiên cứu hữu ích.",
        agent=researcher_agent,
        context=[project_initiation_validation_task], # Có thể dùng báo cáo validation làm context
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Research Initiation Best Practices Task ---"),
            write_output(os.path.join(phase_output_dir, "Initiation_Research_Summary.md"), str(output)),
            shared_memory.set("phase_0_initiation", "research_summary", str(output)),
            logging.info(f"Đã lưu Initiation_Research_Summary.md và cập nhật shared_memory.")
        )
    )

    return [
        vision_task,
        conops_task,
        charter_task,
        project_initiation_validation_task,
        research_initiation_best_practices
    ]
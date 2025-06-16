# tasks/quality_gate_tasks.py

from crewai import Task
from utils.file_writer import write_output
from memory.shared_memory import shared_memory
import os

def create_quality_gate_task(project_manager_agent, phase_name, output_key_to_validate, document_description, report_filename):
    """
    Tạo một task kiểm tra chất lượng (Quality Gate) cho một giai đoạn cụ thể.
    Task này sẽ yêu cầu Project Manager agent đánh giá đầu ra của giai đoạn trước.

    Args:
        project_manager_agent (Agent): Agent của Project Manager.
        phase_name (str): Tên của giai đoạn hiện tại (ví dụ: "Phase 1: Planning").
        output_key_to_validate (str): Khóa trong shared_memory chứa output cần được kiểm tra (ví dụ: "project_plan").
        document_description (str): Mô tả ngắn gọn về tài liệu/kết quả cần kiểm tra.
        report_filename (str): Tên file báo cáo validation (ví dụ: "validation_report_phase_1.md").

    Returns:
        Task: Một đối tượng CrewAI Task cho Quality Gate.
    """
    # Lấy nội dung cần validate từ shared_memory
    # Giả định shared_memory.get lấy từ phase hiện tại
    content_to_validate = shared_memory.get(phase_name.lower().replace(" ", "_").replace(":", ""), output_key_to_validate)

    if not content_to_validate:
        content_to_validate = f"Không tìm thấy nội dung cho '{output_key_to_validate}' trong shared_memory của '{phase_name}'. Vui lòng kiểm tra lại."
        print(f"Cảnh báo: {content_to_validate}")

    return Task(
        description=(
            f"Thực hiện Quality Gate cho {phase_name}. "
            f"Bạn, với vai trò Project Manager, hãy đánh giá kỹ lưỡng tài liệu/kết quả sau: '{document_description}'. "
            f"Cụ thể, hãy kiểm tra tính đầy đủ, chính xác, nhất quán và tuân thủ các tiêu chuẩn dự án.\n\n"
            f"--- Nội dung cần đánh giá từ {document_description} ({output_key_to_validate}):\n"
            f"{content_to_validate}\n\n"
            f"Dựa trên đánh giá của bạn, hãy tạo một báo cáo xác nhận (validation report) chi tiết."
        ),
        expected_output=(
            f"Một tài liệu tiếng Việt '{report_filename}' nêu rõ: "
            f"1. Trạng thái 'Passed' hoặc 'Failed' cho Quality Gate này. "
            f"2. Lý do chi tiết cho trạng thái đó (nếu Passed thì vì sao đạt yêu cầu, nếu Failed thì các điểm cần cải thiện cụ thể)."
            f"3. Các đề xuất để cải thiện (nếu có)."
        ),
        agent=project_manager_agent,
        callback=lambda output: (
            print(f"--- Hoàn thành Quality Gate Task cho {phase_name} ---"),
            write_output(os.path.join("output", phase_name.split(':')[0].strip().lower().replace(" ", "_"), report_filename), str(output)),
            shared_memory.set(phase_name.lower().replace(" ", "_").replace(":", ""), report_filename.replace(".md", ""), str(output))
        )
    )
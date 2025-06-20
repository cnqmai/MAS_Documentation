from crewai import Task
from utils.output_formats import create_docx
from memory.shared_memory import SharedMemory
import os
from utils.phase_outputs import phase_outputs

def create_quality_gate_tasks(shared_memory: SharedMemory, output_base_dir: str, project_manager_agent):
    """
    Tạo các tác vụ Quality Gate cho tất cả các giai đoạn của dự án.
    """
    tasks = []

    for phase_dir, output_docs in phase_outputs.items():
        phase_name = phase_dir.split('_', 1)[1].capitalize()

        quality_gate_task = Task(
            description=(
                f"Sử dụng công cụ `create_docx` để tạo tài liệu Báo cáo kiểm tra chất lượng (Quality Gate Report) cho giai đoạn {phase_name}. "
                f"Kiểm tra các tài liệu đầu ra ({', '.join(output_docs)}) trong SharedMemory để đảm bảo tính đầy đủ, chính xác, và hợp lệ theo các tiêu chuẩn như ISTQB, PMBOK, hoặc các tiêu chuẩn ngành liên quan. "
                f"Tài liệu phải bao gồm: danh sách tài liệu được kiểm tra, tiêu chí đánh giá (tính đầy đủ, chính xác, định dạng, tuân thủ tiêu chuẩn), kết quả kiểm tra (đạt/không đạt), các vấn đề phát hiện, khuyến nghị khắc phục. "
                f"Lưu tài liệu dưới dạng `.docx` trong thư mục `output/{phase_dir}` với tên `Quality_Gate_Report.docx`. "
                f"Lưu kết quả vào SharedMemory với key `quality_gate_{phase_dir}`."
            ),
            agent=project_manager_agent,
            expected_output=(
                f"Tài liệu `Quality_Gate_Report.docx` chứa báo cáo kiểm tra chất lượng cho giai đoạn {phase_name}, "
                f"được lưu trong `output/{phase_dir}` và SharedMemory với key `quality_gate_{phase_dir}`."
            ),
            callback=lambda output, phase=phase_name, dir=phase_dir: create_docx(
                f"Báo cáo kiểm tra chất lượng - {phase}",
                [
                    f"1. Danh sách tài liệu: {', '.join(output_docs)}.",
                    "2. Tiêu chí đánh giá: Tính đầy đủ, chính xác, định dạng, tuân thủ tiêu chuẩn.",
                    "3. Kết quả kiểm tra: Đạt hoặc không đạt cho từng tài liệu.",
                    "4. Vấn đề phát hiện: Các lỗi hoặc thiếu sót trong tài liệu.",
                    "5. Khuyến nghị khắc phục: Đề xuất cải thiện chất lượng tài liệu.",
                ] + [str(shared_memory.load(doc)) or f"Không có dữ liệu cho {doc}" for doc in output_docs],
                f"{output_base_dir}/{dir}/0_Quality_Gate_Report.docx"
            ) and shared_memory.save(f"quality_gate_{dir}", output)
        )
        tasks.append(quality_gate_task)

    return tasks
from crewai import Task
from utils.output_formats import create_docx
from memory.shared_memory import SharedMemory
import os.path
from utils.phase_outputs import phase_outputs

def create_research_tasks(shared_memory: SharedMemory, output_base_dir: str, researcher_agent):
    """
    Tạo các tác vụ Research cho tất cả các giai đoạn của dự án.
    """
    tasks = []
    
    for phase_dir, output_docs in phase_outputs.items():
        phase_name = phase_dir.split('_', 1)[1].capitalize()

        research_task = Task(
            description=(
                f"Sử dụng công cụ `create_docx` để tạo tài liệu Phương pháp tốt nhất (Best Practices) cho giai đoạn {phase_name}. "
                f"Nghiên cứu các phương pháp tốt nhất dựa trên tiêu chuẩn ngành (PMBOK, Agile, IEEE, hoặc các nguồn đáng tin cậy) để tối ưu hóa quy trình và tài liệu của giai đoạn này. "
                f"Tập trung đặc biệt vào các giai đoạn Initiation, Planning, và Requirements (nếu áp dụng), với các ví dụ cụ thể về cách áp dụng các phương pháp này vào các tài liệu như {', '.join(output_docs)}. "
                f"Tài liệu phải bao gồm: giới thiệu, mục đích, danh sách phương pháp tốt nhất, ví dụ áp dụng, lợi ích, tài liệu tham khảo. "
                f"Lưu tài liệu dưới dạng `.docx` trong thư mục `output/{phase_dir}` với tên `Best_Practice_{phase_name}.docx`. "
                f"Lưu kết quả vào SharedMemory với key `best_practices_{phase_dir}`."
            ),
            agent=researcher_agent,
            expected_output=(
                f"Tài liệu `Best_Practice_{phase_name}.docx` chứa phương pháp tốt nhất cho giai đoạn {phase_name}, "
                f"được lưu trong `output/{phase_dir}` và SharedMemory với key `best_practices_{phase_dir}`."
            ),
            callback=lambda output, phase=phase_name, dir=phase_dir: create_docx(
                f"Phương pháp tốt nhất - {phase}",
                [
                    f"1. Giới thiệu: Mục đích của phương pháp tốt nhất cho giai đoạn {phase}.",
                    "2. Danh sách phương pháp: Các phương pháp tốt nhất theo tiêu chuẩn ngành (PMBOK, Agile, IEEE).",
                    f"3. Ví dụ áp dụng: Cách áp dụng vào các tài liệu như {', '.join(output_docs)}.",
                    "4. Lợi ích: Lợi ích của việc áp dụng phương pháp tốt nhất.",
                    "5. Tài liệu tham khảo: Các nguồn tham khảo (PMBOK, IEEE, v.v.).",
                    f"6. Ghi chú đặc biệt: Tăng cường tập trung vào Initiation, Planning, Requirements (nếu là giai đoạn {phase})."
                ],
                os.path.join(output_base_dir, dir, f"Best_Practice_{phase}.docx")
            ) and shared_memory.save(f"best_practices_{dir}", output)
        )
        tasks.append(research_task)

    return tasks
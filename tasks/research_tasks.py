import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx
from utils.phase_outputs import phase_outputs

# --- Hàm Callback cho DOCX ---
def make_docx_callback(title, filename, shared_memory, save_key):
    def callback(output_from_agent_object):
        print(f"Bắt đầu tạo DOCX cho: {title}...")
        content_raw_string = (
            getattr(output_from_agent_object, "result", None)
            or getattr(output_from_agent_object, "response", None)
            or getattr(output_from_agent_object, "final_output", None)
            or str(output_from_agent_object)
        )
        content_raw_string = str(content_raw_string)
        if not content_raw_string.strip():
            print(f"⚠️  Lưu ý: Agent không trả về nội dung cho task '{title}'.")
            return False
        content_paragraphs = content_raw_string.split('\n')
        docx_path = create_docx(title, content_paragraphs, filename)
        shared_memory.save(save_key, content_raw_string)
        if docx_path:
            print(f"✅ DOCX '{filename}' đã tạo thành công và lưu vào SharedMemory '{save_key}'.")
            return True
        else:
            print(f"❌ Lỗi hệ thống: Không thể tạo DOCX '{filename}'.")
            return False
    return callback

# --- Hàm tạo Task chính ---
def create_research_tasks(shared_memory: SharedMemory, output_base_dir: str, researcher_agent):
    tasks = []

    for phase_dir, output_docs in phase_outputs.items():
        phase_name = phase_dir.split('_', 1)[1].capitalize()
        os.makedirs(os.path.join(output_base_dir, phase_dir), exist_ok=True)

        tasks.append(Task(
            description=(
                f"Nghiên cứu các phương pháp tốt nhất (Best Practices) cho giai đoạn {phase_name} dựa trên tiêu chuẩn ngành (PMBOK, Agile, IEEE, hoặc các nguồn đáng tin cậy) để tối ưu hóa quy trình và tài liệu của giai đoạn này. "
                f"Tập trung đặc biệt vào các giai đoạn Initiation, Planning, và Requirements (nếu áp dụng), với các ví dụ cụ thể về cách áp dụng các phương pháp này vào các tài liệu như {', '.join(output_docs)}. "
                f"Tài liệu phải bao gồm nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào: giới thiệu, mục đích, danh sách phương pháp tốt nhất, ví dụ áp dụng, lợi ích, tài liệu tham khảo. "
                f"Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
            ),
            agent=researcher_agent,
            expected_output=(
                f"Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên nghiên cứu tiêu chuẩn ngành (PMBOK, Agile, IEEE). "
                f"Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
                f"Sẵn sàng để chuyển sang file DOCX cho giai đoạn {phase_name}."
            ),
            context=[{
                "description": f"Thông tin về các tài liệu đầu ra của giai đoạn {phase_name}",
                "expected_output": f"Tóm tắt các tài liệu như {', '.join(output_docs)} để áp dụng phương pháp tốt nhất.",
                "input": f"Danh sách tài liệu: {', '.join(output_docs)}"
            }],
            callback=make_docx_callback(
                f"Phương pháp tốt nhất - {phase_name}",
                os.path.join(output_base_dir, phase_dir, f"Best_Practice_{phase_name}.docx"),
                shared_memory,
                f"best_practices_{phase_dir}"
            )
        ))

    return tasks
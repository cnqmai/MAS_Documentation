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
def create_quality_gate_tasks(shared_memory: SharedMemory, output_base_dir: str, project_manager_agent):
    tasks = []

    for phase_dir, output_docs in phase_outputs.items():
        phase_name = phase_dir.split('_', 1)[1].capitalize()
        os.makedirs(os.path.join(output_base_dir, phase_dir), exist_ok=True)

        global_context = {doc: shared_memory.load(doc) for doc in output_docs}

        tasks.append(Task(
            description=(
                f"Kiểm tra các tài liệu đầu ra của giai đoạn {phase_name} để đảm bảo tính đầy đủ, chính xác, và hợp lệ theo các tiêu chuẩn như ISTQB, PMBOK, hoặc các tiêu chuẩn ngành liên quan. "
                f"Dưới đây là dữ liệu của các tài liệu:\n\n"
                + '\n\n'.join([f"{doc}:\n{global_context[doc] or 'Không có dữ liệu'}" for doc in output_docs]) + "\n\n"
                f"Tài liệu phải bao gồm nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào: danh sách tài liệu được kiểm tra ({', '.join(output_docs)}), tiêu chí đánh giá (tính đầy đủ, chính xác, định dạng, tuân thủ tiêu chuẩn), kết quả kiểm tra (đạt/không đạt), các vấn đề phát hiện, khuyến nghị khắc phục. "
                f"Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
            ),
            agent=project_manager_agent,
            expected_output=(
                f"Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên kiểm tra các tài liệu {', '.join(output_docs)} theo tiêu chuẩn ngành (ISTQB, PMBOK). "
                f"Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
                f"Sẵn sàng để chuyển sang file DOCX cho giai đoạn {phase_name}."
            ),
            context=[
                {
                    "description": f"Thông tin về các tài liệu đầu ra của giai đoạn {phase_name}",
                    "expected_output": f"Kiểm tra tính đầy đủ và chính xác của các tài liệu như {', '.join(output_docs)}.",
                    "input": f"Danh sách tài liệu: {', '.join(output_docs)}\n\n" + '\n'.join([f"{doc}: {str(global_context[doc]) or 'Không có dữ liệu'}" for doc in output_docs])
                }
            ],
            callback=make_docx_callback(
                f"Báo cáo kiểm định chất lượng - {phase_name}",
                os.path.join(output_base_dir, phase_dir, "Quality_Gate_0.docx"),
                shared_memory,
                f"quality_gate_{phase_dir}"
            )
        ))

    return tasks
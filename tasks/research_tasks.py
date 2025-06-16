# tasks/research_tasks.py

from crewai import Task
from memory.shared_memory import shared_memory
from utils.file_writer import write_output
import os

def create_research_task(researcher_agent, phase_name: str, topic_or_key: str, output_filename: str):
    """
    Tạo một task nghiên cứu chung cho Researcher Agent.

    Args:
        researcher_agent: Instance của Researcher Agent.
        phase_name (str): Tên của giai đoạn hiện tại (ví dụ: "Phase 0: Initiation", "Phase 1: Planning").
        topic_or_key (str): Có thể là:
                            - Một chuỗi mô tả chủ đề nghiên cứu trực tiếp (ví dụ: "phương pháp lập kế hoạch dự án").
                            - Hoặc một key trong shared_memory của phase hiện tại
                              mà Researcher Agent nên đọc để tìm các từ khóa/yêu cầu nghiên cứu.
        output_filename (str): Tên file để lưu kết quả nghiên cứu (bao gồm cả phần mở rộng).
    """
    # Chuẩn hóa tên thư mục output
    # Ví dụ: "Phase 0: Initiation" -> "0_initiation"
    phase_dir_name = phase_name.split(':')[0].strip().replace('Phase ', '').replace(' ', '_').lower()

    # Xử lý trường hợp topic_or_key là một key trong shared_memory
    research_query = topic_or_key
    if shared_memory.get(phase_dir_name, topic_or_key):
        # Nếu topic_or_key là một key trong shared_memory, lấy nội dung từ đó
        # Đây là nơi Researcher Agent sẽ lấy "Query_Keywords" hoặc "Phase_Specific_Requirements"
        research_query = shared_memory.get(phase_dir_name, topic_or_key)
        print(f"[Research Task] Lấy nội dung nghiên cứu từ shared_memory[{phase_dir_name}][{topic_or_key}]:\n{research_query[:100]}...")
    elif shared_memory.get("system_input", topic_or_key): # Kiểm tra cả system_input phase
        research_query = shared_memory.get("system_input", topic_or_key)
        print(f"[Research Task] Lấy nội dung nghiên cứu từ shared_memory['system_input'][{topic_or_key}]:\n{research_query[:100]}...")


    return Task(
        description=(
            f"Thực hiện nghiên cứu chuyên sâu dựa trên thông tin sau cho {phase_name}: \n"
            f"**Chủ đề/Yêu cầu nghiên cứu:**\n{research_query}\n\n"
            f"Hãy cung cấp thông tin, tài liệu tham khảo, các phương pháp hay nhất hoặc mẫu cần thiết. "
            f"Tóm tắt các phát hiện chính và lưu trữ chúng để các agent khác có thể sử dụng."
        ),
        expected_output=f"Một báo cáo nghiên cứu chi tiết bằng tiếng Việt về chủ đề đã cho, "
                        f"được lưu vào file '{output_filename}' trong thư mục output của phase.",
        agent=researcher_agent,
        callback=lambda output: (
            print(f"--- Hoàn thành Research Task cho {phase_name} về {topic_or_key} ---"),
            write_output(os.path.join("output", phase_dir_name, output_filename), str(output)),
            # Lưu vào shared_memory với key là tên file (không có phần mở rộng)
            shared_memory.set(phase_dir_name, output_filename.rsplit('.', 1)[0], str(output))
        )
    )
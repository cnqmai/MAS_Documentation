import logging
import os
from crewai import Task
from memory.shared_memory import SharedMemory # Đảm bảo đường dẫn này đúng

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_input_tasks(shared_memory: SharedMemory, input_base_dir: str, input_agent):
    """
    Tạo các tác vụ cho Input Agent để thu thập và xử lý yêu cầu đầu vào thông qua hội thoại tương tác.
    """
    tasks = []

    # Đảm bảo thư mục đầu vào tồn tại
    os.makedirs(input_base_dir, exist_ok=True)

    # Tác vụ thu thập yêu cầu từ người dùng/stakeholders
    collect_requirements_task = Task(
        description=(
            "Thực hiện quy trình thu thập yêu cầu chi tiết từ người dùng và các bên liên quan thông qua "
            "một cuộc **hội thoại tương tác, hỏi đáp động** (dynamic, interactive questioning session). "
            "Bạn phải sử dụng khả năng của mình để đặt **MỘT câu hỏi mỗi lần** dựa trên ngữ cảnh hội thoại đã có. "
            "Hãy đặt câu hỏi để làm rõ các yêu cầu về **Mục tiêu dự án, Phạm vi (tính năng chính/phụ), "
            "Người dùng mục tiêu, Vấn đề hiện tại cần giải quyết, Các tính năng mong muốn, "
            "Công nghệ ưa thích (nếu có), và Ràng buộc (ngân sách/thời gian)**. "
            "Nếu người dùng trả lời không rõ ràng hoặc quá ngắn gọn, hãy đặt lại câu hỏi theo cách khác "
            "hoặc chuyển sang khía cạnh khác để tiếp tục thu thập thông tin."
            "Sau mỗi câu hỏi, bạn sẽ chờ phản hồi từ người dùng."
            "**QUAN TRỌNG:**"
            "   - **Nếu bạn đã thu thập đủ thông tin quan trọng** để tạo bản tóm tắt yêu cầu hệ thống toàn diện, "
            "     hãy tự động kết thúc phiên hỏi đáp và bắt đầu tạo bản tóm tắt cuối cùng."
            "   - **Nếu người dùng muốn dừng lại và yêu cầu bản tóm tắt ngay lập tức**, họ sẽ gõ 'DỪNG' hoặc 'TÓM TẮT'. "
            "     Khi nhận được tín hiệu này, bạn phải dừng việc đặt câu hỏi và ngay lập tức tạo một bản **tóm tắt yêu cầu hệ thống chi tiết và toàn diện** "
            "     dựa trên tất cả thông tin đã thu thập được cho đến thời điểm đó."
            "Đảm bảo bản tóm tắt này phản ánh đầy đủ ý định của các bên liên quan. "
            f"Bạn cần **lưu toàn bộ lịch sử câu hỏi và câu trả lời** của phiên tương tác này "
            f"vào một file nhật ký trong thư mục '{input_base_dir}' (ví dụ: `initial_requirements_conversation.md`). "
            f"Cuối cùng, lưu bản tóm tắt yêu cầu hệ thống cuối cùng vào file `System_Request_Summary.md` "
            f"trong thư mục '{input_base_dir}'. "
            "Đây là một quá trình tương tác, do đó bạn cần chuẩn bị để chờ đợi và xử lý các phản hồi của người dùng."
        ),
        agent=input_agent,
        expected_output=(
            "Một bản tóm tắt yêu cầu hệ thống chi tiết và toàn diện (dưới dạng văn bản) "
            "chứa các yêu cầu chức năng, phi chức năng, mục tiêu dự án, phạm vi, v.v. "
            "đã được xác định thông qua phiên hỏi đáp tương tác. "
            "Kèm theo đó là file `System_Request_Summary.md` chứa bản tóm tắt này "
            "và file `initial_requirements_conversation.md` chứa toàn bộ lịch sử hội thoại, "
            "cả hai đều nằm trong thư mục `{input_base_dir}`. "
            "Dữ liệu tóm tắt cũng sẽ được lưu vào SharedMemory với khóa `system_request_summary`."
        ),
        callback=lambda output: shared_memory.set("phase_0_initiation", "system_request_summary", output),
        human_input=True # Đánh dấu rằng task này yêu cầu tương tác của con người
    )

    tasks.append(collect_requirements_task)
    return tasks
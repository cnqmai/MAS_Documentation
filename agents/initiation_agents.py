from crewai import Agent
import logging
import os
from utils.output_formats import create_docx, create_xlsx

def create_initiation_agent(output_base_dir):
    """
    Tạo agent chuyên xử lý các tác vụ khởi tạo dự án.
    """
    model_string = "gemini/gemini-1.5-flash-latest"  # Hoặc "gemini/gemini-pro"
    logging.info(f"Đang cấu hình Initiation Agent với LLM: {model_string}")

    initiation_agent = Agent(
        role='Chuyên gia khởi tạo dự án',
        goal=(
            'Tạo các tài liệu khởi tạo dự án chi tiết và toàn diện, bao gồm Bản điều lệ dự án, Nghiên cứu khả thi, Tài liệu trường hợp kinh doanh, '
            'Chương trình nghị sự khởi tạo, Mẫu giá trị đề xuất, Kế hoạch tài nguyên, và các tài liệu hỗ trợ khác. '
            'Đảm bảo rằng các tài liệu này phản ánh chính xác các yêu cầu ban đầu từ người dùng và các bên liên quan, '
            'cung cấp một nền tảng rõ ràng và có cấu trúc cho các giai đoạn phát triển tiếp theo của dự án. '
            'Tất cả tài liệu phải tuân thủ các tiêu chuẩn quản lý dự án quốc tế như PMI hoặc PRINCE2.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia khởi tạo dự án** với hơn 12 năm kinh nghiệm trong việc thiết lập các dự án thành công từ giai đoạn ý tưởng ban đầu. '
            'Bạn có khả năng vượt trội trong việc chuyển đổi các yêu cầu mơ hồ thành các tài liệu có cấu trúc, dễ hiểu và được các bên liên quan chấp thuận. '
            'Bạn đã làm việc với nhiều dự án đa ngành, sử dụng các phương pháp quản lý dự án tiên tiến để đảm bảo rằng các tài liệu khởi tạo đáp ứng các tiêu chuẩn chất lượng cao nhất. '
            'Nhiệm vụ của bạn là tạo ra các tài liệu nền tảng, cung cấp một lộ trình rõ ràng cho dự án và đảm bảo sự thống nhất giữa các bên liên quan.'
        ),
        llm=model_string,
        allow_delegation=False,  # Agent này không ủy quyền để đảm bảo chất lượng tài liệu
        verbose=True  # Giúp theo dõi quá trình suy nghĩ của agent
    )

    def create_project_document(title, content):
        output_path = os.path.join(output_base_dir, "0_initiation", f"{title.replace(' ', '_')}.docx")
        return create_docx(title, content, output_path)

    def create_analysis_table(data):
        output_path = os.path.join(output_base_dir, "0_initiation", "Analysis_Table.xlsx")
        return create_xlsx(data, output_path)

    initiation_agent.tools = [
        {
            "name": "create_project_document",
            "description": "Tạo các tài liệu dự án dựa trên dữ liệu đầu vào",
            "function": lambda title, content: create_project_document(title, content)
        },
        {
            "name": "create_analysis_table",
            "description": "Tạo bảng phân tích định lượng trong file Excel",
            "function": lambda data: create_analysis_table(data)
        }
    ]

    return initiation_agent
from crewai import Agent
import logging
import os
from utils.output_formats import create_docx

def create_design_agent(output_base_dir):
    """
    Tạo agent chuyên xử lý các tác vụ thiết kế hệ thống.
    """
    model_string = "gemini/gemini-1.5-flash-latest"  # Hoặc "gemini/gemini-pro"
    logging.info(f"Đang cấu hình Design Agent với LLM: {model_string}")

    design_agent = Agent(
        role='Chuyên gia thiết kế hệ thống',
        goal=(
            'Thiết kế các thành phần hệ thống chi tiết, bao gồm kiến trúc hệ thống, sơ đồ cơ sở dữ liệu, và giao diện người dùng, dựa trên tài liệu yêu cầu hệ thống. '
            'Đảm bảo rằng các thiết kế đáp ứng các yêu cầu chức năng và phi chức năng, đồng thời tuân thủ các tiêu chuẩn kỹ thuật và quy định ngành. '
            'Mục tiêu là tạo ra các tài liệu thiết kế rõ ràng, có thể triển khai, và được các bên liên quan phê duyệt.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia thiết kế hệ thống** với hơn 10 năm kinh nghiệm trong việc thiết kế các hệ thống CNTT phức tạp. '
            'Bạn có kỹ năng xuất sắc trong việc sử dụng các công cụ như UML, ERD, và các framework thiết kế để tạo ra các bản thiết kế chi tiết. '
            'Bạn đã làm việc trên nhiều dự án đa ngành, đảm bảo rằng các thiết kế không chỉ đáp ứng yêu cầu mà còn tối ưu hóa hiệu suất và khả năng mở rộng. '
            'Nhiệm vụ của bạn là tạo ra các tài liệu thiết kế có cấu trúc, dễ hiểu, và sẵn sàng cho giai đoạn phát triển.'
        ),
        llm=model_string,
        allow_delegation=False,  # Agent này không ủy quyền để đảm bảo tính chính xác của thiết kế
        verbose=True  # Giúp theo dõi quá trình suy nghĩ của agent
    )

    def create_design_document(title, content):
        output_path = os.path.join(output_base_dir, "3_design", f"{title.replace(' ', '_')}.docx")
        return create_docx(title, content, output_path)

    design_agent.tools = [
        {
            "name": "create_design_document",
            "description": "Tạo tài liệu thiết kế hệ thống dựa trên dữ liệu đầu vào",
            "function": lambda title, content: create_design_document(title, content)
        }
    ]

    return design_agent
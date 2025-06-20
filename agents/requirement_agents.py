from crewai import Agent
import logging
import os
from utils.output_formats import create_docx

def create_requirement_agent(output_base_dir):
    """
    Tạo agent chuyên thu thập và phân tích yêu cầu dự án.
    """
    model_string = "gemini/gemini-1.5-flash-latest"  # Hoặc "gemini/gemini-pro"
    logging.info(f"Đang cấu hình Requirement Agent với LLM: {model_string}")

    requirement_agent = Agent(
        role='Chuyên gia phân tích yêu cầu',
        goal=(
            'Thu thập, phân tích, và ghi nhận các yêu cầu chi tiết của dự án, bao gồm yêu cầu chức năng, phi chức năng, và các ràng buộc nghiệp vụ. '
            'Đảm bảo rằng các yêu cầu được xác định rõ ràng, có thể kiểm chứng, và được các bên liên quan phê duyệt. '
            'Mục tiêu là tạo ra tài liệu Yêu cầu hệ thống (System Requirements Specification) làm cơ sở cho các giai đoạn thiết kế và phát triển.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia phân tích yêu cầu** với hơn 12 năm kinh nghiệm trong việc làm việc với các bên liên quan để xác định các yêu cầu chính xác cho các hệ thống phức tạp. '
            'Bạn có kỹ năng vượt trội trong việc sử dụng các kỹ thuật như phân tích Use Case, User Stories, và mô hình hóa dữ liệu để đảm bảo rằng các yêu cầu được ghi nhận đầy đủ và rõ ràng. '
            'Bạn đã làm việc trên nhiều dự án đa ngành, sử dụng các tiêu chuẩn như IEEE hoặc BABOK để đảm bảo chất lượng tài liệu yêu cầu. '
            'Nhiệm vụ của bạn là tạo ra các tài liệu yêu cầu có cấu trúc, dễ hiểu, và đáp ứng các kỳ vọng của các bên liên quan.'
        ),
        llm=model_string,
        allow_delegation=False,  # Agent này không ủy quyền để đảm bảo tính chính xác của yêu cầu
        verbose=True  # Giúp theo dõi quá trình suy nghĩ của agent
    )

    def create_requirements_document(title, content):
        output_path = os.path.join(output_base_dir, "2_requirements", f"{title.replace(' ', '_')}.docx")
        return create_docx(title, content, output_path)

    requirement_agent.tools = [
        {
            "name": "create_requirements_document",
            "description": "Tạo tài liệu yêu cầu hệ thống dựa trên dữ liệu đầu vào",
            "function": lambda title, content: create_requirements_document(title, content)
        }
    ]

    return requirement_agent
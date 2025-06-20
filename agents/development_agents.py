from crewai import Agent
import logging
import os
from utils.output_formats import create_docx

def create_development_agent(output_base_dir):
    """
    Tạo agent chuyên xử lý các tác vụ phát triển hệ thống.
    """
    model_string = "gemini/gemini-1.5-flash-latest"  # Hoặc "gemini/gemini-pro"
    logging.info(f"Đang cấu hình Development Agent với LLM: {model_string}")

    development_agent = Agent(
        role='Chuyên gia phát triển hệ thống',
        goal=(
            'Phát triển các thành phần hệ thống dựa trên tài liệu thiết kế, bao gồm mã nguồn, tích hợp hệ thống, và các tài liệu hỗ trợ phát triển. '
            'Đảm bảo rằng mã nguồn đáp ứng các yêu cầu chức năng và phi chức năng, tuân thủ các tiêu chuẩn mã hóa, và được tối ưu hóa về hiệu suất. '
            'Mục tiêu là tạo ra một hệ thống hoạt động ổn định, có thể kiểm thử, và sẵn sàng cho giai đoạn kiểm thử.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia phát triển hệ thống** với hơn 12 năm kinh nghiệm trong việc viết mã và tích hợp các hệ thống phức tạp. '
            'Bạn có kỹ năng vượt trội trong việc sử dụng các ngôn ngữ lập trình hiện đại, các framework phát triển, và các công cụ CI/CD. '
            'Bạn đã làm việc trên nhiều dự án đa ngành, đảm bảo rằng mã nguồn không chỉ đáp ứng yêu cầu mà còn dễ bảo trì và mở rộng. '
            'Nhiệm vụ của bạn là tạo ra các tài liệu phát triển và mã nguồn có chất lượng cao, sẵn sàng cho kiểm thử.'
        ),
        llm=model_string,
        allow_delegation=False,  # Agent này không ủy quyền để đảm bảo chất lượng mã nguồn
        verbose=True  # Giúp theo dõi quá trình suy nghĩ của agent
    )

    def create_development_document(title, content):
        output_path = os.path.join(output_base_dir, "4_development", f"{title.replace(' ', '_')}.docx")
        return create_docx(title, content, output_path)

    development_agent.tools = [
        {
            "name": "create_development_document",
            "description": "Tạo tài liệu phát triển hệ thống dựa trên dữ liệu đầu vào",
            "function": lambda title, content: create_development_document(title, content)
        }
    ]

    return development_agent
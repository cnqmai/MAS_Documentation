from crewai import Agent
import logging

def create_development_agent():
    """
    Tạo agent chuyên xử lý các tác vụ phát triển hệ thống.
    """
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Đang cấu hình Development Agent với LLM: {model_string}")

    development_agent = Agent(
        role='Chuyên gia phát triển hệ thống',
        goal=(
            'Phát triển các thành phần hệ thống dựa trên tài liệu thiết kế, bao gồm mã nguồn, tích hợp hệ thống, và các tài liệu hỗ trợ phát triển. '
            'Đảm bảo rằng mã nguồn đáp ứng các yêu cầu chức năng và phi chức năng, tuân thủ các tiêu chuẩn mã hóa, và được tối ưu hóa về hiệu suất.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia phát triển hệ thống** với hơn 12 năm kinh nghiệm trong việc viết mã và tích hợp các hệ thống phức tạp. '
            'Bạn có kỹ năng vượt trội trong sử dụng các ngôn ngữ lập trình hiện đại, các framework phát triển, và các công cụ CI/CD.'
        ),
        llm=model_string,
        allow_delegation=False,
        verbose=True,
    )

    return development_agent

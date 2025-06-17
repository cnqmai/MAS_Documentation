# agents/design_agent.py

from crewai import Agent
import logging

def create_design_agent():
    """
    Tạo Agent cho Giai đoạn 3: Thiết kế Kỹ thuật (Design) trong SDLC.
    """

    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Khởi tạo Design Agent với LLM: {model_string}")

    design_agent = Agent(
        role='System Architect / Lead Software Engineer',
        goal=(
            'Chuyển đổi các yêu cầu trong tài liệu SRS thành một bản thiết kế kỹ thuật chi tiết và khả thi. '
            'Tạo ra các tài liệu thiết kế bao gồm kiến trúc hệ thống, sơ đồ cơ sở dữ liệu, đặc tả API, và thiết kế các thành phần.'
        ),
        backstory=(
            'Bạn là một Kiến trúc sư Hệ thống với hơn 15 năm kinh nghiệm xây dựng các hệ thống phần mềm phức tạp, có khả năng mở rộng và bảo trì cao. '
            'Bạn thành thạo các mẫu thiết kế (design patterns), kiến trúc microservices, thiết kế CSDL quan hệ và NoSQL, và các tiêu chuẩn API (REST, GraphQL). '
            'Nhiệm vụ của bạn là tạo ra một bản thiết kế vững chắc để đội ngũ phát triển có thể dựa vào đó để xây dựng sản phẩm một cách hiệu quả.'
        ),
        llm=model_string,
        allow_delegation=False, # Đã thay đổi thành False để nhất quán với development_agent và deployment_agent
        verbose=True
    )

    return design_agent # Trực tiếp trả về instance của tác nhân
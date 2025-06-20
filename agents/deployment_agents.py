from crewai import Agent
import logging

def create_deployment_agent():
    """
    Tạo agent chuyên xử lý các tác vụ triển khai hệ thống.
    """
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Đang cấu hình Deployment Agent với LLM: {model_string}")

    deployment_agent = Agent(
        role='Chuyên gia triển khai hệ thống',
        goal=(
            'Lập kế hoạch và thực hiện triển khai hệ thống, bao gồm việc cài đặt, cấu hình, và chuyển giao hệ thống cho môi trường sản xuất. '
            'Đảm bảo rằng quá trình triển khai diễn ra suôn sẻ, không gây gián đoạn, và đáp ứng các yêu cầu của các bên liên quan.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia triển khai hệ thống** với hơn 10 năm kinh nghiệm trong việc triển khai các hệ thống CNTT phức tạp. '
            'Bạn có kỹ năng xuất sắc trong sử dụng các công cụ DevOps, quản lý cơ sở hạ tầng, và phối hợp với các đội ngũ.'
        ),
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )

    return deployment_agent
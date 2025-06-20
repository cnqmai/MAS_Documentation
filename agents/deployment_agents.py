from crewai import Agent
import logging
import os
from utils.output_formats import create_docx

def create_deployment_agent(output_base_dir):
    """
    Tạo agent chuyên xử lý các tác vụ triển khai hệ thống.
    """
    model_string = "gemini/gemini-1.5-flash-latest"  # Hoặc "gemini/gemini-pro"
    logging.info(f"Đang cấu hình Deployment Agent với LLM: {model_string}")

    deployment_agent = Agent(
        role='Chuyên gia triển khai hệ thống',
        goal=(
            'Lập kế hoạch và thực hiện triển khai hệ thống, bao gồm việc cài đặt, cấu hình, và chuyển giao hệ thống cho môi trường sản xuất. '
            'Đảm bảo rằng quá trình triển khai diễn ra suôn sẻ, không gây gián đoạn, và đáp ứng các yêu cầu của các bên liên quan. '
            'Mục tiêu là tạo ra các tài liệu triển khai chi tiết và đảm bảo hệ thống hoạt động ổn định trong môi trường thực tế.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia triển khai hệ thống** với hơn 10 năm kinh nghiệm trong việc triển khai các hệ thống CNTT phức tạp. '
            'Bạn có kỹ năng xuất sắc trong việc sử dụng các công cụ DevOps, quản lý cơ sở hạ tầng, và phối hợp với các đội ngũ để đảm bảo triển khai thành công. '
            'Bạn đã làm việc trên nhiều dự án đa ngành, đảm bảo rằng các hệ thống được triển khai đúng thời hạn và đáp ứng các tiêu chuẩn chất lượng. '
            'Nhiệm vụ của bạn là tạo ra các tài liệu triển khai chi tiết và hỗ trợ quá trình chuyển giao hệ thống.'
        ),
        llm=model_string,
        allow_delegation=False,  # Agent này không ủy quyền để đảm bảo chất lượng triển khai
        verbose=True  # Giúp theo dõi quá trình suy nghĩ của agent
    )

    def create_deployment_plan_document(title, content):
        output_path = os.path.join(output_base_dir, "6_deployment", f"{title.replace(' ', '_')}.docx")
        return create_docx(title, content, output_path)

    deployment_agent.tools = [
        {
            "name": "create_deployment_plan_document",
            "description": "Tạo tài liệu kế hoạch triển khai dựa trên dữ liệu đầu vào",
            "function": lambda title, content: create_deployment_plan_document(title, content)
        }
    ]

    return deployment_agent
from crewai import Agent
import logging
import os
from utils.output_formats import create_docx

def create_maintenance_agent(output_base_dir):
    """
    Tạo agent chuyên xử lý các tác vụ bảo trì hệ thống.
    """
    model_string = "gemini/gemini-1.5-flash-latest"  # Hoặc "gemini/gemini-pro"
    logging.info(f"Đang cấu hình Maintenance Agent với LLM: {model_string}")

    maintenance_agent = Agent(
        role='Chuyên gia bảo trì hệ thống',
        goal=(
            'Lập kế hoạch và thực hiện các hoạt động bảo trì hệ thống, bao gồm giám sát hiệu suất, sửa lỗi, và nâng cấp hệ thống. '
            'Đảm bảo rằng hệ thống tiếp tục hoạt động ổn định, đáp ứng các yêu cầu của các bên liên quan, và thích ứng với các thay đổi trong môi trường vận hành. '
            'Mục tiêu là tạo ra các tài liệu bảo trì chi tiết và đảm bảo hệ thống duy trì chất lượng cao trong suốt vòng đời.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia bảo trì hệ thống** với hơn 10 năm kinh nghiệm trong việc quản lý và duy trì các hệ thống CNTT phức tạp. '
            'Bạn có kỹ năng xuất sắc trong việc giám sát hệ thống, xử lý sự cố, và triển khai các bản cập nhật để cải thiện hiệu suất. '
            'Bạn đã làm việc trên nhiều dự án đa ngành, đảm bảo rằng các hệ thống luôn hoạt động ổn định và đáp ứng các tiêu chuẩn chất lượng. '
            'Nhiệm vụ của bạn là tạo ra các tài liệu bảo trì chi tiết và hỗ trợ quá trình duy trì hệ thống.'
        ),
        llm=model_string,
        allow_delegation=False,  # Agent này không ủy quyền để đảm bảo chất lượng bảo trì
        verbose=True  # Giúp theo dõi quá trình suy nghĩ của agent
    )

    def create_maintenance_plan_document(title, content):
        output_path = os.path.join(output_base_dir, "7_maintenance", f"{title.replace(' ', '_')}.docx")
        return create_docx(title, content, output_path)

    maintenance_agent.tools = [
        {
            "name": "create_maintenance_plan_document",
            "description": "Tạo tài liệu kế hoạch bảo trì dựa trên dữ liệu đầu vào",
            "function": lambda title, content: create_maintenance_plan_document(title, content)
        }
    ]

    return maintenance_agent
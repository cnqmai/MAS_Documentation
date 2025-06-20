from crewai import Agent
import logging

def create_maintenance_agent():
    """
    Tạo agent chuyên xử lý các tác vụ bảo trì hệ thống.
    """
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Đang cấu hình Maintenance Agent với LLM: {model_string}")

    maintenance_agent = Agent(
        role='Chuyên gia bảo trì hệ thống',
        goal=(
            'Lập kế hoạch và thực hiện các hoạt động bảo trì hệ thống, bao gồm giám sát hiệu suất, sửa lỗi, và nâng cấp hệ thống. '
            'Đảm bảo rằng hệ thống tiếp tục hoạt động ổn định, đáp ứng các yêu cầu của các bên liên quan.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia bảo trì hệ thống** với hơn 10 năm kinh nghiệm trong việc quản lý và duy trì các hệ thống CNTT phức tạp. '
            'Bạn có kỹ năng xuất sắc trong giám sát hệ thống, xử lý sự cố, và triển khai các bản cập nhật.'
        ),
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )

    return maintenance_agent
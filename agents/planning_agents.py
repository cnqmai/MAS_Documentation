from crewai import Agent
import logging
import os
from utils.output_formats import create_docx

def create_planning_agent(output_base_dir):
    """
    Tạo agent chuyên xử lý các tác vụ lập kế hoạch dự án.
    """
    model_string = "gemini/gemini-1.5-flash-latest"  # Hoặc "gemini/gemini-pro"
    logging.info(f"Đang cấu hình Planning Agent với LLM: {model_string}")

    planning_agent = Agent(
        role='Chuyên gia lập kế hoạch dự án',
        goal=(
            'Phát triển các kế hoạch dự án chi tiết và toàn diện, bao gồm Kế hoạch quản lý dự án, Lịch trình dự án, và Kế hoạch quản lý rủi ro. '
            'Đảm bảo rằng các kế hoạch này dựa trên các tài liệu khởi tạo (như Project Charter, Business Case) và phản ánh chính xác các yêu cầu của các bên liên quan. '
            'Mục tiêu là cung cấp một lộ trình rõ ràng cho việc thực hiện dự án, tối ưu hóa tài nguyên và thời gian, đồng thời giảm thiểu rủi ro.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia lập kế hoạch dự án** với hơn 10 năm kinh nghiệm trong việc xây dựng các kế hoạch quản lý dự án phức tạp. '
            'Bạn có kỹ năng xuất sắc trong việc lập lịch trình, phân bổ tài nguyên, và dự đoán các rủi ro tiềm ẩn thông qua các công cụ như ma trận rủi ro và biểu đồ Gantt. '
            'Bạn đã làm việc với các dự án đa ngành, sử dụng các phương pháp như PMI, PRINCE2, và Agile để đảm bảo rằng các kế hoạch dự án đáp ứng các tiêu chuẩn chất lượng cao nhất. '
            'Nhiệm vụ của bạn là tạo ra các tài liệu lập kế hoạch có cấu trúc, dễ hiểu, và hỗ trợ các giai đoạn tiếp theo của dự án.'
        ),
        llm=model_string,
        allow_delegation=False,  # Agent này không ủy quyền để đảm bảo tính chính xác của kế hoạch
        verbose=True  # Giúp theo dõi quá trình suy nghĩ của agent
    )

    def create_project_plan_document(title, content):
        output_path = os.path.join(output_base_dir, "1_planning", f"{title.replace(' ', '_')}.docx")
        return create_docx(title, content, output_path)

    planning_agent.tools = [
        {
            "name": "create_project_plan_document",
            "description": "Tạo tài liệu kế hoạch dự án dựa trên dữ liệu đầu vào",
            "function": lambda title, content: create_project_plan_document(title, content)
        }
    ]

    return planning_agent
from crewai import Agent
import logging
import os
from utils.output_formats import create_docx

def create_testing_agent(output_base_dir):
    """
    Tạo agent chuyên xử lý các tác vụ kiểm thử hệ thống.
    """
    model_string = "gemini/gemini-1.5-flash-latest"  # Hoặc "gemini/gemini-pro"
    logging.info(f"Đang cấu hình Testing Agent với LLM: {model_string}")

    testing_agent = Agent(
        role='Chuyên gia kiểm thử hệ thống',
        goal=(
            'Thiết kế và thực hiện các kế hoạch kiểm thử hệ thống, bao gồm kiểm thử đơn vị, kiểm thử tích hợp, và kiểm thử chấp nhận người dùng. '
            'Đảm bảo rằng hệ thống đáp ứng tất cả các yêu cầu chức năng và phi chức năng được xác định trong tài liệu yêu cầu và thiết kế. '
            'Mục tiêu là tạo ra các báo cáo kiểm thử chi tiết, xác định lỗi, và đảm bảo hệ thống sẵn sàng cho triển khai.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia kiểm thử hệ thống** với hơn 10 năm kinh nghiệm trong việc thiết kế và thực hiện các kịch bản kiểm thử phức tạp. '
            'Bạn có kỹ năng xuất sắc trong việc sử dụng các công cụ kiểm thử tự động và thủ công, cũng như phân tích kết quả để xác định lỗi và cải tiến hệ thống. '
            'Bạn đã làm việc trên nhiều dự án đa ngành, đảm bảo rằng các hệ thống đạt chất lượng cao trước khi triển khai. '
            'Nhiệm vụ của bạn là tạo ra các tài liệu kiểm thử chi tiết và đảm bảo hệ thống đáp ứng các tiêu chuẩn chất lượng.'
        ),
        llm=model_string,
        allow_delegation=False,  # Agent này không ủy quyền để đảm bảo chất lượng kiểm thử
        verbose=True  # Giúp theo dõi quá trình suy nghĩ của agent
    )

    def create_test_plan_document(title, content):
        output_path = os.path.join(output_base_dir, "5_testing", f"{title.replace(' ', '_')}.docx")
        return create_docx(title, content, output_path)

    testing_agent.tools = [
        {
            "name": "create_test_plan_document",
            "description": "Tạo tài liệu kế hoạch kiểm thử dựa trên dữ liệu đầu vào",
            "function": lambda title, content: create_test_plan_document(title, content)
        }
    ]

    return testing_agent
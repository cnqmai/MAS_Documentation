from crewai import Agent
import logging

def create_testing_agent():
    """
    Tạo agent chuyên xử lý các tác vụ kiểm thử hệ thống.
    """
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Đang cấu hình Testing Agent với LLM: {model_string}")

    testing_agent = Agent(
        role='Chuyên gia kiểm thử hệ thống',
        goal=(
            'Thiết kế và thực hiện các kế hoạch kiểm thử hệ thống, bao gồm kiểm thử đơn vị, kiểm thử tích hợp, và kiểm thử chấp nhận người dùng. '
            'Đảm bảo rằng hệ thống đáp ứng tất cả các yêu cầu chức năng và phi chức năng được xác định trong tài liệu yêu cầu và thiết kế.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia kiểm thử hệ thống** với hơn 10 năm kinh nghiệm trong việc thiết kế và thực hiện các kịch bản kiểm thử phức tạp. '
            'Bạn có kỹ năng xuất sắc trong sử dụng các công cụ kiểm thử tự động và thủ công, cũng như phân tích kết quả để xác định lỗi.'
        ),
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )

    return testing_agent
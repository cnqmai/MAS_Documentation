# agents/input_agent.py

from crewai import Agent
import logging

def create_input_agent():
    """
    Tạo agent chuyên thu thập và xử lý yêu cầu đầu vào từ người dùng/stakeholder.
    """
    model_string = "gemini/gemini-1.5-flash-latest" # Hoặc "gemini/gemini-pro"
    logging.info(f"Configuring Input Agent with LLM: {model_string}")

    input_agent = Agent(
        role='User Requirement Collector',
        goal='Thu thập, phân tích và tóm tắt yêu cầu ban đầu của người dùng/stakeholder thành một tài liệu rõ ràng, có cấu trúc thông qua tương tác hỏi đáp.',
        backstory=(
            'Bạn là một chuyên gia phân tích nghiệp vụ với hơn 10 năm kinh nghiệm trong việc phỏng vấn '
            'stakeholder, thu thập các yêu cầu chức năng và phi chức năng, xác định các điểm khó khăn (pain points) '
            'và kỳ vọng của người dùng. Bạn có khả năng biến các ý tưởng mơ hồ thành các yêu cầu cụ thể, chi tiết '
            'và dễ hiểu cho đội ngũ phát triển. Bạn thực hiện điều này bằng cách đặt các câu hỏi rõ ràng, từng bước một, '
            'cho đến khi bạn có đủ thông tin để tóm tắt yêu cầu hệ thống.'
        ),
        llm=model_string,
        allow_delegation=False, # Quan trọng: Agent này không ủy quyền cho agent khác trong việc hỏi người dùng
        verbose=True # Giúp bạn theo dõi quá trình suy nghĩ của agent
    )
    return input_agent


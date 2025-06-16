# agents/requirement_agent.py

from crewai import Agent
import logging

def create_requirement_agent():
    """Tạo agent cho giai đoạn Requirements."""
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Configuring Requirement Agent with LLM: {model_string}")

    requirement_analyst_agent = Agent(
        role='Requirement Analyst',
        goal='Chuyển đổi các yêu cầu kinh doanh thành các tài liệu kỹ thuật chi tiết như BRD, SRS, Use Cases, RTM, SLA, NFR, và Kế hoạch đào tạo.',
        backstory='Bạn là một chuyên gia phân tích yêu cầu với hơn 10 năm kinh nghiệm, có khả năng diễn giải các nhu cầu phức tạp của người dùng và chuyển đổi chúng thành các đặc tả rõ ràng, đầy đủ cho đội ngũ phát triển.',
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )
    return requirement_analyst_agent
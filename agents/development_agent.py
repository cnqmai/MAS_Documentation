# agents/development_agent.py

from crewai import Agent
import logging

def create_development_agent():
    """Tạo agent cho giai đoạn Development."""
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Configuring Development Agent with LLM: {model_string}")

    lead_software_engineer_agent = Agent(
        role='Lead Software Engineer',
        goal='Thiết lập các tiêu chuẩn mã hóa, hướng dẫn phát triển, chiến lược kiểm soát mã nguồn, quy trình build/deploy, quy trình review code và kế hoạch tích hợp.',
        backstory='Bạn là một kỹ sư phần mềm cấp cao và là trưởng nhóm phát triển, có khả năng định hướng kỹ thuật và đảm bảo chất lượng mã hóa, cũng như tối ưu hóa quy trình phát triển.',
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )
    return lead_software_engineer_agent
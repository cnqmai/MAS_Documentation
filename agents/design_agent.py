# agents/design_agent.py

from crewai import Agent
import logging

def create_design_agent():
    """Tạo agent cho giai đoạn Design."""
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Configuring Design Agent with LLM: {model_string}")

    system_architect_agent = Agent(
        role='System Architect',
        goal='Thiết kế kiến trúc hệ thống cấp cao (HLD) và cấp thấp (LLD), bao gồm sơ đồ DFD, Sequence, thiết kế cơ sở dữ liệu, API, và kiến trúc bảo mật.',
        backstory='Bạn là một kiến trúc sư hệ thống giàu kinh nghiệm với hơn 15 năm trong việc tạo ra các giải pháp kỹ thuật mạnh mẽ, có khả năng mở rộng và bảo mật.',
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )
    return system_architect_agent
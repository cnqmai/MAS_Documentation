# agents/planning_agent.py

from crewai import Agent
import logging

def create_planning_agent():
    """Tạo agent cho giai đoạn Planning."""
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Configuring Planning Agent with LLM: {model_string}")

    planning_orchestrator_agent = Agent(
        role='Planning Orchestrator',
        goal='Phát triển kế hoạch dự án chi tiết, bao gồm WBS, ước tính chi phí (CapEx/OpEx), và kế hoạch mua sắm.',
        backstory='Bạn là một chuyên gia lập kế hoạch dự án với kinh nghiệm sâu rộng trong việc xây dựng các kế hoạch thực tế và quản lý nguồn lực hiệu quả.',
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )
    return planning_orchestrator_agent
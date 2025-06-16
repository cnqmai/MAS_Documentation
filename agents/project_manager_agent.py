# agents/project_manager_agent.py

from crewai import Agent
import logging

def create_project_manager_agent():
    """Tạo agent cho Project Manager chịu trách nhiệm cổng chất lượng."""
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Configuring Project Manager Agent with LLM: {model_string}")

    project_manager_agent = Agent(
        role='Project Manager / PMO Officer',
        goal='Đảm bảo chất lượng đầu ra của các giai đoạn dự án, kiểm tra và phê duyệt tất cả các tài liệu quan trọng thông qua các cổng chất lượng (quality gates).',
        backstory='Bạn là một Project Manager (PMP) kỳ cựu với hơn 15 năm kinh nghiệm, chuyên về quản lý chất lượng và quy trình dự án. Bạn có khả năng đánh giá chặt chẽ các deliverables để đảm bảo chúng đáp ứng các tiêu chuẩn và mục tiêu dự án.',
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )
    return project_manager_agent
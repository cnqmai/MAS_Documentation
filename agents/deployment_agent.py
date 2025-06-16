# agents/deployment_agent.py

from crewai import Agent
import logging

def create_deployment_agent():
    """Tạo agent cho giai đoạn Deployment."""
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Configuring Deployment Agent with LLM: {model_string}")

    devops_engineer_agent = Agent(
        role='DevOps Engineer',
        goal='Lập kế hoạch và thực hiện triển khai hệ thống, bao gồm các bước bàn giao sản xuất, kế hoạch khắc phục sự cố và thiết lập giám sát.',
        backstory='Bạn là một kỹ sư DevOps giàu kinh nghiệm, chuyên về tự động hóa triển khai, quản lý cấu hình và đảm bảo hoạt động liên tục của hệ thống.',
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )
    return devops_engineer_agent
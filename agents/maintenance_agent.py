# agents/maintenance_agent.py

from crewai import Agent
import logging

def create_maintenance_agent():
    """Tạo agent cho giai đoạn Maintenance."""
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Configuring Maintenance Agent with LLM: {model_string}")

    site_reliability_engineer_agent = Agent(
        role='Site Reliability Engineer',
        goal='Duy trì, nâng cấp, và hỗ trợ hệ thống sau triển khai, bao gồm quản lý bản vá, thực thi SLA, và xem xét sau dự án.',
        backstory='Bạn là một kỹ sư SRE tận tâm, chuyên về vận hành ổn định, tối ưu hóa hiệu suất và phản ứng sự cố, đảm bảo dịch vụ luôn sẵn sàng và tin cậy.',
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )
    return site_reliability_engineer_agent
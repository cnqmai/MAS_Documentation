# agents/testing_agent.py

from crewai import Agent
import logging

def create_testing_agent():
    """Tạo agent cho giai đoạn Testing."""
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Configuring Testing Agent with LLM: {model_string}")

    qa_automation_engineer_agent = Agent(
        role='QA Automation Engineer',
        goal='Xây dựng kế hoạch kiểm thử, danh sách kiểm tra QA, các trường hợp/kịch bản kiểm thử, báo cáo lỗi, kế hoạch UAT, báo cáo kiểm thử bảo mật/hiệu năng và báo cáo quản lý kiểm thử.',
        backstory='Bạn là một kỹ sư QA chuyên nghiệp với kinh nghiệm sâu rộng trong kiểm thử tự động, kiểm thử hiệu năng và bảo mật, đảm bảo sản phẩm đạt chất lượng cao nhất trước khi triển khai.',
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )
    return qa_automation_engineer_agent
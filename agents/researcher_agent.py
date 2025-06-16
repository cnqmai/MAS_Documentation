# agents/researcher_agent.py

from crewai import Agent
import logging

def create_researcher_agent():
    """Tạo agent làm trợ lý kiến thức (knowledge assistant) cho tất cả các phase."""
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Configuring Researcher Agent with LLM: {model_string}")

    researcher_agent = Agent(
        role='Knowledge Assistant',
        goal='Cung cấp các tài liệu tham khảo, mẫu, các phương pháp hay nhất (best practices), tiêu chuẩn (ví dụ: IEEE, UML), và kiến trúc mẫu liên quan đến các nhiệm vụ của dự án.',
        backstory='Bạn là một chuyên gia nghiên cứu và tổng hợp thông tin, có khả năng tìm kiếm và cung cấp kiến thức chuyên sâu từ nhiều nguồn khác nhau để hỗ trợ các agent khác trong dự án.',
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )
    return researcher_agent
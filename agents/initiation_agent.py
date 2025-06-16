# agents/initiation_agent.py

from crewai import Agent
import logging

def create_initiation_agent():
    """Tạo các agent cho giai đoạn Initiation."""
    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Configuring Initiation Agents with LLM: {model_string}")

    vision_agent = Agent(
        role='Project Visionary / System Analyst',
        goal='Định hình và viết tài liệu Tầm nhìn (Vision Document) rõ ràng, truyền cảm hứng cho dự án dựa trên yêu cầu ban đầu.',
        backstory='Bạn là một nhà phân tích hệ thống và chiến lược gia có 15 năm kinh nghiệm, có khả năng nhìn xa trông rộng và diễn đạt tầm nhìn một cách thuyết phục.',
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )

    conops_agent = Agent(
        role='Concept of Operations (ConOps) Specialist',
        goal='Phát triển tài liệu Khái niệm Vận hành (ConOps) chi tiết, mô tả cách hệ thống sẽ được sử dụng trong thực tế dựa trên yêu cầu ban đầu.',
        backstory='Bạn là một nhà phân tích nghiệp vụ tỉ mỉ với hơn 12 năm kinh nghiệm, giỏi trong việc mô hình hóa quy trình và tương tác người dùng.',
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )

    charter_agent = Agent(
         role='Project Charter Creator / PMO Officer',
         goal='Tạo ra bản Hiến chương Dự án (Project Charter) chính thức, xác định rõ mục tiêu, phạm vi, các bên liên quan và quyền hạn dựa trên yêu cầu ban đầu và các tài liệu vision/conops.',
         backstory='Bạn là một Quản lý Dự án (PMP) hoặc Nhân viên Văn phòng Quản lý Dự án (PMO) với hơn 12 năm kinh nghiệm, chuyên nghiệp trong việc thiết lập nền tảng cho các dự án.',
         llm=model_string,
         allow_delegation=False,
         verbose=True
    )
    return vision_agent, conops_agent, charter_agent
# agents/development_agent.py

from crewai import Agent
import logging

def create_development_agent():
    """Tạo Agent cho Giai đoạn 4: PHÁT TRIỂN trong SDLC."""

    model_string = "gemini/gemini-1.5-flash-latest"
    logging.info(f"Khởi tạo Development Agent với LLM: {model_string}")

    development_agent = Agent(
        role="Lead Software Engineer",
        goal=(
            "Dẫn dắt quá trình phát triển phần mềm bằng cách thiết lập và tuân thủ các tiêu chuẩn lập trình, "
            "quản lý kho mã nguồn, xây dựng và triển khai phần mềm tự động, tích hợp liên tục và đánh giá mã nguồn. "
            "Đảm bảo tất cả tài liệu và biểu mẫu phát triển được xây dựng đầy đủ, chính xác và có liên kết chặt chẽ với các đầu vào kỹ thuật."
        ),
        backstory=(
            "Bạn là một kỹ sư phần mềm cấp cao với kinh nghiệm dẫn dắt nhiều đội phát triển phần mềm trong môi trường Agile và DevOps. "
            "Bạn hiểu sâu sắc về vòng đời phát triển phần mềm, kiểm soát mã nguồn, kiểm thử đơn vị, xây dựng CI/CD pipeline, và viết tài liệu kỹ thuật rõ ràng. "
            "Bạn đảm nhiệm việc đảm bảo chất lượng, hiệu quả và sự phối hợp giữa các bên liên quan trong giai đoạn phát triển."
        ),
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )

    return development_agent
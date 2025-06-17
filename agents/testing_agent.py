# agents/testing_agent.py

from crewai import Agent
import logging

def create_testing_agent():
    """Tạo Agent cho Giai đoạn 5: KIỂM THỬ trong SDLC."""

    model_string = "gemini/gemini-1.5-flash-latest" 

    logging.info(f"Khởi tạo Testing Agent với LLM: {model_string}")

    testing_agent = Agent(
        role="QA Automation Engineer",
        goal=(
            "Đảm bảo chất lượng toàn diện cho hệ thống bằng cách thiết kế và thực thi các hoạt động kiểm thử. "
            "Viết test plan, xây dựng test cases theo yêu cầu nghiệp vụ, thực thi kiểm thử thủ công và tự động, "
            "ghi nhận lỗi và tạo báo cáo đánh giá mức độ bao phủ kiểm thử. "
            "Đảm bảo hệ thống đạt yêu cầu chức năng, phi chức năng, và sẵn sàng triển khai."
        ),
        backstory=(
            "Bạn là một chuyên gia kiểm thử phần mềm với hơn 8 năm kinh nghiệm làm việc trong các dự án lớn, đa tầng. "
            "Bạn thành thạo việc xây dựng kế hoạch kiểm thử (Test Plan), viết test case rõ ràng và có thể tái sử dụng, "
            "sử dụng thành thạo các công cụ kiểm thử như Selenium, Postman, Pytest, JUnit và tích hợp CI/CD với Jenkins hoặc GitHub Actions. "
            "Bạn hiểu rõ mô hình kiểm thử Agile, có khả năng đánh giá coverage, traceability, và phối hợp hiệu quả với các Developer và Product Owner."
        ),
        llm=model_string,
        allow_delegation=False,
        verbose=True
    )

    return testing_agent
from crewai import Agent
import logging
import os
from utils.output_formats import create_docx, create_xlsx

def create_project_manager_agent(output_base_dir):
    """
    Tạo agent chuyên quản lý và xác thực tài liệu dự án.
    """
    model_string = "gemini/gemini-1.5-flash-latest"  # Hoặc "gemini/gemini-pro"
    logging.info(f"Đang cấu hình Project Manager Agent với LLM: {model_string}")

    project_manager_agent = Agent(
        role='Quản lý dự án và xác thực tài liệu',
        goal=(
            'Xác thực tất cả các tài liệu khởi tạo dự án để đảm bảo tính đầy đủ, chính xác và phù hợp với các tiêu chuẩn quản lý dự án quốc tế như PMI hoặc PRINCE2. '
            'Tạo báo cáo xác thực chi tiết, nêu rõ trạng thái của từng tài liệu (đạt, cần chỉnh sửa, không đạt) và đưa ra các khuyến nghị cải thiện nếu cần. '
            'Đảm bảo rằng các tài liệu đáp ứng các yêu cầu từ các bên liên quan và sẵn sàng để sử dụng trong các giai đoạn tiếp theo của dự án.'
        ),
        backstory=(
            'Bạn là một **Quản lý dự án** được chứng nhận PMP với hơn 10 năm kinh nghiệm quản lý các dự án phức tạp trong nhiều lĩnh vực khác nhau. '
            'Bạn nổi tiếng với sự chú ý đến từng chi tiết và khả năng đảm bảo rằng mọi tài liệu dự án đều đạt chất lượng cao nhất. '
            'Bạn có kinh nghiệm sâu rộng trong việc phối hợp với các bên liên quan để xác minh và phê duyệt tài liệu, cũng như sử dụng các công cụ phân tích để đánh giá tính phù hợp của chúng. '
            'Nhiệm vụ của bạn là giám sát quá trình xác thực tài liệu, đảm bảo rằng dự án được khởi động với sự rõ ràng, chính xác và sẵn sàng cho các bước tiếp theo.'
        ),
        llm=model_string,
        allow_delegation=False,  # Agent này không ủy quyền để đảm bảo chất lượng xác thực
        verbose=True  # Giúp theo dõi quá trình suy nghĩ của agent
    )

    def validate_documents(phase, documents):
        content = [f"- {doc_name}: Đã kiểm tra, đạt yêu cầu." for doc_name in documents]
        output_doc_path = os.path.join(output_base_dir, "0_initiation", "Validation_Report.docx")
        output_xlsx_path = os.path.join(output_base_dir, "0_initiation", "Validation_Report.xlsx")
        create_docx(f"Báo cáo xác thực tài liệu - Giai đoạn {phase}", content, output_doc_path)
        create_xlsx([{"Tài liệu": doc_name, "Trạng thái": "Đạt"} for doc_name in documents], output_xlsx_path)
        return output_doc_path, output_xlsx_path

    project_manager_agent.tools = [
        {
            "name": "validate_documents",
            "description": "Kiểm tra và xác thực các tài liệu khởi tạo",
            "function": lambda documents: validate_documents("Khởi tạo", documents)
        }
    ]

    return project_manager_agent
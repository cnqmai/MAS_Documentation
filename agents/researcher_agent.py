from crewai import Agent
import logging
import os
from utils.output_formats import create_docx

def create_researcher_agent(output_base_dir):
    """
    Tạo agent chuyên nghiên cứu và tư vấn cho giai đoạn khởi tạo dự án.
    """
    model_string = "gemini/gemini-1.5-flash-latest"  # Hoặc "gemini/gemini-pro"
    logging.info(f"Đang cấu hình Researcher Agent với LLM: {model_string}")

    researcher_agent = Agent(
        role='Chuyên gia nghiên cứu và tư vấn dự án',
        goal=(
            'Đề xuất các phương pháp tốt nhất và thực tiễn hàng đầu để hỗ trợ giai đoạn khởi tạo dự án. '
            'Cung cấp các khuyến nghị dựa trên nghiên cứu chuyên sâu nhằm đảm bảo dự án được bắt đầu với một nền tảng vững chắc, '
            'bao gồm các chiến lược quản lý rủi ro, phương pháp thu thập yêu cầu hiệu quả, và cách tiếp cận lập kế hoạch sơ bộ. '
            'Mục tiêu là tối ưu hóa quy trình khởi tạo, giảm thiểu các rủi ro tiềm ẩn, và tăng khả năng thành công của dự án thông qua việc áp dụng các thực tiễn đã được chứng minh.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia nghiên cứu và tư vấn dự án** với hơn 15 năm kinh nghiệm trong lĩnh vực quản lý dự án và tư vấn khởi tạo. '
            'Bạn đã hỗ trợ hàng trăm dự án thuộc nhiều ngành khác nhau đạt được thành công nhờ vào khả năng nghiên cứu sâu rộng và áp dụng các phương pháp thực tiễn tốt nhất. '
            'Bạn nổi tiếng với việc dự đoán các thách thức tiềm ẩn và đề xuất các giải pháp sáng tạo để đảm bảo dự án đi đúng hướng ngay từ giai đoạn đầu. '
            'Nhiệm vụ của bạn là cung cấp các tài liệu hướng dẫn chi tiết, chẳng hạn như danh sách các phương pháp tốt nhất, để hỗ trợ đội ngũ dự án trong giai đoạn khởi tạo.'
        ),
        llm=model_string,
        allow_delegation=False,  # Agent này không ủy quyền để đảm bảo tính chính xác của nghiên cứu
        verbose=True  # Giúp theo dõi quá trình suy nghĩ của agent
    )

    def generate_best_practices(phase):
        content = [
            "1. Thu thập yêu cầu rõ ràng từ tất cả các bên liên quan thông qua các buổi phỏng vấn, workshop, và khảo sát.",
            "2. Đảm bảo Bản điều lệ dự án được phê duyệt bởi tất cả các bên liên quan trước khi tiến hành các bước tiếp theo.",
            "3. Sử dụng ma trận rủi ro để xác định và quản lý các rủi ro tiềm ẩn ngay từ giai đoạn khởi tạo.",
            "4. Thiết lập một quy trình giao tiếp rõ ràng để đảm bảo thông tin được truyền đạt hiệu quả."
        ]
        output_path = os.path.join(output_base_dir, "0_initiation", f"Best_Practices_{phase}.docx")
        return create_docx(f"Phương pháp tốt nhất cho giai đoạn {phase}", content, output_path)

    researcher_agent.tools = [
        {
            "name": "generate_best_practices",
            "description": "Tạo tài liệu phương pháp tốt nhất cho giai đoạn khởi tạo",
            "function": lambda: generate_best_practices("Khởi tạo")
        }
    ]

    return researcher_agent
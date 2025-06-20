from crewai import Agent
import logging
import os
from utils.output_formats import create_docx

def create_input_agent(input_base_dir):
    """
    Tạo agent chuyên thu thập và xử lý yêu cầu đầu vào từ người dùng/stakeholder.
    """
    model_string = "gemini/gemini-1.5-flash-latest"  # Hoặc "gemini/gemini-pro"
    logging.info(f"Đang cấu hình Input Agent với LLM: {model_string}")

    input_agent = Agent(
        role='Chuyên gia khơi gợi và điều phối yêu cầu',
        goal=(
            'Thấu hiểu sâu sắc và thu thập toàn bộ các yêu cầu ban đầu từ người dùng và các bên liên quan (stakeholders) thông qua quy trình tương tác hỏi đáp. '
            'Mục tiêu là chắt lọc các ý tưởng, nhu cầu và vấn đề chưa rõ ràng thành một tập hợp các yêu cầu đầu vào rõ ràng, có cấu trúc và nhất quán. '
            'Đảm bảo rằng mọi khía cạnh quan trọng của hệ thống đều được ghi nhận, bao gồm cả các yêu cầu chức năng, phi chức năng và các ràng buộc nghiệp vụ.'
        ),
        backstory=(
            'Bạn là một **Chuyên gia khơi gợi và điều phối yêu cầu (Requirements Elicitor & Facilitator)** có kinh nghiệm dày dặn, với hơn 12 năm chuyên môn trong lĩnh vực phân tích nghiệp vụ. '
            'Bạn có khả năng vượt trội trong việc dẫn dắt các cuộc phỏng vấn, tổ chức các buổi workshop, và sử dụng các kỹ thuật phân tích yêu cầu tiên tiến để khám phá những nhu cầu ẩn giấu. '
            'Bạn không chỉ giỏi lắng nghe mà còn biết cách đặt các câu hỏi chiến lược, gợi mở để đào sâu thông tin, xác định các điểm đau (painánpoints), các trường hợp ngoại lệ, và kỳ vọng thực sự của người dùng. '
            'Nhiệm vụ của bạn là xây dựng một nền tảng yêu cầu vững chắc, biến những mong muốn ban đầu thành một bản tóm tắt đầu vào (Input Summary) chuẩn xác, làm cơ sở cho các giai đoạn phát triển tiếp theo.'
        ),
        llm=model_string,
        allow_delegation=False,  # Quan trọng: Agent này không ủy quyền cho agent khác trong việc hỏi người dùng
        verbose=True  # Giúp bạn theo dõi quá trình suy nghĩ của agent
    )

    def generate_dynamic_questions(context):
        questions = []
        context = context.lower()
        if "mục tiêu dự án" in context:
            questions.append("Phạm vi cụ thể của dự án là gì?")
            questions.append("Ngân sách dự kiến cho dự án là bao nhiêu?")
        elif "ngân sách" in context:
            questions.append("Nguồn tài trợ cho dự án đến từ đâu?")
            questions.append("Có yêu cầu cụ thể nào về chi phí không?")
        elif "yêu cầu kinh doanh" in context:
            questions.append("Yêu cầu chức năng cụ thể là gì?")
            questions.append("Có yêu cầu phi chức năng nào cần xem xét không?")
        else:
            questions.append("Mục tiêu chính của dự án là gì?")
        return questions

    def save_interaction_log(questions, answers):
        output_path = os.path.join(input_base_dir, "system_request_summary.docx")
        content = [f"Câu hỏi: {q}\nCâu trả lời: {a}" for q, a in zip(questions, answers)]
        return create_docx("Tóm tắt yêu cầu hệ thống", content, output_path)

    input_agent.tools = [
        {
            "name": "generate_dynamic_questions",
            "description": "Tạo câu hỏi dựa trên câu trả lời trước đó",
            "function": generate_dynamic_questions
        },
        {
            "name": "save_interaction_log",
            "description": "Lưu lịch sử câu hỏi và câu trả lời vào file docx",
            "function": save_interaction_log
        }
    ]

    return input_agent
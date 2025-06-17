import logging
from crewai import Task, Crew, Process
from memory.shared_memory import shared_memory
from utils.file_writer import write_output
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_initial_requirement_collection_task(input_agent, existing_context: str):
    """
    Tạo một task để agent thu thập yêu cầu ban đầu từ người dùng thông qua các câu hỏi.
    Args:
        input_agent (Agent): Agent thu thập yêu cầu.
        existing_context (str): Ngữ cảnh hiện tại của cuộc hội thoại, bao gồm các câu hỏi và trả lời trước đó.
    Returns:
        Task: Một đối tượng CrewAI Task.
    """
    return Task(
        description=(
            f"Bạn là một chuyên gia thu thập yêu cầu. Nhiệm vụ của bạn là đặt các câu hỏi rõ ràng, "
            f"cụ thể cho người dùng để làm rõ các yêu cầu ban đầu cho một hệ thống phần mềm. "
            f"Dựa trên ngữ cảnh hội thoại đã có (bao gồm các câu hỏi của bạn và trả lời của người dùng), "
            f"hãy xác định câu hỏi tiếp theo cần hỏi để đào sâu hoặc làm rõ thêm thông tin.\n\n"
            f"**CÁC QUY TẮC QUAN TRỌNG:**\n"
            f"1. **Chỉ hỏi MỘT câu hỏi mỗi lần.** Đừng tóm tắt hoặc nói thêm gì khác ngoài câu hỏi.\n"
            f"2. Nếu bạn đã có đủ thông tin (tối thiểu là các mục tiêu chính, các tính năng mong muốn, và vấn đề cần giải quyết), "
            f"   hãy kết thúc bằng cách bắt đầu output của bạn với từ khóa 'KẾT THÚC_TÓM TẮT:' "
            f"   theo sau là bản tóm tắt chi tiết yêu cầu hệ thống.\n"
            f"3. Cố gắng hỏi các câu hỏi mở để khuyến khích người dùng cung cấp thêm thông tin.\n"
            f"4. Đặt câu hỏi về Mục tiêu dự án, Phạm vi (tính năng chính/phụ), Người dùng mục tiêu, Vấn đề hiện tại cần giải quyết, "
            f"   Các tính năng mong muốn, Công nghệ ưa thích (nếu có), Ràng buộc (ngân sách/thời gian).\n"
            f"5. **MỚI:** Nếu người dùng trả lời không rõ ràng, quá ngắn gọn (ví dụ: 'Không có', '') hoặc không cung cấp đủ thông tin cho câu hỏi hiện tại, "
            f"   hãy thử đặt lại câu hỏi theo một cách khác, đặt một câu hỏi mở rộng hơn, hoặc chuyển sang một khía cạnh khác của yêu cầu để tiếp tục thu thập thông tin.\n\n"
            f"--- Ngữ cảnh hội thoại hiện tại ---\n"
            f"{existing_context}\n\n"
            f"Câu hỏi tiếp theo hoặc Bản tóm tắt cuối cùng của bạn:"
        ),
        expected_output="Một câu hỏi duy nhất dành cho người dùng, hoặc một bản tóm tắt yêu cầu hệ thống bắt đầu bằng 'KẾT THÚT_TÓM TẮT:'.",
        agent=input_agent,
        verbose=False
    )

# Đã thay đổi 'output_base_dir' thành 'summary_output_dir' và cập nhật cách sử dụng.
def run_input_collection_conversation(input_agent, summary_output_dir: str):
    """
    Thực hiện một cuộc hội thoại tương tác với người dùng để thu thập yêu cầu.
    Args:
        input_agent (Agent): Agent chuyên thu thập yêu cầu.
        summary_output_dir (str): Thư mục để lưu trữ output của bản tóm tắt yêu cầu và lịch sử hội thoại.
                                  Thư mục này sẽ nằm cùng cấp với thư mục 'outputs'.
    """
    logging.info("--- Bắt đầu thu thập yêu cầu hệ thống từ người dùng (tương tác) ---")

    initial_system_prompt = "Chào mừng bạn! Tôi là trợ lý thu thập yêu cầu. Hãy cho tôi biết ý tưởng ban đầu của bạn về hệ thống phần mềm mà bạn muốn xây dựng. Bạn muốn giải quyết vấn đề gì, hoặc đạt được mục tiêu gì?"

    print(f"\nAGENT HỎI: {initial_system_prompt}")
    print(" (Gợi ý: Nếu bạn muốn kết thúc và yêu cầu tóm tắt, hãy gõ 'TÓM TẮT' và nhấn Enter.)") # Gợi ý cho người dùng
    first_user_response = input("BẠN TRẢ LỜI: ")

    conversation_history = [
        f"\nAGENT HỎI: {initial_system_prompt}\n",
        f"BẠN TRẢ LỜI: {first_user_response}\n"
    ]
    current_context = f"Người dùng đã trả lời: {first_user_response}"
    
    # === ĐÃ THAY ĐỔI DÒNG NÀY ===
    # Sử dụng trực tiếp summary_output_dir vì main.py đã cung cấp đường dẫn đầy đủ (ví dụ: "./input")
    phase_output_dir = summary_output_dir 
    # ============================
    os.makedirs(phase_output_dir, exist_ok=True)

    user_requested_summary = False # Biến cờ để kiểm soát việc người dùng yêu cầu tóm tắt

    while True:
        task_context = "".join(conversation_history) + f"AGENT: {current_context}"
        
        # Nếu người dùng yêu cầu tóm tắt, hãy thêm chỉ dẫn này vào ngữ cảnh của agent
        if user_requested_summary:
            task_context += "\n\nQUAN TRỌNG: Người dùng đã yêu cầu bạn tóm tắt lại tất cả các yêu cầu đã thu thập được cho đến thời điểm này. BẮT ĐẦU output của bạn với 'KẾT THÚC_TÓM TẮT:' và trình bày bản tóm tắt chi tiết yêu cầu hệ thống."
            user_requested_summary = False # Đặt lại cờ

        task = create_initial_requirement_collection_task(input_agent, task_context)
        
        temp_crew = Crew(
            agents=[input_agent],
            tasks=[task],
            process=Process.sequential,
            verbose=False
        )
        
        try:
            result = temp_crew.kickoff()
            agent_output = str(result).strip()

            if agent_output.startswith("KẾT THÚC_TÓM TẮT:"):
                final_summary = agent_output.replace("KẾT THÚC_TÓM TẮT:", "").strip()
                logging.info("Agent đã hoàn thành thu thập yêu cầu và tạo bản tóm tắt.")
                
                print("\n" + "="*80)
                print("           BẢN TÓM TẮT YÊU CẦU HỆ THỐNG (SYSTEM REQUEST SUMMARY)           ")
                print("="*80)
                print(final_summary)
                print("="*80 + "\n")
                
                shared_memory.set("phase_0_initiation", "system_request_summary", final_summary)
                
                summary_file_path = os.path.join(phase_output_dir, "System_Request_Summary.md")
                write_output(summary_file_path, final_summary)
                logging.info(f"Đã lưu bản tóm tắt yêu cầu hệ thống vào {summary_file_path}.")

                conversation_log_path = os.path.join(phase_output_dir, "initial_requirements_conversation.md")
                with open(conversation_log_path, "w", encoding="utf-8") as f:
                    f.write("# Lịch sử hội thoại thu thập yêu cầu ban đầu\n\n")
                    f.write("".join(conversation_history))
                    f.write(f"\n\n## Bản tóm tắt yêu cầu cuối cùng:\n{final_summary}\n")
                logging.info(f"Đã lưu lịch sử hội thoại vào {conversation_log_path}.")
                break

            else:
                # Agent đang đặt câu hỏi
                print(f"\nAGENT HỎI: {agent_output}")
                # Gợi ý cho người dùng nếu chưa có
                if not conversation_history or ("TÓM TẮT" not in conversation_history[-1]): # Sửa lỗi chính tả "TÓM CẮT" thành "TÓM TẮT" nếu cần
                    print(" (Gợi ý: Nếu bạn muốn kết thúc và yêu cầu tóm tắt, hãy gõ 'TÓM TẮT' và nhấn Enter.)")

                conversation_history.append(f"\nAGENT HỎI: {agent_output}\n")
                
                user_response = input("BẠN TRẢ LỜI: ")
                
                # Kiểm tra nếu người dùng muốn tóm tắt
                if user_response.strip().upper() == "TÓM TẮT":
                    user_requested_summary = True
                    current_context = "Người dùng đã yêu cầu tóm tắt các yêu cầu đã thu thập được."
                    conversation_history.append(f"BẠN TRẢ LỜI: TÓM TẮT\n")
                    continue # Bắt đầu vòng lặp mới để agent tạo tóm tắt

                conversation_history.append(f"BẠN TRẢ LỜI: {user_response}\n")
                current_context = f"Người dùng đã trả lời: {user_response}"

        except Exception as e:
            logging.error(f"❌ Lỗi trong quá trình tương tác thu thập yêu cầu: {e}", exc_info=True)
            print("Đã xảy ra lỗi trong quá trình thu thập yêu cầu. Vui lòng kiểm tra log để biết chi tiết.")
            break

    logging.info("--- Kết thúc quy trình thu thập yêu cầu ---")
import logging
import os
from crewai import Task, Crew, Process
from memory.shared_memory import SharedMemory
from utils.output_formats import create_md

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_initial_requirement_collection_task(input_agent, existing_context: str):
    return Task(
        description=(
            f"Bạn là một chuyên gia thu thập yêu cầu. Nhiệm vụ của bạn là đặt các câu hỏi rõ ràng, cụ thể "
            f"cho người dùng để làm rõ các yêu cầu ban đầu cho một hệ thống phần mềm.\n\n"
            f"**QUY TẮC:**\n"
            f"1. Chỉ hỏi MỘT câu mỗi lần.\n"
            f"2. Nếu đã đủ thông tin, bắt đầu output bằng 'KẾT THÚC_TÓM TẮT:' và viết bản tóm tắt.\n"
            f"3. Hỏi các khía cạnh như: mục tiêu, tính năng, người dùng, ràng buộc kỹ thuật, công nghệ ưa thích, v.v.\n"
            f"--- Ngữ cảnh hội thoại ---\n"
            f"{existing_context}\n\n"
            f"Câu hỏi tiếp theo hoặc Bản tóm tắt:"
        ),
        expected_output="Một câu hỏi duy nhất hoặc bản tóm tắt bắt đầu bằng 'KẾT THÚC_TÓM TẮT:'.",
        agent=input_agent,
        verbose=False
    )

def run_input_collection_conversation(input_agent, summary_output_dir: str, shared_memory: SharedMemory):
    logging.info("--- Bắt đầu thu thập yêu cầu hệ thống từ người dùng (tương tác) ---")

    os.makedirs(summary_output_dir, exist_ok=True)

    initial_prompt = "Chào mừng bạn! Bạn hãy mô tả ý tưởng hoặc mục tiêu chính của hệ thống phần mềm bạn muốn xây dựng."
    print(f"\nAGENT HỎI: {initial_prompt}")
    print(" (Gợi ý: Nếu bạn muốn kết thúc và yêu cầu tóm tắt, hãy gõ 'TÓM TẮT' và nhấn Enter.)")
    user_input = input("BẠN TRẢ LỜI: ")

    conversation_history = [
        f"\nAGENT HỎI: {initial_prompt}\n",
        f"BẠN TRẢ LỜI: {user_input}\n"
    ]
    current_context = f"Người dùng đã trả lời: {user_input}"
    user_requested_summary = False

    while True:
        task_context = "".join(conversation_history) + f"AGENT: {current_context}"
        if user_requested_summary:
            task_context += "\n\nNgười dùng đã yêu cầu tóm tắt. Bắt đầu câu trả lời bằng 'KẾT THÚC_TÓM TẮT:' và tóm tắt toàn bộ yêu cầu đã thu thập."

        task = create_initial_requirement_collection_task(input_agent, task_context)
        crew = Crew(agents=[input_agent], tasks=[task], process=Process.sequential, verbose=False)

        try:
            result = crew.kickoff()
            agent_output = str(result).strip()

            if agent_output.startswith("KẾT THÚC_TÓM TẮT:"):
                final_summary = agent_output.replace("KẾT THÚC_TÓM TẮT:", "").strip()

                print("\n" + "="*80)
                print("        BẢN TÓM TẮT YÊU CẦU HỆ THỐNG (SYSTEM REQUEST SUMMARY)        ")
                print("="*80)
                print(final_summary)
                print("="*80 + "\n")

                # ✅ Lưu vào bộ nhớ
                shared_memory.save("system_request_summary", final_summary)

                # ✅ Lưu file Markdown
                summary_path = os.path.join(summary_output_dir, "System_Request_Summary.md")
                create_md(final_summary, summary_path)

                history_md = "# Lịch sử hội thoại thu thập yêu cầu ban đầu\n\n" + \
                             "".join(conversation_history) + \
                             f"\n\n## Bản tóm tắt cuối cùng:\n{final_summary}\n"
                history_path = os.path.join(summary_output_dir, "Conversation_History.md")
                create_md(history_md, history_path)

                logging.info(f"✅ Đã lưu {summary_path} và {history_path}")
                break

            else:
                print(f"\nAGENT HỎI: {agent_output}")
                print(" (Gợi ý: Gõ 'TÓM TẮT' nếu bạn muốn kết thúc và tạo bản tóm tắt.)")

                conversation_history.append(f"\nAGENT HỎI: {agent_output}\n")
                user_response = input("BẠN TRẢ LỜI: ")

                if user_response.strip().upper() == "TÓM TẮT":
                    user_requested_summary = True
                    current_context = "Người dùng đã yêu cầu tóm tắt các yêu cầu đã thu thập."
                    conversation_history.append("BẠN TRẢ LỜI: TÓM TẮT\n")
                    continue

                conversation_history.append(f"BẠN TRẢ LỜI: {user_response}\n")
                current_context = f"Người dùng đã trả lời: {user_response}"

        except Exception as e:
            logging.error(f"❌ Lỗi khi thu thập yêu cầu: {e}", exc_info=True)
            print("⚠️ Đã xảy ra lỗi trong quá trình thu thập yêu cầu.")
            break

    logging.info("--- Kết thúc quá trình thu thập yêu cầu ---")

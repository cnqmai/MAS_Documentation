import logging
import os
from crewai import Task, Crew, Process
from memory.shared_memory import SharedMemory
from utils.output_formats import create_md

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_initial_requirement_collection_task(input_agent, existing_context: str):
    return Task(
        description=(
            f"You are a requirements elicitation expert. Your task is to ask clear, specific questions "
            f"to the user to clarify the initial requirements for a software system.\n\n"
            f"**RULES:**\n"
            f"1. Ask ONLY ONE question at a time.\n"
            f"2. If you have enough information, start your output with 'END_SUMMARY:' and write a summary.\n"
            f"3. Ask about aspects such as: goals, features, users, technical constraints, preferred technologies, etc.\n"
            f"--- Conversation context ---\n"
            f"{existing_context}\n\n"
            f"Next question or Summary:"
        ),
        expected_output="A single question or a summary starting with 'END_SUMMARY:'.",
        agent=input_agent,
        verbose=False
    )

def run_input_collection_conversation(input_agent, summary_output_dir: str, shared_memory: SharedMemory):
    logging.info("--- Starting system requirements elicitation from user (interactive) ---")

    os.makedirs(summary_output_dir, exist_ok=True)

    initial_prompt = "Welcome! Please describe the main idea or goal of the software system you want to build."
    print(f"\nAGENT ASKS: {initial_prompt}")
    print(" (Tip: If you want to finish and request a summary, type 'SUMMARY' and press Enter.)")
    user_input = input("YOUR ANSWER: ")

    conversation_history = [
        f"\nAGENT ASKS: {initial_prompt}\n",
        f"YOUR ANSWER: {user_input}\n"
    ]
    current_context = f"The user answered: {user_input}"
    user_requested_summary = False

    while True:
        task_context = "".join(conversation_history) + f"AGENT: {current_context}"
        if user_requested_summary:
            task_context += "\n\nThe user has requested a summary. Start your answer with 'END_SUMMARY:' and summarize all collected requirements."

        task = create_initial_requirement_collection_task(input_agent, task_context)
        crew = Crew(agents=[input_agent], tasks=[task], process=Process.sequential, verbose=False)

        try:
            result = crew.kickoff()
            agent_output = str(result).strip()

            if agent_output.startswith("END_SUMMARY:"):
                final_summary = agent_output.replace("END_SUMMARY:", "").strip()

                print("\n" + "="*80)
                print("        SYSTEM REQUIREMENTS SUMMARY        ")
                print("="*80)
                print(final_summary)
                print("="*80 + "\n")

                # ✅ Save to memory
                shared_memory.save("system_request_summary", final_summary)

                # ✅ Save Markdown file
                summary_path = os.path.join(summary_output_dir, "System_Request_Summary.md")
                create_md(final_summary, summary_path)

                history_md = "# Initial Requirements Elicitation Conversation History\n\n" + \
                             "".join(conversation_history) + \
                             f"\n\n## Final Summary:\n{final_summary}\n"
                history_path = os.path.join(summary_output_dir, "Conversation_History.md")
                create_md(history_md, history_path)

                logging.info(f"✅ Saved {summary_path} and {history_path}")
                break

            else:
                print(f"\nAGENT ASKS: {agent_output}")
                print(" (Tip: Type 'SUMMARY' if you want to finish and get a summary.)")

                conversation_history.append(f"\nAGENT ASKS: {agent_output}\n")
                user_response = input("YOUR ANSWER: ")

                if user_response.strip().upper() == "SUMMARY":
                    user_requested_summary = True
                    current_context = "The user has requested a summary of the collected requirements."
                    conversation_history.append("YOUR ANSWER: SUMMARY\n")
                    continue

                conversation_history.append(f"YOUR ANSWER: {user_response}\n")
                current_context = f"The user answered: {user_response}"

        except Exception as e:
            logging.error(f"❌ Error during requirements elicitation: {e}", exc_info=True)
            print("⚠️ An error occurred during requirements elicitation.")
            break

    logging.info("--- Finished requirements elicitation process ---")

import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx
from utils.phase_outputs import phase_outputs

# --- DOCX Callback Function ---
def make_docx_callback(title, filename, shared_memory, save_key):
    def callback(output_from_agent_object):
        print(f"Starting DOCX creation for: {title}...")
        content_raw_string = (
            getattr(output_from_agent_object, "result", None)
            or getattr(output_from_agent_object, "response", None)
            or getattr(output_from_agent_object, "final_output", None)
            or str(output_from_agent_object)
        )
        content_raw_string = str(content_raw_string)
        if not content_raw_string.strip():
            print(f"⚠️  Note: Agent did not return content for task '{title}'.")
            return False
        content_paragraphs = content_raw_string.split('\n')
        docx_path = create_docx(title, content_paragraphs, filename)
        shared_memory.save(save_key, content_raw_string)
        if docx_path:
            print(f"✅ DOCX '{filename}' created successfully and saved to SharedMemory '{save_key}'.")
            return True
        else:
            print(f"❌ System error: Unable to create DOCX '{filename}'.")
            return False
    return callback

# --- Main Task Creation Function ---
def create_quality_gate_tasks(shared_memory: SharedMemory, output_base_dir: str, project_manager_agent):
    tasks = []

    for phase_dir, output_docs in phase_outputs.items():
        phase_name = phase_dir.split('_', 1)[1].capitalize()
        os.makedirs(os.path.join(output_base_dir, phase_dir), exist_ok=True)

        global_context = {doc: shared_memory.load(doc) for doc in output_docs}

        tasks.append(Task(
            description=(
                f"Review the output documents of the {phase_name} phase to ensure completeness, accuracy, and validity according to standards such as ISTQB, PMBOK, or relevant industry standards. "
                f"Below is the data of the documents:\n\n"
                + '\n\n'.join([f"{doc}:\n{global_context[doc] or 'No data'}" for doc in output_docs]) + "\n\n"
                f"The report must include complete and specific content, leaving no section blank: list of reviewed documents ({', '.join(output_docs)}), evaluation criteria (completeness, accuracy, formatting, compliance), review results (pass/fail), detected issues, recommendations for improvement. "
                f"If data is missing, infer or make reasonable assumptions instead of leaving blank."
            ),
            agent=project_manager_agent,
            expected_output=(
                f"A complete document, fully filled out based on the review of {', '.join(output_docs)} according to industry standards (ISTQB, PMBOK). "
                f"The document is not a template, does not contain placeholders or [], but is specific and clear content. "
                f"Ready to be exported to DOCX for the {phase_name} phase."
            ),
            context=[
                {
                    "description": f"Information about the output documents of the {phase_name} phase",
                    "expected_output": f"Check the completeness and accuracy of documents such as {', '.join(output_docs)}.",
                    "input": f"Document list: {', '.join(output_docs)}\n\n" + '\n'.join([f"{doc}: {str(global_context[doc]) or 'No data'}" for doc in output_docs])
                }
            ],
            callback=make_docx_callback(
                f"Quality Gate Report - {phase_name}",
                os.path.join(output_base_dir, phase_dir, "Quality_Gate_0.docx"),
                shared_memory,
                f"quality_gate_{phase_dir}"
            )
        ))

    return tasks
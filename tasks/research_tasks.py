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
def create_research_tasks(shared_memory: SharedMemory, output_base_dir: str, researcher_agent):
    tasks = []

    for phase_dir, output_docs in phase_outputs.items():
        phase_name = phase_dir.split('_', 1)[1].capitalize()
        os.makedirs(os.path.join(output_base_dir, phase_dir), exist_ok=True)

        tasks.append(Task(
            description=(
                f"Research best practices for the {phase_name} phase based on industry standards (PMBOK, Agile, IEEE, or reputable sources) to optimize the process and documentation of this phase. "
                f"Pay special attention to the Initiation, Planning, and Requirements phases (if applicable), with specific examples of how to apply these practices to documents such as {', '.join(output_docs)}. "
                f"The document must include complete and specific content, leaving no section blank: introduction, purpose, list of best practices, application examples, benefits, references. "
                f"If data is missing, infer or make reasonable assumptions instead of leaving blank."
            ),
            agent=researcher_agent,
            expected_output=(
                f"A complete document, fully filled out based on research of industry standards (PMBOK, Agile, IEEE). "
                f"The document is not a template, does not contain placeholders or [], but is specific and clear content. "
                f"Ready to be exported to DOCX for the {phase_name} phase."
            ),
            context=[{
                "description": f"Information about the output documents of the {phase_name} phase",
                "expected_output": f"Summarize documents such as {', '.join(output_docs)} to apply best practices.",
                "input": f"Document list: {', '.join(output_docs)}"
            }],
            callback=make_docx_callback(
                f"Best Practices - {phase_name}",
                os.path.join(output_base_dir, phase_dir, f"Best_Practice_{phase_name}.docx"),
                shared_memory,
                f"best_practices_{phase_dir}"
            )
        ))

    return tasks
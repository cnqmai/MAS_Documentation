import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx, create_xlsx, create_image
from graphviz import Digraph
import json

# --- Adjusted Callback Functions ---
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
            print(f"❌ Error: Unable to create DOCX '{filename}'.")
            return False
    return callback

def make_docx_xlsx_callback(title, docx_filename, xlsx_filename, shared_memory, save_key):
    def callback(output_from_agent_object): 
        print(f"🚀 Starting DOCX and XLSX creation for: {title}...")
        try:
            raw_output_json_string = (
                getattr(output_from_agent_object, "result", None)
                or getattr(output_from_agent_object, "response", None)
                or getattr(output_from_agent_object, "final_output", None)
                or str(output_from_agent_object)
            )
            raw_output_json_string = str(raw_output_json_string)
            if not raw_output_json_string.strip():
                print(f"⚠️ Agent did not return JSON data for task '{title}'.")
                return False
            parsed_output = json.loads(raw_output_json_string)
            docx_content_raw = parsed_output.get("docx_content", "")
            xlsx_data_raw = parsed_output.get("xlsx_data", [])
            docx_paragraphs = docx_content_raw.split('\n')
            docx_path = create_docx(title, docx_paragraphs, docx_filename)
            xlsx_path = create_xlsx(xlsx_data_raw, xlsx_filename)
            shared_memory.save(save_key, raw_output_json_string)
            if docx_path and xlsx_path:
                print(f"✅ DOCX '{docx_filename}' and XLSX '{xlsx_filename}' created and saved successfully.")
                return True
            else:
                print(f"❌ Error creating DOCX or XLSX for task '{title}'.")
                return False
        except json.JSONDecodeError as e:
            print(f"❌ JSON Error: Unable to parse agent output for '{title}': {e}")
            print(f"🪵 Output received: {raw_output_json_string[:500]}...")
            return False
        except Exception as e:
            print(f"❌ Unknown error processing callback for '{title}': {e}")
            return False
    return callback

# --- Main Task Creation Function ---
def create_requirements_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, requirement_agent):
    tasks = []
    os.makedirs(f"{output_base_dir}/2_requirements", exist_ok=True)

    global_context = {
        "project_plan": shared_memory.load("project_plan"),
        "project_charter": shared_memory.load("project_charter"),
        "statement_of_work": shared_memory.load("statement_of_work"),
        "business_case": shared_memory.load("business_case"),
        "brd": shared_memory.load("brd"),
        "functional_requirements": shared_memory.load("functional_requirements"),
        "non_functional_requirements": shared_memory.load("non_functional_requirements"),
        "wbs": shared_memory.load("wbs"),
        "rtm": shared_memory.load("rtm")
    }

    # Task 1: Managing Scope and Requirements Checklist
    tasks.append(Task(
        description=(
            f"Below is the project_plan information:\n\n"
            f"{global_context['project_plan']}\n\n"
            f"Below is the project_charter information:\n\n"
            f"{global_context['project_charter']}\n\n"
            "Use the above data to write a complete 'Managing Scope and Requirements Checklist' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: purpose, product/system overview, project implementation reason, assumptions, dependencies, constraints, stakeholder list, risks, scope/requirements checklist. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=requirement_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_plan' and 'project_charter'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided project_plan information",
                "expected_output": "Summary of objectives, scope, risks...",
                "input": global_context["project_plan"]
            },
            {
                "description": "User-provided project_charter information",
                "expected_output": "Summary of product overview, reason, assumptions...",
                "input": global_context["project_charter"]
            }
        ],
        callback=make_docx_callback(
            "Managing Scope and Requirements Checklist",
            f"{output_base_dir}/2_requirements/Managing_Scope_and_Requirements_Checklist.docx",
            shared_memory,
            "scope_requirements_checklist"
        )
    ))

    # Task 2: Business Requirements Document (BRD)
    tasks.append(Task(
        description=(
            f"Below is the project_plan information:\n\n"
            f"{global_context['project_plan']}\n\n"
            f"Below is the statement_of_work information:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            f"Below is the business_case information:\n\n"
            f"{global_context['business_case']}\n\n"
            "Use the above data to write a complete 'Business Requirements Document (BRD)' with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: project information, current and improved processes, system and end-user requirements, other requirements. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=requirement_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_plan', 'statement_of_work', and 'business_case'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided project_plan information",
                "expected_output": "Summary of objectives, costs, risks...",
                "input": global_context["project_plan"]
            },
            {
                "description": "User-provided statement_of_work information",
                "expected_output": "Summary of improved processes, scope...",
                "input": global_context["statement_of_work"]
            },
            {
                "description": "User-provided business_case information",
                "expected_output": "Summary of business requirements, benefits...",
                "input": global_context["business_case"]
            }
        ],
        callback=make_docx_callback(
            "Business Requirements Document",
            f"{output_base_dir}/2_requirements/Business_Requirements_Document.docx",
            shared_memory,
            "brd"
        )
    ))

    # Task 3: Business Requirements Presentation To Stakeholders
    tasks.append(Task(
        description=(
            f"Below is the brd information:\n\n"
            f"{global_context['brd']}\n\n"
            "Use the above data to write a complete 'Business Requirements Presentation To Stakeholders' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: reason why business requirements are important, project information and description, objectives and scope, stakeholders, costs, annual maintenance, timeline, current/future process flow, high-level business requirements, system interfaces, infrastructure, other requirements. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=requirement_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'brd'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided brd information",
            "expected_output": "Summary of reason, objectives, scope, requirements...",
            "input": global_context["brd"]
        }],
        callback=make_docx_callback(
            "Business Requirements Presentation",
            f"{output_base_dir}/2_requirements/Business_Requirements_Presentation.docx",
            shared_memory,
            "brd_presentation"
        )
    ))

    # Task 4: Functional Requirements Document
    tasks.append(Task(
        description=(
            f"Below is the brd information:\n\n"
            f"{global_context['brd']}\n\n"
            f"Below is the project_plan information:\n\n"
            f"{global_context['project_plan']}\n\n"
            "Use the above data to write a complete 'Functional Requirements Document' with specific content, leaving no section blank. "
            "This document defines functional requirements, including: objectives, process information, functional and non-functional requirements, system interfaces, software, hardware, communication. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=requirement_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'brd' and 'project_plan'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided brd information",
                "expected_output": "Summary of business requirements, objectives, processes...",
                "input": global_context["brd"]
            },
            {
                "description": "User-provided project_plan information",
                "expected_output": "Summary of objectives, scope, business processes...",
                "input": global_context["project_plan"]
            }
        ],
        callback=make_docx_callback(
            "Functional Requirements Document",
            f"{output_base_dir}/2_requirements/Functional_Requirements_Document.docx",
            shared_memory,
            "functional_requirements"
        )
    ))

    # Task 5: Software Architecture Plan
    tasks.append(Task(
        description=(
            f"Below is the brd information:\n\n"
            f"{global_context['brd']}\n\n"
            f"Below is the functional_requirements information:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            "Use the above data to write a complete 'Software Architecture Plan' document with specific content, leaving no section blank. "
            "This document describes the software architecture overview from multiple perspectives, including: scope, notation, terminology, architecture objectives, views (Use-case, Logic, Process, Deployment, Data Deployment, Performance, Size, Quality). "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=requirement_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'brd' and 'functional_requirements'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided brd information",
                "expected_output": "Summary of business requirements, scope...",
                "input": global_context["brd"]
            },
            {
                "description": "User-provided functional_requirements information",
                "expected_output": "Summary of functional requirements, technical views...",
                "input": global_context["functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Software Architecture Plan",
            f"{output_base_dir}/2_requirements/Software_Architecture_Plan.docx",
            shared_memory,
            "software_architecture_plan"
        )
    ))

    # Task 6: Use Case Template
    tasks.append(Task(
        description=(
            f"Below is the functional_requirements information:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            "Use the above data to write a complete 'Use Case Template' document with specific content, leaving no section blank. "
            "This document describes project requirements as user scenarios to achieve goals, including: objectives, project information, high-level business requirements, interfaces, infrastructure, use case descriptions (simple, traditional, example), related requirements (screens, content, training). "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=requirement_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'functional_requirements'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided functional_requirements information",
            "expected_output": "Summary of functional requirements, usage scenarios, interfaces...",
            "input": global_context["functional_requirements"]
        }],
        callback=make_docx_callback(
            "Use Case Template",
            f"{output_base_dir}/2_requirements/Use_Case_Template.docx",
            shared_memory,
            "use_case_template"
        )
    ))

    # Task 7: Requirements Inspection Checklist
    tasks.append(Task(
        description=(
            f"Below is the brd information:\n\n"
            f"{global_context['brd']}\n\n"
            f"Below is the functional_requirements information:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            "Use the above data to write a complete 'Requirements Inspection Checklist' document with specific content, leaving no section blank. "
            "This document ensures project requirements are clearly defined and high quality, including: correctness, traceability, interfaces, behavioral and non-behavioral requirements. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=project_manager_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'brd' and 'functional_requirements'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided brd information",
                "expected_output": "Summary of business requirements, objectives...",
                "input": global_context["brd"]
            },
            {
                "description": "User-provided functional_requirements information",
                "expected_output": "Summary of functional requirements, interfaces, behaviors...",
                "input": global_context["functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Requirements Inspection Checklist",
            f"{output_base_dir}/2_requirements/Requirements_Inspection_Checklist.docx",
            shared_memory,
            "requirements_inspection_checklist"
        )
    ))

    # Task 8: Requirements Traceability Matrix (RTM)
    tasks.append(Task(
        description=(
            f"Below is the brd information:\n\n"
            f"{global_context['brd']}\n\n"
            f"Below is the functional_requirements information:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Below is the wbs information:\n\n"
            f"{global_context['wbs']}\n\n"
            "Use the above data to write a complete 'Requirements Traceability Matrix (RTM)' document with specific content, leaving no section blank. "
            "This matrix traces requirements from initial requirements to design and testing, ensuring completeness and consistency, including: purpose, requirements matrix (general info, interfaces, behaviors, non-behaviors, accuracy, traceability). "
            "Return a JSON string containing both the DOCX content (under 'docx_content') and the XLSX data (under 'xlsx_data'). "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=requirement_agent,
        expected_output=(
            "A valid JSON string containing two fields: "
            "'docx_content' is the content of the requirements traceability matrix document (structured, clear, all sections filled, no blanks or placeholders), "
            "'xlsx_data' is the spreadsheet data detailing requirements, sources, design, testing. "
            "docx_content can be in Markdown or plain text."
        ),
        context=[
            {
                "description": "User-provided brd information",
                "expected_output": "Summary of business requirements, objectives...",
                "input": global_context["brd"]
            },
            {
                "description": "User-provided functional_requirements information",
                "expected_output": "Summary of functional requirements, interfaces, behaviors...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "User-provided wbs information",
                "expected_output": "Summary of work structure, items...",
                "input": global_context["wbs"]
            }
        ],
        callback=make_docx_xlsx_callback(
            "Requirements Traceability Matrix",
            f"{output_base_dir}/2_requirements/Requirements_Traceability_Matrix.docx",
            f"{output_base_dir}/2_requirements/Requirements_Traceability_Matrix.xlsx",
            shared_memory,
            "rtm"
        )
    ))

    # Task 9: Requirements Changes Impact Analysis
    tasks.append(Task(
        description=(
            f"Below is the rtm information:\n\n"
            f"{global_context['rtm']}\n\n"
            f"Below is the brd information:\n\n"
            f"{global_context['brd']}\n\n"
            "Use the above data to write a complete 'Requirements Changes Impact Analysis' document with specific content, leaving no section blank. "
            "This document analyzes the impact of requirements changes, including: purpose, change description, risks, assumptions, affected components, time/cost estimation. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=requirement_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'rtm' and 'brd'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided rtm information",
                "expected_output": "Summary of requirements traceability matrix, related requirements...",
                "input": global_context["rtm"]
            },
            {
                "description": "User-provided brd information",
                "expected_output": "Summary of business requirements, objectives...",
                "input": global_context["brd"]
            }
        ],
        callback=make_docx_callback(
            "Requirements Changes Impact Analysis",
            f"{output_base_dir}/2_requirements/Requirements_Changes_Impact_Analysis.docx",
            shared_memory,
            "requirements_changes_impact"
        )
    ))

    # Task 10: Training Plan
    tasks.append(Task(
        description=(
            f"Below is the functional_requirements information:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Below is the brd information:\n\n"
            f"{global_context['brd']}\n\n"
            "Use the above data to write a complete 'Training Plan' document with specific content, leaving no section blank. "
            "This document supports the use and maintenance of the system or application, including: introduction, scope, training methods, user/technical training courses, environment requirements, training schedule, approval and sign-off. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=requirement_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'functional_requirements' and 'brd'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided functional_requirements information",
                "expected_output": "Summary of functional requirements, technical training...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "User-provided brd information",
                "expected_output": "Summary of business requirements, objectives, scope...",
                "input": global_context["brd"]
            }
        ],
        callback=make_docx_callback(
            "Training Plan",
            f"{output_base_dir}/2_requirements/Training_Plan.docx",
            shared_memory,
            "training_plan"
        )
    ))

    # Task 11: Service Level Agreement Template
    tasks.append(Task(
        description=(
            f"Below is the non_functional_requirements information:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            f"Below is the brd information:\n\n"
            f"{global_context['brd']}\n\n"
            "Use the above data to write a complete 'Service Level Agreement Template' document with specific content, leaving no section blank. "
            "This document is an official agreement between the organization and the customer about the provided service, including: terms, duration, related organizations, supported application list (disaster recovery, priority levels), responsibilities, support, performance reporting, termination/cancellation conditions, SLA modifications. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=requirement_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'non_functional_requirements' and 'brd'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided non_functional_requirements information",
                "expected_output": "Summary of non-functional requirements, performance, support...",
                "input": global_context["non_functional_requirements"]
            },
            {
                "description": "User-provided brd information",
                "expected_output": "Summary of business requirements, related organizations...",
                "input": global_context["brd"]
            }
        ],
        callback=make_docx_callback(
            "Service Level Agreement Template",
            f"{output_base_dir}/2_requirements/Service_Level_Agreement_Template.docx",
            shared_memory,
            "sla_template"
        )
    ))

    # Task 12: Non-functional Requirements
    tasks.append(Task(
        description=(
            f"Below is the brd information:\n\n"
            f"{global_context['brd']}\n\n"
            f"Below is the project_plan information:\n\n"
            f"{global_context['project_plan']}\n\n"
            "Use the above data to write a complete 'Non-functional Requirements' document with specific content, leaving no section blank. "
            "This document defines non-functional requirements such as performance, security, scalability, and usability, including: performance, security, scalability, usability requirements, technical and business constraints. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=requirement_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'brd' and 'project_plan'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided brd information",
                "expected_output": "Summary of business requirements, performance, security...",
                "input": global_context["brd"]
            },
            {
                "description": "User-provided project_plan information",
                "expected_output": "Summary of objectives, technical, business constraints...",
                "input": global_context["project_plan"]
            }
        ],
        callback=make_docx_callback(
            "Non-functional Requirements",
            f"{output_base_dir}/2_requirements/Non_functional_Requirements.docx",
            shared_memory,
            "non_functional_requirements"
        )
    ))

    # Task 13: Privacy & Security Requirements
    tasks.append(Task(
        description=(
            f"Below is the non_functional_requirements information:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            f"Below is the brd information:\n\n"
            f"{global_context['brd']}\n\n"
            "Use the above data to write a complete 'Privacy & Security Requirements' document with specific content, leaving no section blank. "
            "This document defines requirements related to system security and privacy, including: data security requirements, user privacy, legal compliance, access control measures. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=requirement_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'non_functional_requirements' and 'brd'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided non_functional_requirements information",
                "expected_output": "Summary of non-functional requirements, security, privacy...",
                "input": global_context["non_functional_requirements"]
            },
            {
                "description": "User-provided brd information",
                "expected_output": "Summary of business requirements, user information...",
                "input": global_context["brd"]
            }
        ],
        callback=make_docx_callback(
            "Privacy and Security Requirements",
            f"{output_base_dir}/2_requirements/Privacy_and_Security_Requirements.docx",
            shared_memory,
            "privacy_security_requirements"
        )
    ))

    # New Task: Use Case Diagram for BRD
    tasks.append(Task(
        description=(
            f"Based on project_charter and business_case data:\n\n"
            f"project_charter:\n{global_context['project_charter']}\n\n"
            f"business_case:\n{global_context['business_case']}\n\n"
            f"Create a use case diagram for the Business Requirements Document (BRD) to illustrate the main actors and use cases of the system. "
            f"The diagram must include at least 3 actors (e.g., User, Admin, External System) and 5 use cases (e.g., Login, Data Management, Report Export), with links showing relationships. "
            f"The result is Graphviz DOT code for a directed graph (digraph), saved to 'Use_Case_Diagram_BRD.dot' in the '{output_base_dir}/2_requirements' folder. "
            f"Render the DOT file as a PNG image using the create_image function. "
            f"Save the DOT code to SharedMemory with key 'graphviz_brd_use_case' and the PNG image path to SharedMemory with key 'image_brd_use_case'."
        ),
        agent=researcher_agent,
        expected_output=(
            f"Complete Graphviz DOT code illustrating the use case diagram for BRD, saved in '{output_base_dir}/2_requirements/Use_Case_Diagram_BRD.dot' and SharedMemory with key 'graphviz_brd_use_case'. "
            f"PNG image rendered from DOT, saved in '{output_base_dir}/2_requirements/Use_Case_Diagram_BRD.png' and SharedMemory with key 'image_brd_use_case'. "
            f"The diagram is clear, with at least 3 actors and 5 use cases, with links shown."
        ),
        context=[
            {
                "description": "Information from project_charter",
                "expected_output": "Summarize project objectives and related actors.",
                "input": global_context["project_charter"]
            },
            {
                "description": "Information from business_case",
                "expected_output": "Summarize business requirements to identify use cases.",
                "input": global_context["business_case"]
            }
        ],
        callback=lambda output: (
            shared_memory.save("graphviz_brd_use_case", output) and
            (open(os.path.join(output_base_dir, "2_requirements", "Use_Case_Diagram_BRD.dot"), "w", encoding="utf-8").write(output), True)[-1] and
            shared_memory.save("image_brd_use_case", create_image(Digraph(body=output.split('\n')[1:-1]), os.path.join(output_base_dir, "2_requirements", "Use_Case_Diagram_BRD")))
        )
    ))

    # New Task: Traceability Matrix for RTM (Graphviz)
    tasks.append(Task(
        description=(
            f"Based on functional_requirements and non_functional_requirements data:\n\n"
            f"functional_requirements:\n{global_context['functional_requirements']}\n\n"
            f"non_functional_requirements:\n{global_context['non_functional_requirements']}\n\n"
            f"Create a requirements traceability matrix for the Requirements Traceability Matrix (RTM) to illustrate the relationship between requirements and test cases. "
            f"The matrix must include at least 5 requirements (e.g., REQ-001, REQ-002) and 5 test cases (e.g., TC-001, TC-002), with links showing which requirements are tested by which test cases. "
            f"The result is Graphviz DOT code for a directed graph (digraph), saved to 'Traceability_Matrix_RTM.dot' in the '{output_base_dir}/2_requirements' folder. "
            f"Render the DOT file as a PNG image using the create_image function. "
            f"Save the DOT code to SharedMemory with key 'graphviz_rtm_traceability' and the PNG image path to SharedMemory with key 'image_rtm_traceability'."
        ),
        agent=researcher_agent,
        expected_output=(
            f"Complete Graphviz DOT code illustrating the requirements traceability matrix for RTM, saved in '{output_base_dir}/2_requirements/Traceability_Matrix_RTM.dot' and SharedMemory with key 'graphviz_rtm_traceability'. "
            f"PNG image rendered from DOT, saved in '{output_base_dir}/2_requirements/Traceability_Matrix_RTM.png' and SharedMemory with key 'image_rtm_traceability'. "
            f"The diagram is clear, with at least 5 requirements and 5 test cases, with links shown."
        ),
        context=[
            {
                "description": "Information from functional_requirements",
                "expected_output": "Summarize functional requirements to identify requirements.",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Information from non_functional_requirements",
                "expected_output": "Summarize non-functional requirements to supplement requirements.",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=lambda output: (
            shared_memory.save("graphviz_rtm_traceability", output) and
            (open(os.path.join(output_base_dir, "2_requirements", "Traceability_Matrix_RTM.dot"), "w", encoding="utf-8").write(output), True)[-1] and
            shared_memory.save("image_rtm_traceability", create_image(Digraph(body=output.split('\n')[1:-1]), os.path.join(output_base_dir, "2_requirements", "Traceability_Matrix_RTM")))
        )
    ))

    return tasks
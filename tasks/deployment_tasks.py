import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx, create_image
from graphviz import Digraph
import json

# --- DOCX Callback Function ---
def make_docx_callback(title, filename, shared_memory, save_key):
    def callback(output_from_agent_object):
        print(f"Bắt đầu tạo DOCX cho: {title}...")
        content_raw_string = (
            getattr(output_from_agent_object, "result", None)
            or getattr(output_from_agent_object, "response", None)
            or getattr(output_from_agent_object, "final_output", None)
            or str(output_from_agent_object)
        )
        content_raw_string = str(content_raw_string)
        if not content_raw_string.strip():
            print(f"⚠️  Lưu ý: Agent không trả về nội dung cho task '{title}'.")
            return False
        content_paragraphs = content_raw_string.split('\n')
        docx_path = create_docx(title, content_paragraphs, filename)
        shared_memory.save(save_key, content_raw_string)
        if docx_path:
            print(f"✅ DOCX '{filename}' đã tạo thành công và lưu vào SharedMemory '{save_key}'.")
            return True
        else:
            print(f"❌ Lỗi hệ thống: Không thể tạo DOCX '{filename}'.")
            return False
    return callback

# --- Main Task Creation Function ---
def create_deployment_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, deployment_agent):
    tasks = []
    os.makedirs(f"{output_base_dir}/6_deployment", exist_ok=True)

    global_context = {
        "build_deployment_plan": shared_memory.load("build_deployment_plan"),
        "system_architecture": shared_memory.load("system_architecture"),
        "functional_requirements": shared_memory.load("functional_requirements"),
        "ui_design_template": shared_memory.load("ui_design_template"),
        "security_architecture": shared_memory.load("security_architecture"),
        "test_summary_report": shared_memory.load("test_summary_report"),
        "project_acceptance": shared_memory.load("project_acceptance"),
        "production_implementation_plan": shared_memory.load("production_implementation_plan"),
        "system_admin_guide": shared_memory.load("system_admin_guide"),
        "non_functional_requirements": shared_memory.load("non_functional_requirements")
    }

    # Task 1: Process Guide
    tasks.append(Task(
        description=(
            f"Below is the build_deployment_plan data:\n\n"
            f"{global_context['build_deployment_plan']}\n\n"
            "Use the above data to write the 'Process Guide' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: introduction, purpose and scope, background, audience, references, process information, main procedures, tasks, functions, additional process information."
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=deployment_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'build_deployment_plan'."
            "The document is not a template, does not contain placeholders or [], but is specific and clear content."
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided build_deployment_plan information",
            "expected_output": "Summary of build and deployment plan, process details...",
            "input": global_context["build_deployment_plan"]
        }],
        callback=make_docx_callback(
            "Process Guide",
            f"{output_base_dir}/6_deployment/Process_Guide.docx",
            shared_memory,
            "process_guideline"
        )
    ))

    # Task 2: Installation Guide
    tasks.append(Task(
        description=(
            f"Below is the build_deployment_plan data:\n\n"
            f"{global_context['build_deployment_plan']}\n\n"
            f"Below is the system_architecture data:\n\n"
            f"{global_context['system_architecture']}\n\n"
            "Use the above data to write the 'Installation Guide' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: introduction, purpose, objectives, stakeholders, contacts, installation information, system overview, scope, environment, risks, security, pre-installation plan and requirements, installation schedule, installation instructions, main phases, tasks, backup and recovery, change and rollback process, installation support, hardware, software, network, facilities list."
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=deployment_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'build_deployment_plan' and 'system_architecture'."
            "The document is not a template, does not contain placeholders or [], but is specific and clear content."
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided build_deployment_plan information",
                "expected_output": "Summary of build and deployment plan, installation requirements...",
                "input": global_context["build_deployment_plan"]
            },
            {
                "description": "User-provided system_architecture information",
                "expected_output": "Summary of system architecture, installation environment...",
                "input": global_context["system_architecture"]
            }
        ],
        callback=make_docx_callback(
            "Installation Guide",
            f"{output_base_dir}/6_deployment/Installation_Guide.docx",
            shared_memory,
            "installation_guideline"
        )
    ))

    # Task 3: Software User Guide
    tasks.append(Task(
        description=(
            f"Below is the functional_requirements data:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Below is the ui_design_template data:\n\n"
            f"{global_context['ui_design_template']}\n\n"
            "Use the above data to write the 'Software User Guide' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: introduction, purpose and scope, background, audience, references, application overview, main components, functions, benefits, user roles, access information, navigation, menu guide, main page, actions, main procedures and functions."
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=deployment_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'functional_requirements' and 'ui_design_template'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided functional_requirements information",
                "expected_output": "Summary of functional requirements, main functions...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "User-provided ui_design_template information",
                "expected_output": "Summary of UI design template, navigation...",
                "input": global_context["ui_design_template"]
            }
        ],
        callback=make_docx_callback(
            "Software User Guide",
            f"{output_base_dir}/6_deployment/Software_User_Guide.docx",
            shared_memory,
            "software_user_guideline"
        )
    ))

    # Task 4: System Administration Guide
    tasks.append(Task(
        description=(
            f"Below is the system_architecture data:\n\n"
            f"{global_context['system_architecture']}\n\n"
            f"Below is the security_architecture data:\n\n"
            f"{global_context['security_architecture']}\n\n"
            "Use the above data to write the 'System Administration Guide' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: introduction, purpose, objectives, references, general system information, overview, data assets, process procedures, environment (facilities, hardware, software, network), administration and maintenance, server administration, user accounts, software/system administration, database administration, backup and recovery."
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=deployment_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'system_architecture' and 'security_architecture'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided system_architecture information",
                "expected_output": "Summary of system architecture, administration environment...",
                "input": global_context["system_architecture"]
            },
            {
                "description": "User-provided security_architecture information",
                "expected_output": "Summary of security architecture, data assets...",
                "input": global_context["security_architecture"]
            }
        ],
        callback=make_docx_callback(
            "System Administration Guide",
            f"{output_base_dir}/6_deployment/System_Administration_Guide.docx",
            shared_memory,
            "system_admin_guideline"
        )
    ))

    # Task 5: Operations Guide
    tasks.append(Task(
        description=(
            f"Below is the system_architecture data:\n\n"
            f"{global_context['system_architecture']}\n\n"
            f"Below is the build_deployment_plan data:\n\n"
            f"{global_context['build_deployment_plan']}\n\n"
            "Use the above data to write the 'Operations Guide' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: introduction, purpose, audience, system information, overview, contacts, environment, assets, system interfaces, operations, administration and maintenance, operations schedule, responsibility assignment, detailed operations procedures, maintenance and troubleshooting, change management, configuration, system administration, software, servers, databases."
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=deployment_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'system_architecture' and 'build_deployment_plan'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided system_architecture information",
                "expected_output": "Summary of system architecture, system interfaces...",
                "input": global_context["system_architecture"]
            },
            {
                "description": "User-provided build_deployment_plan information",
                "expected_output": "Summary of build and deployment plan, operations procedures...",
                "input": global_context["build_deployment_plan"]
            }
        ],
        callback=make_docx_callback(
            "Operations Guide",
            f"{output_base_dir}/6_deployment/Operations_Guide.docx",
            shared_memory,
            "operations_guideline"
        )
    ))

    # Task 6: Production Implementation Plan
    tasks.append(Task(
        description=(
            f"Below is the build_deployment_plan data:\n\n"
            f"{global_context['build_deployment_plan']}\n\n"
            f"Below is the test_summary_report data:\n\n"
            f"{global_context['test_summary_report']}\n\n"
            "Use the above data to write the 'Production Implementation Plan' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: product implementation description, objectives, affected devices, product handover steps, technical support information, potential impacts, software, hardware components and corresponding implementation steps, testing and acceptance, rollback and contingency plan, user training and documentation, other emergency contacts."
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=deployment_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'build_deployment_plan' and 'test_summary_report'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided build_deployment_plan information",
                "expected_output": "Summary of build and deployment plan, implementation description...",
                "input": global_context["build_deployment_plan"]
            },
            {
                "description": "User-provided test_summary_report information",
                "expected_output": "Summary of test summary report, affected devices...",
                "input": global_context["test_summary_report"]
            }
        ],
        callback=make_docx_callback(
            "Production Implementation Plan",
            f"{output_base_dir}/6_deployment/Production_Implementation_Plan.docx",
            shared_memory,
            "production_implementation_plan"
        )
    ))

    # Task 7: Production Turnover Approval
    tasks.append(Task(
        description=(
            f"Below is the project_acceptance data:\n\n"
            f"{global_context['project_acceptance']}\n\n"
            f"Below is the test_summary_report data:\n\n"
            f"{global_context['test_summary_report']}\n\n"
            "Use the above data to write the 'Production Turnover Approval' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: introduction, purpose, system/project overview, scope, turnover approval requirements, approval and sign-off."
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=deployment_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_acceptance' and 'test_summary_report'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided project_acceptance information",
                "expected_output": "Summary of project acceptance document, approval requirements...",
                "input": global_context["project_acceptance"]
            },
            {
                "description": "User-provided test_summary_report information",
                "expected_output": "Summary of test summary report, system overview...",
                "input": global_context["test_summary_report"]
            }
        ],
        callback=make_docx_callback(
            "Production Turnover Approval",
            f"{output_base_dir}/6_deployment/Production_Turnover_Approval.docx",
            shared_memory,
            "production_turnover_approval"
        )
    ))

    # Task 8: Deployment Plan
    tasks.append(Task(
        description=(
            f"Below is the build_deployment_plan data:\n\n"
            f"{global_context['build_deployment_plan']}\n\n"
            f"Below is the production_implementation_plan data:\n\n"
            f"{global_context['production_implementation_plan']}\n\n"
            "Use the above data to write the 'Deployment Plan' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: purpose, scope, deployment strategy, deployment schedule, deployment steps, deployment environment, post-deployment testing, rollback plan, post-deployment support."
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=deployment_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'build_deployment_plan' and 'production_implementation_plan'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided build_deployment_plan information",
                "expected_output": "Summary of build and deployment plan, deployment strategy...",
                "input": global_context["build_deployment_plan"]
            },
            {
                "description": "User-provided production_implementation_plan information",
                "expected_output": "Summary of production implementation plan, deployment schedule...",
                "input": global_context["production_implementation_plan"]
            }
        ],
        callback=make_docx_callback(
            "Deployment Plan",
            f"{output_base_dir}/6_deployment/Deployment_Plan.docx",
            shared_memory,
            "deployment_plan"
        )
    ))

    # Task 9: Monitoring and Alerting Setup Guide
    tasks.append(Task(
        description=(
            f"Below is the system_admin_guide data:\n\n"
            f"{global_context['system_admin_guide']}\n\n"
            f"Below is the non_functional_requirements data:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Use the above data to write the 'Monitoring and Alerting Setup Guide' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: purpose, monitoring tools, monitoring configuration, metrics to monitor, alert setup, incident response process, monitoring report."
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=deployment_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'system_admin_guide' and 'non_functional_requirements'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided system_admin_guide information",
                "expected_output": "Summary of system admin guide, monitoring tools...",
                "input": global_context["system_admin_guide"]
            },
            {
                "description": "User-provided non_functional_requirements information",
                "expected_output": "Summary of non-functional requirements, monitored metrics...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Monitoring and Alerting Setup Guide",
            f"{output_base_dir}/6_deployment/Monitoring_and_Alerting_Setup_Guide.docx",
            shared_memory,
            "monitoring_alerting_guideline"
        )
    ))

    # New Task: CI/CD Flow for Build and Deployment Plan (Graphviz)
    tasks.append(Task(
        description=(
            f"Based on the build_deployment_plan data:\n\n"
            f"build_deployment_plan:\n{global_context['build_deployment_plan']}\n\n"
            f"Create a CI/CD Flow diagram for the Build and Deployment Plan to illustrate the steps in the deployment pipeline (e.g., Build, Test, Deploy, Monitor). "
            f"The diagram must include at least 4 steps, with links showing the execution order. "
            f"The result is Graphviz DOT code for a directed graph (digraph), saved to 'CICD_Flow.dot' in the '{output_base_dir}/6_deployment' folder. "
            f"Render the DOT file as a PNG image using the create_image function. "
            f"Save the DOT code to SharedMemory with key 'graphviz_cicd_flow' and the PNG image path to SharedMemory with key 'image_cicd_flow'."
        ),
        agent=deployment_agent,
        expected_output=(
            f"Complete Graphviz DOT code illustrating the CI/CD flow diagram, saved in '{output_base_dir}/6_deployment/CICD_Flow.dot' and SharedMemory with key 'graphviz_cicd_flow'. "
            f"PNG image rendered from DOT, saved in '{output_base_dir}/6_deployment/CICD_Flow.png' and SharedMemory with key 'image_cicd_flow'. "
            f"The diagram is clear, with at least 4 steps and sequential links."
        ),
        context=[
            {
                "description": "Information from build_deployment_plan",
                "expected_output": "Summarize the build and deployment plan to identify CI/CD steps.",
                "input": global_context["build_deployment_plan"]
            }
        ],
        callback=lambda output: (
            shared_memory.save("graphviz_cicd_flow", output) and
            (open(os.path.join(output_base_dir, "6_deployment", "CICD_Flow.dot"), "w", encoding="utf-8").write(output), True)[-1] and
            shared_memory.save("image_cicd_flow", create_image(Digraph(body=output.split('\n')[1:-1]), os.path.join(output_base_dir, "6_deployment", "CICD_Flow")))
        )
    ))

    return tasks
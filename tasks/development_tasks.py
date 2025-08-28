import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx
import json

# --- Adjusted Callback Function ---
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
            print(f"✅ DOCX '{filename}' has been successfully created and saved to SharedMemory '{save_key}'.")
            return True
        else:
            print(f"❌ System Error: Unable to create DOCX '{filename}'.")
            return False
    return callback

# --- Main Task Creation Function ---
def create_development_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, development_agent):
    tasks = []
    os.makedirs(f"{output_base_dir}/4_development", exist_ok=True)

    global_context = {
        "technical_requirements": shared_memory.load("technical_requirements"),
        "project_plan": shared_memory.load("project_plan"),
        "dev_standards": shared_memory.load("dev_standards"),
        "coding_guidelines": shared_memory.load("coding_guidelines"),
        "system_architecture": shared_memory.load("system_architecture"),
        "api_design": shared_memory.load("api_design"),
        "version_control_plan": shared_memory.load("version_control_plan"),
        "integration_plan": shared_memory.load("integration_plan"),
        "wbs": shared_memory.load("wbs"),
        "lld": shared_memory.load("lld")
    }

    # Task 1: Development Standards Document
    tasks.append(Task(
        description=(
            f"Below is the data for technical_requirements:\n\n"
            f"{global_context['technical_requirements']}\n\n"
            f"Below is the data for project_plan:\n\n"
            f"{global_context['project_plan']}\n\n"
            "Please use the above data to write the 'Development Standards Document' with complete and specific content, leaving no section empty. "
            "Do not create templates or guidelines; real content is needed for each item: purpose, scope, coding standards, development tools, quality control processes, documentation requirements, performance and security standards. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=development_agent,
        expected_output=(
            "A complete document with content filled based on the actual data in 'technical_requirements' and 'project_plan'. "
            "The document is not a template, and does not contain placeholder instructions or brackets [], but clear and specific content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "Description of technical_requirements from the user",
                "expected_output": "Summary of technical requirements, coding standards, security...",
                "input": global_context["technical_requirements"]
            },
            {
                "description": "Description of project_plan from the user",
                "expected_output": "Summary of objectives, quality control processes...",
                "input": global_context["project_plan"]
            }
        ],
        callback=make_docx_callback(
            "Development Standards",
            f"{output_base_dir}/4_development/Development_Standards_Document.docx",
            shared_memory,
            "dev_standards"
        )
    ))

    # Task 2: Coding Guidelines
    tasks.append(Task(
        description=(
            f"Below is the data for dev_standards:\n\n"
            f"{global_context['dev_standards']}\n\n"
            "Please use the above data to write the 'Coding Guidelines' with complete and specific content, leaving no section empty. "
            "Do not create templates or guidelines; real content is needed for each item: coding style, naming conventions, code structure, error handling, code comments, and illustrative examples. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=development_agent,
        expected_output=(
            "A complete document with content filled based on the actual data in 'dev_standards'. "
            "The document is not a template, and does not contain placeholder instructions or brackets [], but clear and specific content. "
            "Ready to be converted to DOCX file."
        ),
        context=[{
            "description": "Description of dev_standards from the user",
            "expected_output": "Summary of coding standards, naming conventions, code comments...",
            "input": global_context["dev_standards"]
        }],
        callback=make_docx_callback(
            "Coding Guidelines",
            f"{output_base_dir}/4_development/Coding_Guidelines.docx",
            shared_memory,
            "coding_guidelines"
        )
    ))

    # Task 3: Version Control Plan
    tasks.append(Task(
        description=(
            f"Below is the data for dev_standards:\n\n"
            f"{global_context['dev_standards']}\n\n"
            "Please use the above data to write the 'Version Control Plan' with complete and specific content, leaving no section empty. "
            "Do not create templates or guidelines; real content is needed for each item: purpose, version control tools, branch and merge processes, commit rules, tag and release management, backup procedures. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=development_agent,
        expected_output=(
            "A complete document with content filled based on the actual data in 'dev_standards'. "
            "The document is not a template, and does not contain placeholder instructions or brackets [], but clear and specific content. "
            "Ready to be converted to DOCX file."
        ),
        context=[{
            "description": "Description of dev_standards from the user",
            "expected_output": "Summary of development standards, version control tools...",
            "input": global_context["dev_standards"]
        }],
        callback=make_docx_callback(
            "Version Control Plan",
            f"{output_base_dir}/4_development/Version_Control_Plan.docx",
            shared_memory,
            "version_control_plan"
        )
    ))

    # Task 4: Integration Plan
    tasks.append(Task(
        description=(
            f"Below is the data for system_architecture:\n\n"
            f"{global_context['system_architecture']}\n\n"
            f"Below is the data for api_design:\n\n"
            f"{global_context['api_design']}\n\n"
            "Please use the above data to write the 'Integration Plan' with complete and specific content, leaving no section empty. "
            "Do not create templates or guidelines; real content is needed for each item: purpose, scope, integration strategy, integration schedule, integrated components, environment requirements, integration testing processes. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=development_agent,
        expected_output=(
            "A complete document with content filled based on the actual data in 'system_architecture' and 'api_design'. "
            "The document is not a template, and does not contain placeholder instructions or brackets [], but clear and specific content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "Description of system_architecture from the user",
                "expected_output": "Summary of system architecture, integrated components...",
                "input": global_context["system_architecture"]
            },
            {
                "description": "Description of api_design from the user",
                "expected_output": "Summary of API design, API integration...",
                "input": global_context["api_design"]
            }
        ],
        callback=make_docx_callback(
            "Integration Plan",
            f"{output_base_dir}/4_development/Integration_Plan.docx",
            shared_memory,
            "integration_plan"
        )
    ))

    # Task 5: Code Review Checklist
    tasks.append(Task(
        description=(
            f"Below is the data for coding_guidelines:\n\n"
            f"{global_context['coding_guidelines']}\n\n"
            f"Below is the data for technical_requirements:\n\n"
            f"{global_context['technical_requirements']}\n\n"
            "Please use the above data to write the 'Code Review Checklist' with complete and specific content, leaving no section empty. "
            "Do not create templates or guidelines; real content is needed for each item: code structure, documentation, variables, data types, programming style, control structures, loops, maintenance, security, error testing, exception handling, testing, validation. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=project_manager_agent,
        expected_output=(
            "A complete document with content filled based on the actual data in 'coding_guidelines' and 'technical_requirements'. "
            "The document is not a template, and does not contain placeholder instructions or brackets [], but clear and specific content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "Description of coding_guidelines from the user",
                "expected_output": "Summary of coding guidelines, programming style...",
                "input": global_context["coding_guidelines"]
            },
            {
                "description": "Description of technical_requirements from the user",
                "expected_output": "Summary of technical requirements, security, testing...",
                "input": global_context["technical_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Code Review Checklist",
            f"{output_base_dir}/4_development/Code_Review_Checklist.docx",
            shared_memory,
            "code_review_checklist"
        )
    ))

    # Task 6: Source Code Repository Checklist
    tasks.append(Task(
        description=(
            f"Below is the data for version_control_plan:\n\n"
            f"{global_context['version_control_plan']}\n\n"
            "Please use the above data to write the 'Source Code Repository Checklist' with complete and specific content, leaving no section empty. "
            "Do not create templates or guidelines; real content is needed for each item: repository configuration, access rights, directory structure, commit rules, security checks, backups, and repository monitoring. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=development_agent,
        expected_output=(
            "A complete document with content filled based on the actual data in 'version_control_plan'. "
            "The document is not a template, and does not contain placeholder instructions or brackets [], but clear and specific content. "
            "Ready to be converted to DOCX file."
        ),
        context=[{
            "description": "Description of version_control_plan from the user",
            "expected_output": "Summary of version control plan, repository configuration...",
            "input": global_context["version_control_plan"]
        }],
        callback=make_docx_callback(
            "Source Code Repository Checklist",
            f"{output_base_dir}/4_development/Source_Code_Repository_Checklist.docx",
            shared_memory,
            "source_code_repo_checklist"
        )
    ))

    # Task 7: Development Progress Report
    tasks.append(Task(
        description=(
            f"Below is the data for project_plan:\n\n"
            f"{global_context['project_plan']}\n\n"
            f"Below is the data for wbs:\n\n"
            f"{global_context['wbs']}\n\n"
            "Please use the above data to write the 'Development Progress Report' with complete and specific content, leaving no section empty. "
            "Do not create templates or guidelines; real content is needed for each item: overall progress, completed tasks, ongoing tasks, risks and issues, next steps. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=development_agent,
        expected_output=(
            "A complete document with content filled based on the actual data in 'project_plan' and 'wbs'. "
            "The document is not a template, and does not contain placeholder instructions or brackets [], but clear and specific content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "Description of project_plan from the user",
                "expected_output": "Summary of project objectives, progress...",
                "input": global_context["project_plan"]
            },
            {
                "description": "Description of wbs from the user",
                "expected_output": "Summary of work breakdown structure, completed tasks...",
                "input": global_context["wbs"]
            }
        ],
        callback=make_docx_callback(
            "Development Progress Report",
            f"{output_base_dir}/4_development/Development_Progress_Report.docx",
            shared_memory,
            "dev_progress_report"
        )
    ))

    # Task 8: Build and Deployment Plan
    tasks.append(Task(
        description=(
            f"Below is the data for integration_plan:\n\n"
            f"{global_context['integration_plan']}\n\n"
            f"Below is the data for system_architecture:\n\n"
            f"{global_context['system_architecture']}\n\n"
            "Please use the above data to write the 'Build and Deployment Plan' with complete and specific content, leaving no section empty. "
            "Do not create templates or guidelines; real content is needed for each item: purpose, build strategy, build tools, deployment process, deployment environment, post-deployment testing, rollback plan. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=development_agent,
        expected_output=(
            "A complete document with content filled based on the actual data in 'integration_plan' and 'system_architecture'. "
            "The document is not a template, and does not contain placeholder instructions or brackets [], but clear and specific content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "Description of integration_plan from the user",
                "expected_output": "Summary of integration plan, build strategy...",
                "input": global_context["integration_plan"]
            },
            {
                "description": "Description of system_architecture from the user",
                "expected_output": "Summary of system architecture, CI/CD tools...",
                "input": global_context["system_architecture"]
            }
        ],
        callback=make_docx_callback(
            "Build and Deployment Plan",
            f"{output_base_dir}/4_development/Build_and_Deployment_Plan.docx",
            shared_memory,
            "build_deployment_plan"
        )
    ))

    # Task 9: Middleware Documentation
    tasks.append(Task(
        description=(
            f"Below is the data for integration_plan:\n\n"
            f"{global_context['integration_plan']}\n\n"
            f"Below is the data for api_design:\n\n"
            f"{global_context['api_design']}\n\n"
            "Please use the above data to write the 'Middleware Documentation' with complete and specific content, leaving no section empty. "
            "Do not create templates or guidelines; real content is needed for each item: middleware overview, middleware components, configuration, API integration, performance and security, maintenance processes. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=development_agent,
        expected_output=(
            "A complete document with content filled based on the actual data in 'integration_plan' and 'api_design'. "
            "The document is not a template, and does not contain placeholder instructions or brackets [], but clear and specific content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "Description of integration_plan from the user",
                "expected_output": "Summary of integration plan, middleware roles...",
                "input": global_context["integration_plan"]
            },
            {
                "description": "Description of api_design from the user",
                "expected_output": "Summary of API design, API integration...",
                "input": global_context["api_design"]
            }
        ],
        callback=make_docx_callback(
            "Middleware Documentation",
            f"{output_base_dir}/4_development/Middleware_Documentation.docx",
            shared_memory,
            "middleware_documentation"
        )
    ))

    # Task 10: Source Code Documentation
    tasks.append(Task(
        description=(
            f"Below is the data for lld:\n\n"
            f"{global_context['lld']}\n\n"
            f"Below is the data for coding_guidelines:\n\n"
            f"{global_context['coding_guidelines']}\n\n"
            "Please use the above data to write the 'Source Code Documentation' with complete and specific content, leaving no section empty. "
            "Do not create templates or guidelines; real content is needed for each item: source code overview, module structure, function descriptions, code comments, usage instructions, code examples. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=development_agent,
        expected_output=(
            "A complete document with content filled based on the actual data in 'lld' and 'coding_guidelines'. "
            "The document is not a template, and does not contain placeholder instructions or brackets [], but clear and specific content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "Description of lld from the user",
                "expected_output": "Summary of low-level design, module structure...",
                "input": global_context["lld"]
            },
            {
                "description": "Description of coding_guidelines from the user",
                "expected_output": "Summary of coding guidelines, code comments...",
                "input": global_context["coding_guidelines"]
            }
        ],
        callback=make_docx_callback(
            "Source Code Documentation",
            f"{output_base_dir}/4_development/Source_Code_Documentation.docx",
            shared_memory,
            "source_code_documentation"
        )
    ))

    return tasks
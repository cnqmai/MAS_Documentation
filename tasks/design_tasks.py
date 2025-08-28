import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx, create_xlsx, create_image
from graphviz import Digraph
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
            print(f"❌ System error: Unable to create DOCX '{filename}'.")
            return False
    return callback

# --- Main Task Creation Function ---
def create_design_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, design_agent):
    tasks = []
    os.makedirs(f"{output_base_dir}/3_design", exist_ok=True)

    global_context = {
        "brd": shared_memory.load("brd"),
        "functional_requirements": shared_memory.load("functional_requirements"),
        "non_functional_requirements": shared_memory.load("non_functional_requirements"),
        "project_plan": shared_memory.load("project_plan"),
        "wbs": shared_memory.load("wbs"),
        "srs": shared_memory.load("srs"),
        "software_architecture_plan": shared_memory.load("software_architecture_plan"),
        "use_case_template": shared_memory.load("use_case_template"),
        "privacy_security_requirements": shared_memory.load("privacy_security_requirements"),
        "system_architecture": shared_memory.load("system_architecture"),
        "hld": shared_memory.load("hld"),
        "technical_requirements": shared_memory.load("technical_requirements"),
        "system_requirements": shared_memory.load("system_requirements")
    }

    # Task 1: System Requirements Specification
    tasks.append(Task(
        description=(
            f"Below is the BRD data:\n\n"
            f"{global_context['brd']}\n\n"
            f"Below is the functional requirements data:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Below is the non-functional requirements data:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Please use the above data to write the 'System Requirements Specification' (SRS) document with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: introduction, purpose, scope, roles and responsibilities, system requirements, functional requirements, software/hardware requirements, user characteristics, usability, operating environment, security, regulatory compliance, disaster recovery, data parameters, network impact. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'brd', 'functional_requirements', and 'non_functional_requirements'. "
            "The document is not a template, and does not contain placeholder guidelines or parentheses (), but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "BRD information description from the user",
                "expected_output": "Summary of business requirements, objectives, scope...",
                "input": global_context["brd"]
            },
            {
                "description": "Functional requirements information description from the user",
                "expected_output": "Summary of functional requirements, user characteristics...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Non-functional requirements information description from the user",
                "expected_output": "Summary of non-functional requirements, security, performance...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "System Requirements Specification",
            f"{output_base_dir}/3_design/System_Requirements_Specifications.docx",
            shared_memory,
            "srs"
        )
    ))

    # Task 2: Analysis and Design Document
    tasks.append(Task(
        description=(
            f"Below is the SRS data:\n\n"
            f"{global_context['srs']}\n\n"
            "Please use the above data to write the 'Analysis and Design Document' with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: system overview, infrastructure, design assumptions, summary of changes from initiation, business impact, application, current and proposed architecture, security and auditing, interface design, application layer, deployment information, future enhancements, approval. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'srs'. "
            "The document is not a template, and does not contain placeholder guidelines or parentheses (), but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[{
            "description": "SRS information description from the user",
            "expected_output": "Summary of system requirements, architecture, security...",
            "input": global_context["srs"]
        }],
        callback=make_docx_callback(
            "Analysis and Design Document",
            f"{output_base_dir}/3_design/Analysis_and_Design_Document.docx",
            shared_memory,
            "analysis_design"
        )
    ))

    # Task 3: Application Development Project List
    tasks.append(Task(
        description=(
            f"Below is the project plan data:\n\n"
            f"{global_context['project_plan']}\n\n"
            f"Below is the WBS data:\n\n"
            f"{global_context['wbs']}\n\n"
            "Please use the above data to write the 'Application Development Project List' document with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: system description, current and proposed software architecture, interface design, application layers, infrastructure impact, security, integration, deployment, proposed improvements, approval. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'project_plan' and 'wbs'. "
            "The document is not a template, and does not contain placeholder guidelines or parentheses (), but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "Project plan information description from the user",
                "expected_output": "Summary of objectives, system description...",
                "input": global_context["project_plan"]
            },
            {
                "description": "WBS information description from the user",
                "expected_output": "Summary of work breakdown structure, software architecture...",
                "input": global_context["wbs"]
            }
        ],
        callback=make_docx_callback(
            "Application Development Project List",
            f"{output_base_dir}/3_design/Application_Development_Project_List.docx",
            shared_memory,
            "app_dev_project_list"
        )
    ))

    # Task 4: Technical Requirements Document
    tasks.append(Task(
        description=(
            f"Below is the SRS data:\n\n"
            f"{global_context['srs']}\n\n"
            "Please use the above data to write the 'Technical Requirements Document' with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: purpose, scope, reference documents, assumptions, specific technical requirements (system, network, database, user interface, system interface, security). "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'srs'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[{
            "description": "SRS information description from the user",
            "expected_output": "Summary of technical requirements, system, security...",
            "input": global_context["srs"]
        }],
        callback=make_docx_callback(
            "Technical Requirements Document",
            f"{output_base_dir}/3_design/Technical_Requirements_Document.docx",
            shared_memory,
            "technical_requirements"
        )
    ))

    # Task 5: Database Design Document
    tasks.append(Task(
        description=(
            f"Below is the SRS data:\n\n"
            f"{global_context['srs']}\n\n"
            f"Below is the software architecture data:\n\n"
            f"{global_context['software_architecture_plan']}\n\n"
            "Please use the above data to write the 'Database Design Document' with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: objectives, data users, data owner and steward, assumptions, constraints, system overview, hardware/software architecture, overall design decisions, DBMS functions, detailed design (data mapping, backup, recovery), reporting requirements. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'srs' and 'software_architecture_plan'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "SRS information description from the user",
                "expected_output": "Summary of system requirements, data...",
                "input": global_context["srs"]
            },
            {
                "description": "Software architecture plan information description from the user",
                "expected_output": "Summary of hardware/software architecture...",
                "input": global_context["software_architecture_plan"]
            }
        ],
        callback=make_docx_callback(
            "Database Design Document",
            f"{output_base_dir}/3_design/Database_Design_Document.docx",
            shared_memory,
            "database_design"
        )
    ))

    # Task 6: Website Planning Checklist
    tasks.append(Task(
        description=(
            f"Below is the functional requirements data:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Below is the non-functional requirements data:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Please use the above data to write the 'Website Planning Checklist' document with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: target audience analysis, competitor analysis, content strategy, promotion and maintenance, page structure, navigation, image and layout design, user interface design, testing techniques. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'functional_requirements' and 'non_functional_requirements'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "Functional requirements information description from the user",
                "expected_output": "Summary of functional requirements, audience, interface...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Non-functional requirements information description from the user",
                "expected_output": "Summary of non-functional requirements, design, testing...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Website Planning Checklist",
            f"{output_base_dir}/3_design/Website_Planning_Checklist.docx",
            shared_memory,
            "website_planning_checklist"
        )
    ))

    # Task 7: User Interface Design Template
    tasks.append(Task(
        description=(
            f"Below is the functional requirements data:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            "Please use the above data to write the 'User Interface Design Template' document with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: product/system name, reason for redesign, screen details (name, function, tab, navigation), components (data field, data type, length, calculation, dropdown, font, color, size, action button, popup, format, event), constraints, risks, stakeholders. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'functional_requirements'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[{
            "description": "Functional requirements information description from the user",
            "expected_output": "Summary of functional requirements, interface, components...",
            "input": global_context["functional_requirements"]
        }],
        callback=make_docx_callback(
            "User Interface Design Template",
            f"{output_base_dir}/3_design/User_Interface_Design_Template.docx",
            shared_memory,
            "ui_design_template"
        )
    ))

    # Task 8: Report Design Template
    tasks.append(Task(
        description=(
            f"Below is the functional requirements data:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            "Please use the above data to write the 'Report Design Template' document with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: system name, report purpose, frequency, access rights, assumptions, constraints, risks, stakeholders, components (input parameters, calculations, formulas, report fields, data sources, data groups, title/page, report template). "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'functional_requirements'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[{
            "description": "Functional requirements information description from the user",
            "expected_output": "Summary of functional requirements, reports, data sources...",
            "input": global_context["functional_requirements"]
        }],
        callback=make_docx_callback(
            "Report Design Template",
            f"{output_base_dir}/3_design/Report_Design_Template.docx",
            shared_memory,
            "report_design_template"
        )
    ))

    # Task 9: Code Review Checklist
    tasks.append(Task(
        description=(
            f"Below are the technical requirements data:\n\n"
            f"{global_context['technical_requirements']}\n\n"
            "Please use the above data to write the 'Code Review Checklist' document with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: structure, documentation, variables, data types, programming style, control structures, loops, maintenance, security, usability, error checking, exception handling, resource leaks, timing, testing, validation. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=project_manager_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'technical_requirements'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[{
            "description": "Technical requirements information description from the user",
            "expected_output": "Summary of technical requirements, security, testing...",
            "input": global_context["technical_requirements"]
        }],
        callback=make_docx_callback(
            "Code Review Checklist",
            f"{output_base_dir}/3_design/Code_Review_Checklist.docx",
            shared_memory,
            "code_review_checklist"
        )
    ))

    # Task 10: Conversion Plan
    tasks.append(Task(
        description=(
            f"Below is the SRS data:\n\n"
            f"{global_context['srs']}\n\n"
            "Please use the above data to write the 'Conversion Plan' document with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: purpose, reference documents, system description and conversion strategy, types of conversion, risk factors, conversion schedule, conversion support (hardware, software, personnel), ensuring security and data quality. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'srs'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[{
            "description": "SRS information description from the user",
            "expected_output": "Summary of system requirements, conversion strategy...",
            "input": global_context["srs"]
        }],
        callback=make_docx_callback(
            "Conversion Plan",
            f"{output_base_dir}/3_design/Conversion_Plan.docx",
            shared_memory,
            "conversion_plan"
        )
    ))

    # Task 11: System Architecture
    tasks.append(Task(
        description=(
            f"Below is the software architecture plan data:\n\n"
            f"{global_context['software_architecture_plan']}\n\n"
            f"Below is the non-functional requirements data:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Please use the above data to write the 'System Architecture' document with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: architecture overview, system components, relationships between components, performance requirements, security, scalability. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'software_architecture_plan' and 'non_functional_requirements'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "Software architecture plan information description from the user",
                "expected_output": "Summary of system architecture, components...",
                "input": global_context["software_architecture_plan"]
            },
            {
                "description": "Non-functional requirements information description from the user",
                "expected_output": "Summary of non-functional requirements, performance, security...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "System Architecture",
            f"{output_base_dir}/3_design/System_Architecture.docx",
            shared_memory,
            "system_architecture"
        )
    ))

    # Task 12: Data Flow Diagrams (DFD)
    tasks.append(Task(
        description=(
            f"Below is the SRS data:\n\n"
            f"{global_context['srs']}\n\n"
            "Please use the above data to write the 'Data Flow Diagrams' (DFD) document with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: level 0 DFD, lower-level DFDs, description of processes, data storage, and data flow. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'srs'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[{
            "description": "SRS information description from the user",
            "expected_output": "Summary of system requirements, data flow...",
            "input": global_context["srs"]
        }],
        callback=make_docx_callback(
            "Data Flow Diagrams",
            f"{output_base_dir}/3_design/Data_Flow_Diagrams.docx",
            shared_memory,
            "dfd"
        )
    ))

    # Task 13: Sequence Diagrams
    tasks.append(Task(
        description=(
            f"Below is the functional requirements data:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Below is the use case template data:\n\n"
            f"{global_context['use_case_template']}\n\n"
            "Please use the above data to write the 'Sequence Diagrams' document with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: sequence diagram for main scenarios, description of objects, messages, and interaction sequence. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'functional_requirements' and 'use_case_template'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "Functional requirements information description from the user",
                "expected_output": "Summary of functional requirements, interaction objects...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Use case template information description from the user",
                "expected_output": "Summary of use case scenarios, interaction sequence...",
                "input": global_context["use_case_template"]
            }
        ],
        callback=make_docx_callback(
            "Sequence Diagrams",
            f"{output_base_dir}/3_design/Sequence_Diagrams.docx",
            shared_memory,
            "sequence_diagrams"
        )
    ))

    # Task 14: Security Architecture Document
    tasks.append(Task(
        description=(
            f"Below are the privacy security requirements data:\n\n"
            f"{global_context['privacy_security_requirements']}\n\n"
            f"Below is the system architecture data:\n\n"
            f"{global_context['system_architecture']}\n\n"
            "Please use the above data to write the 'Security Architecture Document' with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: security requirements, security architecture, access control measures, data encryption, and regulatory compliance. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'privacy_security_requirements' and 'system_architecture'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "Privacy security requirements information description from the user",
                "expected_output": "Summary of security requirements, access control...",
                "input": global_context["privacy_security_requirements"]
            },
            {
                "description": "System architecture information description from the user",
                "expected_output": "Summary of system architecture, security components...",
                "input": global_context["system_architecture"]
            }
        ],
        callback=make_docx_callback(
            "Security Architecture Document",
            f"{output_base_dir}/3_design/Security_Architecture_Document.docx",
            shared_memory,
            "security_architecture"
        )
    ))

    # Task 15: High-Level Design (HLD)
    tasks.append(Task(
        description=(
            f"Below is the SRS data:\n\n"
            f"{global_context['srs']}\n\n"
            f"Below is the software architecture plan data:\n\n"
            f"{global_context['software_architecture_plan']}\n\n"
            "Please use the above data to write the 'High-Level Design' (HLD) document with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: system overview, main components, relationships between components, software and hardware architecture. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'srs' and 'software_architecture_plan'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "SRS information description from the user",
                "expected_output": "Summary of system requirements, overview...",
                "input": global_context["srs"]
            },
            {
                "description": "Software architecture plan information description from the user",
                "expected_output": "Summary of software architecture, main components...",
                "input": global_context["software_architecture_plan"]
            }
        ],
        callback=make_docx_callback(
            "High-Level Design",
            f"{output_base_dir}/3_design/High_Level_Design.docx",
            shared_memory,
            "hld"
        )
    ))

    # Task 16: Low-Level Design (LLD)
    tasks.append(Task(
        description=(
            f"Below is the HLD data:\n\n"
            f"{global_context['hld']}\n\n"
            f"Below are the technical requirements data:\n\n"
            f"{global_context['technical_requirements']}\n\n"
            "Please use the above data to write the 'Low-Level Design' (LLD) document with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: detailed description of modules, interfaces, algorithms, data structures. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'hld' and 'technical_requirements'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "HLD information description from the user",
                "expected_output": "Summary of high-level design, modules...",
                "input": global_context["hld"]
            },
            {
                "description": "Technical requirements information description from the user",
                "expected_output": "Summary of technical requirements, algorithms, data structures...",
                "input": global_context["technical_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Low-Level Design",
            f"{output_base_dir}/3_design/Low_Level_Design.docx",
            shared_memory,
            "lld"
        )
    ))

    # Task 17: API Design Document
    tasks.append(Task(
        description=(
            f"Below is the functional requirements data:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Below are the technical requirements data:\n\n"
            f"{global_context['technical_requirements']}\n\n"
            "Please use the above data to write the 'API Design Document' with complete, specific content, leaving no section empty. "
            "Do not create a template or guidelines; instead, fill in the actual content for each section: API description, endpoint, method, parameters, response, and security. "
            "If data is missing, please infer or make reasonable assumptions instead of leaving it blank."
        ),
        agent=design_agent,
        expected_output=(
            "A complete document with content fully filled based on the actual data in 'functional_requirements' and 'technical_requirements'. "
            "The document is not a template, and does not contain placeholder guidelines or brackets [], but rather specific and clear content. "
            "Ready to be converted to DOCX file."
        ),
        context=[
            {
                "description": "Functional requirements information description from the user",
                "expected_output": "Summary of functional requirements, API description...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Technical requirements information description from the user",
                "expected_output": "Summary of technical requirements, security, endpoint...",
                "input": global_context["technical_requirements"]
            }
        ],
        callback=make_docx_callback(
            "API Design Document",
            f"{output_base_dir}/3_design/API_Design_Document.docx",
            shared_memory,
            "api_design"
        )
    ))


    # New Task: System Architecture Diagram for System Architecture (Graphviz)
    tasks.append(Task(
        description=(
            f"Based on the system requirements data:\n\n"
            f"system_requirements:\n{global_context['system_requirements']}\n\n"
            f"Create a system architecture diagram for System Architecture to illustrate the main components of the system (e.g., Frontend, Backend, Database, API Gateway). "
            f"The diagram must include at least 4 components and links showing the interaction flow between them. "
            f"The result is Graphviz DOT code formatting a directed diagram (digraph), saved to the file 'System_Architecture_Diagram.dot' in the folder '{output_base_dir}/4_design'. "
            f"Render the DOT file to a PNG image using the create_image function. "
            f"Save the DOT code to SharedMemory with the key 'graphviz_system_architecture' and the PNG image path to SharedMemory with the key 'image_system_architecture'."
        ),
        agent=design_agent,
        expected_output=(
            f"Complete Graphviz DOT code illustrating the system architecture diagram, saved in '{output_base_dir}/3_design/System_Architecture_Diagram.dot' and SharedMemory with the key 'graphviz_system_architecture'. "
            f"The PNG image rendered from DOT, saved in '{output_base_dir}/3_design/System_Architecture_Diagram.png' and SharedMemory with the key 'image_system_architecture'. "
            f"The diagram is clear, with at least 4 components and interaction links."
        ),
        context=[
            {
                "description": "Information from system_requirements",
                "expected_output": "Summary of system requirements to identify architecture components.",
                "input": global_context["system_requirements"]
            }
        ],
        callback=lambda output: (
            shared_memory.save("graphviz_system_architecture", output) and
            (open(os.path.join(output_base_dir, "3_design", "System_Architecture_Diagram.dot"), "w", encoding="utf-8").write(output), True)[-1] and
            shared_memory.save("image_system_architecture", create_image(Digraph(body=output.split('\n')[1:-1]), os.path.join(output_base_dir, "4_design", "System_Architecture_Diagram")))
        )
    ))

    # New Task: Wireframe for User Interface Design Template (Graphviz)
    tasks.append(Task(
        description=(
            f"Based on the functional requirements data:\n\n"
            f"functional_requirements:\n{global_context['functional_requirements']}\n\n"
            f"Create a wireframe template for User Interface Design Template to illustrate the user interface layout (e.g., Header, Sidebar, Content Area, Footer). "
            f"The wireframe must include at least 4 interface components and links showing the navigation flow. "
            f"The result is Graphviz DOT code formatting a directed diagram (digraph), saved to the file 'UI_Wireframe.dot' in the folder '{output_base_dir}/4_design'. "
            f"Render the DOT file to a PNG image using the create_image function. "
            f"Save the DOT code to SharedMemory with the key 'graphviz_ui_wireframe' and the PNG image path to SharedMemory with the key 'image_ui_wireframe'."
        ),
        agent=design_agent,
        expected_output=(
            f"Complete Graphviz DOT code illustrating the user interface wireframe, saved in '{output_base_dir}/3_design/UI_Wireframe.dot' and SharedMemory with the key 'graphviz_ui_wireframe'. "
            f"The PNG image rendered from DOT, saved in '{output_base_dir}/3_design/UI_Wireframe.png' and SharedMemory with the key 'image_ui_wireframe'. "
            f"The diagram is clear, with at least 4 interface components and navigation flow."
        ),
        context=[
            {
                "description": "Information from functional_requirements",
                "expected_output": "Summary of functional requirements to identify interface layout.",
                "input": global_context["functional_requirements"]
            }
        ],
        callback=lambda output: (
            shared_memory.save("graphviz_ui_wireframe", output) and
            (open(os.path.join(output_base_dir, "3_design", "UI_Wireframe.dot"), "w", encoding="utf-8").write(output), True)[-1] and
            shared_memory.save("image_ui_wireframe", create_image(Digraph(body=output.split('\n')[1:-1]), os.path.join(output_base_dir, "4_design", "UI_Wireframe")))
        )
    ))

    return tasks
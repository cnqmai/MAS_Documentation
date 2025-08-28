import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx, create_xlsx, create_image, create_md
import json 

# --- Adjusted Callback Functions ---
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
            print(f"❌ Lỗi: Không thể tạo DOCX '{filename}'.")
            return False
    return callback

def make_docx_xlsx_callback(title, docx_filename, xlsx_filename, shared_memory, save_key):
    def callback(output_from_agent_object): 
        print(f"🚀 Bắt đầu tạo DOCX và XLSX cho: {title}...")
        try:
            raw_output_json_string = (
                getattr(output_from_agent_object, "result", None)
                or getattr(output_from_agent_object, "response", None)
                or getattr(output_from_agent_object, "final_output", None)
                or str(output_from_agent_object)
            )
            raw_output_json_string = str(raw_output_json_string)
            if not raw_output_json_string.strip():
                print(f"⚠️ Agent không trả về dữ liệu JSON cho task '{title}'.")
                return False
            parsed_output = json.loads(raw_output_json_string)
            docx_content_raw = parsed_output.get("docx_content", "")
            xlsx_data_raw = parsed_output.get("xlsx_data", [])
            docx_paragraphs = docx_content_raw.split('\n')
            docx_path = create_docx(title, docx_paragraphs, docx_filename)
            xlsx_path = create_xlsx(xlsx_data_raw, xlsx_filename)
            shared_memory.save(save_key, raw_output_json_string)
            if docx_path and xlsx_path:
                print(f"✅ DOCX '{docx_filename}' và XLSX '{xlsx_filename}' đã được tạo và lưu thành công.")
                return True
            else:
                print(f"❌ Lỗi khi tạo file DOCX hoặc XLSX cho task '{title}'.")
                return False
        except json.JSONDecodeError as e:
            print(f"❌ Lỗi JSON: Không thể phân tích nội dung agent cho '{title}': {e}")
            print(f"🪵 Output nhận được: {raw_output_json_string[:500]}...")
            return False
        except Exception as e:
            print(f"❌ Lỗi không xác định khi xử lý callback cho '{title}': {e}")
            return False
    return callback

# --- Main Task Creation Function ---
def create_initiation_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, initiation_agent):
    tasks = []
    os.makedirs(f"{output_base_dir}/0_initiation", exist_ok=True)

    global_context = {
        "system_request_summary": shared_memory.load("system_request_summary"),
        "business_case": shared_memory.load("business_case"),
        "project_charter": shared_memory.load("project_charter"),
        "project_team_definition": shared_memory.load("project_team_definition")
    }

    # Task 1: Project Initiation Agenda
    tasks.append(Task(
        description=(
            f"Below is the system_request_summary information:\n\n"
            f"{global_context['system_request_summary']}\n\n"
            "Use the above data to write the 'Project Initiation Agenda' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: meeting topics, initiator, meeting time, attendee list, required reading, discussion topics, presenters, attachments. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=initiation_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'system_request_summary'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided system requirements information",
            "expected_output": "Summary of the system to be built (objectives, users, features...)",
            "input": global_context["system_request_summary"]
        }],
        callback=make_docx_callback(
            "Project Initiation Agenda",
            f"{output_base_dir}/0_initiation/Project_Initiation_Agenda.docx",
            shared_memory,
            "project_initiation_agenda"
        )
    ))

    # Task 2: Project Charter
    tasks.append(Task(
        description=(
            f"Below is the system_request_summary information:\n\n"
            f"{global_context['system_request_summary']}\n\n"
            "Use the above data to write the 'Project Charter' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: opportunity statement, objectives, project scope, in-scope and out-of-scope processes, project team, stakeholders, timeline, estimated cost. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=initiation_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'system_request_summary'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided system requirements information",
            "expected_output": "Summary of the system to be built (objectives, users, features...)",
            "input": global_context["system_request_summary"]
        }],
        callback=make_docx_callback(
            "Project Charter",
            f"{output_base_dir}/0_initiation/Project_Charter.docx",
            shared_memory,
            "project_charter"
        )
    ))

    # Task 3: Business Case Document
    tasks.append(Task(
        description=(
            f"Below is the system_request_summary information:\n\n"
            f"{global_context['system_request_summary']}\n\n"
            "Use the above data to write the 'Business Case Document' with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: need description, problems, solutions; quantitative and qualitative benefits; risks; requirements; costs; schedule; quality; recommendations and alternatives; stakeholder approvals. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=initiation_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'system_request_summary'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided system requirements information",
            "expected_output": "Summary of the system to be built (objectives, users, features...)",
            "input": global_context["system_request_summary"]
        }],
        callback=make_docx_callback(
            "Business Case Document",
            f"{output_base_dir}/0_initiation/Business_Case_Document.docx",
            shared_memory,
            "business_case"
        )
    ))

    # Task 4: Feasibility Study
    tasks.append(Task(
        description=(
            f"Below is the system_request_summary information:\n\n"
            f"{global_context['system_request_summary']}\n\n"
            "Use the above data to write the 'Feasibility Study' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: introduction, objectives, scope; current system; operating environment; user organization; final product; solutions and alternatives; approvals; technical, financial, organizational, legal feasibility analysis; feasibility risks. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=initiation_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'system_request_summary'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided system requirements information",
            "expected_output": "Summary of the system to be built (objectives, users, features...)",
            "input": global_context["system_request_summary"]
        }],
        callback=make_docx_callback(
            "Feasibility Study",
            f"{output_base_dir}/0_initiation/Feasibility_Study.docx",
            shared_memory,
            "feasibility_study"
        )
    ))

    # Task 5: Value Proposition Template
    tasks.append(Task(
        description=(
            f"Below is the system_request_summary information:\n\n"
            f"{global_context['system_request_summary']}\n\n"
            "Use the above data to write the 'Value Proposition Template' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: proposed product/service, project description, target market, needs and pain points, required features, benefits, make or buy decision. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=initiation_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'system_request_summary'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided system requirements information",
            "expected_output": "Summary of the system to be built (objectives, users, features...)",
            "input": global_context["system_request_summary"]
        }],
        callback=make_docx_callback(
            "Value Proposition Template",
            f"{output_base_dir}/0_initiation/Value_Proposition_Template.docx",
            shared_memory,
            "value_proposition"
        )
    ))

    # Task 6: Project or Issue Submission Form
    tasks.append(Task(
        description=(
            f"Below is the system_request_summary information:\n\n"
            f"{global_context['system_request_summary']}\n\n"
            "Use the above data to write the 'Project or Issue Submission Form' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: issue description, priority, impact, proposed actions. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=initiation_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'system_request_summary'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided system requirements information",
            "expected_output": "Summary of the system to be built (objectives, users, features...)",
            "input": global_context["system_request_summary"]
        }],
        callback=make_docx_callback(
            "Project or Issue Submission Form",
            f"{output_base_dir}/0_initiation/Project_or_Issue_Submission_Form.docx",
            shared_memory,
            "submission_form"
        )
    ))

    # Task 7: Project Cost - Benefit Analysis
    tasks.append(Task(
        description=(
            f"Below is the system_request_summary information:\n\n"
            f"{global_context['system_request_summary']}\n\n"
            f"Below is the business case information (if any):\n\n"
            f"{global_context['business_case']}\n\n"
            "Use the above data to write the 'Project Cost - Benefit Analysis' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: general information (project name, sponsor, objectives, benefits), recommendations and alternatives, costs and resources, schedule, risks, risk analysis. "
            "Return a JSON string containing both the DOCX content (under 'docx_content') and the XLSX data (under 'xlsx_data'). "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=initiation_agent,
        expected_output=(
            "A valid JSON string containing two fields: "
            "'docx_content' is the content of the cost-benefit analysis document (structured, clear, all sections filled, no blanks or placeholders), "
            "'xlsx_data' is the spreadsheet data detailing cost/benefit items. "
            "docx_content can be in Markdown or plain text."
        ),
        context=[
            {
                "description": "User-provided system requirements information",
                "expected_output": "Summary of the system to be built (objectives, users, features...)",
                "input": global_context["system_request_summary"]
            },
            {
                "description": "User-provided business case information",
                "expected_output": "User-provided business case information",
                "input": global_context["business_case"]
            }
        ],
        callback=make_docx_xlsx_callback(
            "Project Cost - Benefit Analysis",
            f"{output_base_dir}/0_initiation/Project_Cost_Benefit_Analysis.docx",
            f"{output_base_dir}/0_initiation/Project_Cost_Benefit_Analysis.xlsx",
            shared_memory,
            "cost_benefit_analysis"
        )
    ))

    # Task 8: Project Team Definition
    tasks.append(Task(
        description=(
            f"Below is the project charter (project_charter) information:\n\n"
            f"{global_context['project_charter']}\n\n"
            "Use the above data to write the 'Project Team Definition' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: meeting overview, stakeholder and project member identification, milestone schedule, responsibilities, organization structure, member list, roles and responsibilities, skill requirements. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=initiation_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_charter'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided project charter information",
            "expected_output": "Summary of project team, members, roles, responsibilities, skills...",
            "input": global_context["project_charter"]
        }],
        callback=make_docx_callback(
            "Project Team Definition",
            f"{output_base_dir}/0_initiation/Project_Team_Definition.docx",
            shared_memory,
            "project_team_definition"
        )
    ))

    # Task 9: Stakeholder Identification List
    tasks.append(Task(
        description=(
            f"Below is the project charter (project_charter) information:\n\n"
            f"{global_context['project_charter']}\n\n"
            "Use the above data to write the 'Stakeholder Identification List' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: stakeholder list, asset list, risk list. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=initiation_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_charter'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided project charter information",
            "expected_output": "Summary of stakeholders, assets, project risks",
            "input": global_context["project_charter"]
        }],
        callback=make_docx_callback(
            "Stakeholder Identification List",
            f"{output_base_dir}/0_initiation/Stakeholder_Identification_List.docx",
            shared_memory,
            "identification_list"
        )
    ))

    # Task 10: Project Resource Plan
    tasks.append(Task(
        description=(
            f"Below is the project charter (project_charter) information:\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Below is the project team definition (project_team_definition) information:\n\n"
            f"{global_context['project_team_definition']}\n\n"
            "Use the above data to write the 'Project Resource Plan' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: project team size, required resources/skills, personnel sources, quantity, facility needs, resource profiles, team organization, assumptions, risks and mitigation, stakeholder approvals. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=initiation_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_charter' and 'project_team_definition'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided project charter information",
                "expected_output": "Summary of resources, team organization, assumptions, risks...",
                "input": global_context["project_charter"]
            },
            {
                "description": "User-provided project team definition information",
                "expected_output": "Summary of members, skills, personnel, team organization...",
                "input": global_context["project_team_definition"]
            }
        ],
        callback=make_docx_callback(
            "Project Resource Plan",
            f"{output_base_dir}/0_initiation/Project_Resource_Plan.docx",
            shared_memory,
            "project_resource_plan"
        )
    ))

    # Task 11: Concept Of Operations
    tasks.append(Task(
        description=(
            f"Below is the project charter (project_charter) information:\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Below is the business case (business_case) information:\n\n"
            f"{global_context['business_case']}\n\n"
            "Use the above data to write the 'Concept Of Operations' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: capability needs, operations and support description, basis for change, potential impacts, operational scenarios, functional features, summary and analysis of proposed system, operational processes, roles and responsibilities, operational risks. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=initiation_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_charter' and 'business_case'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided project charter information",
                "expected_output": "Summary of operations, roles, processes, risks...",
                "input": global_context["project_charter"]
            },
            {
                "description": "User-provided business case information",
                "expected_output": "Summary of objectives, benefits, impacts, risks...",
                "input": global_context["business_case"]
            }
        ],
        callback=make_docx_callback(
            "Concept Of Operations",
            f"{output_base_dir}/0_initiation/Concept_Of_Operations.docx",
            shared_memory,
            "concept_of_operations"
        )
    ))

    # Task 12: Initiate Project Checklist
    tasks.append(Task(
        description=(
            f"Below is the project charter (project_charter) information:\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Below is the business case (business_case) information:\n\n"
            f"{global_context['business_case']}\n\n"
            "Use the above data to write the 'Initiate Project Checklist' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: project objectives, system development lifecycle, checklist for each item, task list, completion status, responsible person, notes. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=project_manager_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_charter' and 'business_case'. "
            "The document is not a template, does not contain placeholders or (), but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided project charter information",
                "expected_output": "Summary of objectives, lifecycle, responsibilities, tasks...",
                "input": global_context["project_charter"]
            },
            {
                "description": "User-provided business case information",
                "expected_output": "Summary of objectives, benefits, risks, schedule...",
                "input": global_context["business_case"]
            }
        ],
        callback=make_docx_callback(
            "Initiate Project Checklist",
            f"{output_base_dir}/0_initiation/Initiate_Project_Checklist.docx",
            shared_memory,
            "initiate_project_checklist"
        )
    ))

    return tasks

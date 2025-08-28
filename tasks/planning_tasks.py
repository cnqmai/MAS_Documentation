import os
import json
from crewai import Task
from utils.output_formats import create_docx, create_xlsx, create_image
from memory.shared_memory import SharedMemory
from graphviz import Digraph

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

def create_planning_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, planning_agent):
    tasks = []
    os.makedirs(f"{output_base_dir}/1_planning", exist_ok=True)

    global_context = {
        "project_charter": shared_memory.load("project_charter"),
        "business_case": shared_memory.load("business_case"),
        "cost_benefit_analysis": shared_memory.load("cost_benefit_analysis"),
        "project_team_definition": shared_memory.load("project_team_definition"),
        "project_resource_plan": shared_memory.load("project_resource_plan"),
        "statement_of_work": shared_memory.load("statement_of_work"),
        "project_approval": shared_memory.load("project_approval"),
        "risk_data_collection": shared_memory.load("risk_data_collection"),
        "activity_worksheet": shared_memory.load("activity_worksheet"),
        "wbs": shared_memory.load("wbs"),
        "opportunities_summary": shared_memory.load("opportunities_summary"),
        "project_plan": shared_memory.load("project_plan"),
    }

    # PMO Checklist
    tasks.append(Task(
        description=(
            f"Below is the project_charter information:\n\n"
            f"{global_context['project_charter']}\n\n"
            "Use the above data to write a complete 'Project Management Office Checklist' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: objectives, audience, organizational responsibilities, PMO toolkit, required data, support interface. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_charter'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[{
            "description": "User-provided project_charter information",
            "expected_output": "Summary of objectives, roles, tools, PMO data...",
            "input": global_context["project_charter"]
        }],
        callback=make_docx_callback(
            "Project Management Office Checklist",
            f"{output_base_dir}/1_planning/PMO_Checklist.docx",
            shared_memory,
            "pmo_checklist"
        )
    ))

    # Statement of Work
    tasks.append(Task(
        description=(
            f"Below is the project_charter information:\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Below is the business_case information:\n\n"
            f"{global_context['business_case']}\n\n"
            "Use the above data to write a complete 'Statement of Work' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: business objectives, project description, schedule estimate, cost, resources, project control (risks, issues, changes). "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_charter' and 'business_case'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[
            {
                "description": "User-provided project_charter information",
                "expected_output": "Summary of scope, deliverables, schedule...",
                "input": global_context["project_charter"]
            },
            {
                "description": "User-provided business_case information",
                "expected_output": "Summary of business objectives, benefits, costs...",
                "input": global_context["business_case"]
            }
        ],
        callback=make_docx_callback(
            "Statement of Work",
            f"{output_base_dir}/1_planning/Statement_of_Work.docx",
            shared_memory,
            "statement_of_work"
        )
    ))

    # Project Approval Document
    tasks.append(Task(
        description=(
            f"Below is the project_charter information:\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Below is the business_case information:\n\n"
            f"{global_context['business_case']}\n\n"
            "Use the above data to write a complete 'Project Approval Document' with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: overview, project description, approval information (responsible person, signature, date). "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_charter' and 'business_case'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[
            {
                "description": "User-provided project_charter information",
                "expected_output": "Summary of project overview, scope, objectives...",
                "input": global_context["project_charter"]
            },
            {
                "description": "User-provided business_case information",
                "expected_output": "Summary of objectives, benefits, approval...",
                "input": global_context["business_case"]
            }
        ],
        callback=make_docx_callback(
            "Project Approval Document",
            f"{output_base_dir}/1_planning/Project_Approval_Document.docx",
            shared_memory,
            "project_approval"
        )
    ))

    # Cost Estimating Worksheet
    tasks.append(Task(
        description=(
            f"Below is the cost_benefit_analysis information:\n\n"
            f"{global_context['cost_benefit_analysis']}\n\n"
            "Use the above data to create a 'Cost Estimating Worksheet' spreadsheet with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: IT personnel, professional services, hardware, software, other costs, total cost, risk reserve."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete spreadsheet, fully filled out based on actual data in 'cost_benefit_analysis'. "
            "Not a template, no placeholders or brackets (). Ready to export to XLSX."
        ),
        context=[{
            "description": "User-provided cost_benefit_analysis information",
            "expected_output": "Summary of cost items, risk reserve...",
            "input": global_context["cost_benefit_analysis"]
        }],
        callback=make_docx_xlsx_callback(
            "Cost Estimating Worksheet",
            f"{output_base_dir}/1_planning/Cost_Estimating_Worksheet.docx",
            f"{output_base_dir}/1_planning/Cost_Estimating_Worksheet.xlsx",
            shared_memory,
            "cost_estimating_worksheet"
        )
    ))

    # Development Estimating Worksheet
    tasks.append(Task(
        description=(
            f"Below is the cost_benefit_analysis information:\n\n"
            f"{global_context['cost_benefit_analysis']}\n\n"
            "Use the above data to create a 'Development Estimating Worksheet' spreadsheet with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: prototyping, user interface, reports, database, integration, servers, total development cost, software, long-term support."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete spreadsheet, fully filled out based on actual data in 'cost_benefit_analysis'. "
            "Not a template, no placeholders or brackets (). Ready to export to XLSX."
        ),
        context=[{
            "description": "User-provided cost_benefit_analysis information",
            "expected_output": "Summary of development cost items...",
            "input": global_context["cost_benefit_analysis"]
        }],
        callback=make_docx_xlsx_callback(
            "Development Estimating Worksheet",
            f"{output_base_dir}/1_planning/Development_Estimating_Worksheet.docx",
            f"{output_base_dir}/1_planning/Development_Estimating_Worksheet.xlsx",
            shared_memory,
            "development_estimating_worksheet"
        )
    ))

    # Capital vs. Expense Costs
    tasks.append(Task(
        description=(
            f"Below is the cost_benefit_analysis information:\n\n"
            f"{global_context['cost_benefit_analysis']}\n\n"
            "Use the above data to create a 'Project Capital vs. Expense Costs' spreadsheet with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: hardware, software, services, migration, total capital and operating costs."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete spreadsheet, fully filled out based on actual data in 'cost_benefit_analysis'. "
            "Not a template, no placeholders or brackets (). Ready to export to XLSX."
        ),
        context=[{
            "description": "User-provided cost_benefit_analysis information",
            "expected_output": "Summary of capital and operating cost items...",
            "input": global_context["cost_benefit_analysis"]
        }],
        callback=make_docx_xlsx_callback(
            "Capital vs Operating Costs",
            f"{output_base_dir}/1_planning/Project_Capital_vs_Expense_Costs.docx",
            f"{output_base_dir}/1_planning/Project_Capital_vs_Expense_Costs.xlsx",
            shared_memory,
            "capital_vs_expense"
        )
    ))

    # Configuration Management Plan
    tasks.append(Task(
        description=(
            f"Below is the project_charter information:\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Below is the statement_of_work information:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            "Use the above data to write a complete 'Configuration Management Plan' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: user audience, configuration management organization, activities & responsibilities, configuration control board (CCB), configuration audit, plan approval."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_charter' and 'statement_of_work'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[
            {
                "description": "User-provided project_charter information",
                "expected_output": "Summary of organization, roles, responsibilities...",
                "input": global_context["project_charter"]
            },
            {
                "description": "User-provided statement_of_work information",
                "expected_output": "Summary of scope, activities, control...",
                "input": global_context["statement_of_work"]
            }
        ],
        callback=make_docx_callback(
            "Configuration Management Plan",
            f"{output_base_dir}/1_planning/Configuration_Management_Plan.docx",
            shared_memory,
            "config_management_plan"
        )
    ))

    # Risk Information Data Collection Form
    tasks.append(Task(
        description=(
            f"Below is the project_charter information:\n\n"
            f"{global_context['project_charter']}\n\n"
            "Use the above data to write a complete 'Risk Information Data Collection Form' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: risk identification, root cause analysis, risk assessment, review and response."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_charter'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[{
            "description": "User-provided project_charter information",
            "expected_output": "Summary of risks, causes, assessment...",
            "input": global_context["project_charter"]
        }],
        callback=make_docx_callback(
            "Risk Information Data Collection Form",
            f"{output_base_dir}/1_planning/Risk_Information_Data_Collection_Form.docx",
            shared_memory,
            "risk_data_collection"
        )
    ))

    # Risk Analysis Plan
    tasks.append(Task(
        description=(
            f"Below is the risk_data_collection information:\n\n"
            f"{global_context['risk_data_collection']}\n\n"
            "Use the above data to write a complete 'Risk Analysis Plan' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: project purpose, project information, risk analysis table (priority score, mitigation strategy, contingency plan)."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'risk_data_collection'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[{
            "description": "User-provided risk_data_collection information",
            "expected_output": "Summary of risks, analysis, strategies...",
            "input": global_context["risk_data_collection"]
        }],
        callback=make_docx_callback(
            "Risk Analysis Plan",
            f"{output_base_dir}/1_planning/Risk_Analysis_Plan.docx",
            shared_memory,
            "risk_analysis_plan"
        )
    ))

    # Procurement Plan
    tasks.append(Task(
        description=(
            f"Below is the project_resource_plan information:\n\n"
            f"{global_context['project_resource_plan']}\n\n"
            f"Below is the statement_of_work information:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            "Use the above data to write a complete 'Procurement Plan' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: introduction, objectives, procurement information (responsible person, items, risks, schedule), procurement strategy (pricing strategy, competitive method, budget limits)."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_resource_plan' and 'statement_of_work'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[
            {
                "description": "User-provided project_resource_plan information",
                "expected_output": "Summary of resources, materials, personnel...",
                "input": global_context["project_resource_plan"]
            },
            {
                "description": "User-provided statement_of_work information",
                "expected_output": "Summary of scope, objectives, schedule...",
                "input": global_context["statement_of_work"]
            }
        ],
        callback=make_docx_callback(
            "Procurement Plan",
            f"{output_base_dir}/1_planning/Procurement_Plan.docx",
            shared_memory,
            "procurement_plan"
        )
    ))

    # Project Organization Chart
    tasks.append(Task(
        description=(
            f"Below is the project_team_definition information:\n\n"
            f"{global_context['project_team_definition']}\n\n"
            "Use the above data to write a complete 'Project Organization Chart' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: organization chart, decision makers, support organization."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_team_definition'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[{
            "description": "User-provided project_team_definition information",
            "expected_output": "Summary of roles, organization, support...",
            "input": global_context["project_team_definition"]
        }],
        callback=make_docx_callback(
            "Project Organization Chart",
            f"{output_base_dir}/1_planning/Project_Organization_Chart.docx",
            shared_memory,
            "project_org_chart"
        )
    ))

    # Roles and Responsibilities Matrix
    tasks.append(Task(
        description=(
            f"Below is the project_team_definition information:\n\n"
            f"{global_context['project_team_definition']}\n\n"
            f"Below is the statement_of_work information:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            "Use the above data to write a complete 'Roles and Responsibilities Matrix' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: responsibility matrix setup, sample role and responsibility descriptions, standard matrix and RACI model matrix."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_team_definition' and 'statement_of_work'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[
            {
                "description": "User-provided project_team_definition information",
                "expected_output": "Summary of roles, responsibilities...",
                "input": global_context["project_team_definition"]
            },
            {
                "description": "User-provided statement_of_work information",
                "expected_output": "Summary of activities, responsibilities...",
                "input": global_context["statement_of_work"]
            }
        ],
        callback=make_docx_callback(
            "Roles and Responsibilities Matrix",
            f"{output_base_dir}/1_planning/Roles_and_Responsibilities_Matrix.docx",
            shared_memory,
            "roles_responsibilities_matrix"
        )
    ))

    # Required Approvals Matrix
    tasks.append(Task(
        description=(
            f"Below is the project_approval information:\n\n"
            f"{global_context['project_approval']}\n\n"
            "Use the above data to write a complete 'Required Approvals Matrix' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: project purpose, sample role and responsibility descriptions, approval matrix."
        ),
        agent=project_manager_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_approval'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[{
            "description": "User-provided project_approval information",
            "expected_output": "Summary of approvals, roles, responsibilities...",
            "input": global_context["project_approval"]
        }],
        callback=make_docx_callback(
            "Required Approvals Matrix",
            f"{output_base_dir}/1_planning/Required_Approvals_Matrix.docx",
            shared_memory,
            "required_approvals_matrix"
        )
    ))

    # Activity Worksheet in WBS Dictionary Form
    tasks.append(Task(
        description=(
            f"Below is the statement_of_work information:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            "Use the above data to write a complete 'Activity Worksheet in Work Breakdown Structure Dictionary Form' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: task number, description, specific activities, objectives, acceptance criteria, assumptions, skills, resources, materials, time estimate, cost, predecessor/successor dependencies, approval."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'statement_of_work'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[{
            "description": "User-provided statement_of_work information",
            "expected_output": "Summary of tasks, objectives, skills...",
            "input": global_context["statement_of_work"]
        }],
        callback=make_docx_callback(
            "Activity Worksheet in WBS Dictionary Form",
            f"{output_base_dir}/1_planning/Activity_Worksheet_WBS_Dictionary.docx",
            shared_memory,
            "activity_worksheet"
        )
    ))

    # WBS Resource Planning Template
    tasks.append(Task(
        description=(
            f"Below is the project_resource_plan information:\n\n"
            f"{global_context['project_resource_plan']}\n\n"
            f"Below is the activity_worksheet information:\n\n"
            f"{global_context['activity_worksheet']}\n\n"
            "Use the above data to write a complete 'Work Breakdown Structure Resource Planning Template' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: required skills, time estimate, resource allocation."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_resource_plan' and 'activity_worksheet'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[
            {
                "description": "User-provided project_resource_plan information",
                "expected_output": "Summary of resources, skills...",
                "input": global_context["project_resource_plan"]
            },
            {
                "description": "User-provided activity_worksheet information",
                "expected_output": "Summary of tasks, time...",
                "input": global_context["activity_worksheet"]
            }
        ],
        callback=make_docx_callback(
            "Work Breakdown Structure Resource Planning Template",
            f"{output_base_dir}/1_planning/WBS_Resource_Planning_Template.docx",
            shared_memory,
            "wbs_resource_planning"
        )
    ))

    # Work Breakdown Structure (WBS)
    tasks.append(Task(
        description=(
            f"Below is the activity_worksheet information:\n\n"
            f"{global_context['activity_worksheet']}\n\n"
            "Use the above data to write a complete 'Work Breakdown Structure (WBS)' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: project name, department, work code, description, responsible person/group, completion deadline."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'activity_worksheet'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[{
            "description": "User-provided activity_worksheet information",
            "expected_output": "Summary of work, code, responsible person...",
            "input": global_context["activity_worksheet"]
        }],
        callback=make_docx_callback(
            "Work Breakdown Structure",
            f"{output_base_dir}/1_planning/Work_Breakdown_Structure.docx",
            shared_memory,
            "wbs"
        )
    ))

    # COBIT Checklist and Review
    tasks.append(Task(
        description=(
            f"Below is the project_charter information:\n\n"
            f"{global_context['project_charter']}\n\n"
            "Use the above data to write a complete 'COBIT Checklist and Review' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: COBIT control objectives, summary of COBIT components and processes, main groups (Plan, Implement, Support, Monitor)."
        ),
        agent=researcher_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_charter'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[{
            "description": "User-provided project_charter information",
            "expected_output": "Summary of controls, processes, COBIT groups...",
            "input": global_context["project_charter"]
        }],
        callback=make_docx_callback(
            "COBIT Checklist and Review",
            f"{output_base_dir}/1_planning/COBIT_Checklist_and_Review.docx",
            shared_memory,
            "cobit_checklist"
        )
    ))

    # Request For Information
    tasks.append(Task(
        description=(
            f"Below is the statement_of_work information:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            "Use the above data to write a complete 'Request For Information (RFI)' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: purpose, RFI process, company profile, product technical features, pricing and lifecycle cost information."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'statement_of_work'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[{
            "description": "User-provided statement_of_work information",
            "expected_output": "Summary of objectives, process, features...",
            "input": global_context["statement_of_work"]
        }],
        callback=make_docx_callback(
            "Request For Information",
            f"{output_base_dir}/1_planning/Request_For_Information.docx",
            shared_memory,
            "rfi"
        )
    ))

    # Root Cause Analysis
    tasks.append(Task(
        description=(
            f"Below is the risk_data_collection information:\n\n"
            f"{global_context['risk_data_collection']}\n\n"
            "Use the above data to write a complete 'Root Cause Analysis' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: summary, occurrence time, department, affected application, event sequence, recommended actions."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'risk_data_collection'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[{
            "description": "User-provided risk_data_collection information",
            "expected_output": "Summary of incident, cause, solution...",
            "input": global_context["risk_data_collection"]
        }],
        callback=make_docx_callback(
            "Root Cause Analysis",
            f"{output_base_dir}/1_planning/Root_Cause_Analysis.docx",
            shared_memory,
            "root_cause_analysis"
        )
    ))

    # Project Plan
    tasks.append(Task(
        description=(
            f"Below is the project_charter information:\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Below is the statement_of_work information:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            f"Below is the wbs information:\n\n"
            f"{global_context['wbs']}\n\n"
            "Use the above data to write a complete 'Project Plan' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: main deliverables, milestones, activities, resources, applied by SDLC phases."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'project_charter', 'statement_of_work', and 'wbs'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[
            {
                "description": "User-provided project_charter information",
                "expected_output": "Summary of objectives, resources...",
                "input": global_context["project_charter"]
            },
            {
                "description": "User-provided statement_of_work information",
                "expected_output": "Summary of deliverables, activities...",
                "input": global_context["statement_of_work"]
            },
            {
                "description": "User-provided wbs information",
                "expected_output": "Summary of work, schedule...",
                "input": global_context["wbs"]
            }
        ],
        callback=make_docx_callback(
            "Project Plan",
            f"{output_base_dir}/1_planning/Project_Plan.docx",
            shared_memory,
            "project_plan"
        )
    ))

    # List of Opportunities Summary
    tasks.append(Task(
        description=(
            f"Below is the business_case information:\n\n"
            f"{global_context['business_case']}\n\n"
            "Use the above data to write a complete 'List of Opportunities Summary' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, but provide actual content for each section: description, priority, delivery date, responsible person, notes."
        ),
        agent=planning_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'business_case'. "
            "Not a template, no placeholders or brackets (). Ready to export to DOCX."
        ),
        context=[{
            "description": "User-provided business_case information",
            "expected_output": "Summary of opportunities, priority, responsible person...",
            "input": global_context["business_case"]
        }],
        callback=make_docx_callback(
            "List of Opportunities Summary",
            f"{output_base_dir}/1_planning/List_of_Opportunities_Summary.docx",
            shared_memory,
            "opportunities_summary"
        )
    ))

    # New Task: WBS Diagram for Work Breakdown Structure (Graphviz)
    tasks.append(Task(
        description=(
            f"Based on the project_plan data:\n\n"
            f"project_plan:\n{global_context['project_plan'] or 'No data'}\n\n"
            f"Create a Work Breakdown Structure (WBS) diagram to illustrate the project's work packages, structured as a tree. "
            f"The diagram must include at least 3 levels (e.g., Project -> Phase -> Specific Task), with at least 4 work packages at the lowest level. "
            f"The result is a Graphviz DOT code for a directed graph (digraph), saved to 'WBS_Diagram.dot' in the '{output_base_dir}/1_planning' folder. "
            f"Render the DOT file as a PNG image using the create_image function. "
            f"Save the DOT code to SharedMemory with key 'graphviz_wbs_diagram' and the PNG image path to SharedMemory with key 'image_wbs_diagram'."
        ),
        agent=planning_agent, 
        expected_output=(
            f"Complete Graphviz DOT code illustrating the WBS diagram, saved in '{output_base_dir}/1_planning/WBS_Diagram.dot' and SharedMemory with key 'graphviz_wbs_diagram'. "
            f"PNG image rendered from DOT, saved in '{output_base_dir}/1_planning/WBS_Diagram.png' and SharedMemory with key 'image_wbs_diagram'. "
            f"The diagram is clear, with at least 3 levels and 4 work packages at the lowest level."
        ),
        context=[
            {
                "description": "Information from project_plan",
                "expected_output": "Summarize the project plan to identify work packages and hierarchy.",
                "input": global_context["project_plan"] or "No data"
            }
        ],
        callback=lambda output: (
            __import__('os').makedirs(os.path.join(output_base_dir, "1_planning"), exist_ok=True) or
            # Lấy nội dung chuỗi một cách an toàn
            (
                (lambda s: (
                    shared_memory.save("graphviz_wbs_diagram", s) and
                    open(os.path.join(output_base_dir, "1_planning", "WBS_Diagram.dot"), "w", encoding="utf-8").write(s) and
                    __import__('graphviz').Source(s).render(
                        filename=os.path.join(output_base_dir, "1_planning", "WBS_Diagram"),
                        format="png",
                        cleanup=True
                    ) and
                    shared_memory.save("image_wbs_diagram", os.path.join(output_base_dir, "1_planning", "WBS_Diagram.png"))
                ))(
                    # Thử lấy từ các thuộc tính khác nhau, nếu không có thì chuyển thành chuỗi
                    getattr(output, "response", None) or
                    getattr(output, "final_output", None) or
                    getattr(output, "result", None) or
                    str(output)
                )
            )
        )
    ))

    return tasks
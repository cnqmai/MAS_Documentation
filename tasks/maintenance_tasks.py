import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx
import json

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
def create_maintenance_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, maintenance_agent):
    tasks = []
    os.makedirs(f"{output_base_dir}/7_maintenance", exist_ok=True)

    global_context = {
        "test_summary_report": shared_memory.load("test_summary_report"),
        "project_status_report": shared_memory.load("project_status_report"),
        "operations_guide": shared_memory.load("operations_guide"),
        "system_admin_guide": shared_memory.load("system_admin_guide"),
        "lessons_learned": shared_memory.load("lessons_learned"),
        "requirements_changes_impact_analysis": shared_memory.load("requirements_changes_impact_analysis"),
        "bug_report": shared_memory.load("bug_report"),
        "security_architecture": shared_memory.load("security_architecture"),
        "project_acceptance": shared_memory.load("project_acceptance"),
        "non_functional_requirements": shared_memory.load("non_functional_requirements"),
        "transition_out_plan": shared_memory.load("transition_out_plan"),
        "sla_warranty_policies": shared_memory.load("sla_warranty_policies"),
        "source_code_documentation": shared_memory.load("source_code_documentation"),
        "middleware_documentation": shared_memory.load("middleware_documentation"),
        "monitoring_alerting_guide": shared_memory.load("monitoring_alerting_guide"),
        "sla_template": shared_memory.load("sla_template")
    }

    # Task 1: Lessons Learned
    tasks.append(Task(
        description=(
            f"Below is the test_summary_report data:\n\n"
            f"{global_context['test_summary_report']}\n\n"
            f"Below is the project_status_report data:\n\n"
            f"{global_context['project_status_report']}\n\n"
            "Use the above data to write a complete 'Lessons Learned' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: project closure discussion, participants, greatest success, lessons learned, areas (project initiation, planning, project management, personnel, communication, funding, cost, schedule, roles and responsibilities, risk management, procurement, requirements, scope, development, testing, training, documentation, approval). "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'test_summary_report' and 'project_status_report'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided test_summary_report information",
                "expected_output": "Summary of test report, greatest success...",
                "input": global_context["test_summary_report"]
            },
            {
                "description": "User-provided project_status_report information",
                "expected_output": "Summary of project status report, project closure discussion...",
                "input": global_context["project_status_report"]
            }
        ],
        callback=make_docx_callback(
            "Lessons Learned",
            f"{output_base_dir}/7_maintenance/Lessons_Learned.docx",
            shared_memory,
            "lessons_learned"
        )
    ))

    # Task 2: Transition Out Plan
    tasks.append(Task(
        description=(
            f"Below is the operations_guide data:\n\n"
            f"{global_context['operations_guide']}\n\n"
            f"Below is the system_admin_guide data:\n\n"
            f"{global_context['system_admin_guide']}\n\n"
            "Use the above data to write a complete 'Transition Out Plan' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: transition approach, transition objectives, transition team organization, transition tasks, knowledge transfer process, product rollout (rollout, data migration), communication plan, schedule and handover. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'operations_guide' and 'system_admin_guide'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided operations_guide information",
                "expected_output": "Summary of operations guide, transition approach...",
                "input": global_context["operations_guide"]
            },
            {
                "description": "User-provided system_admin_guide information",
                "expected_output": "Summary of system admin guide, transition team organization...",
                "input": global_context["system_admin_guide"]
            }
        ],
        callback=make_docx_callback(
            "Transition Out Plan",
            f"{output_base_dir}/7_maintenance/Transition_Out_Plan.docx",
            shared_memory,
            "transition_out_plan"
        )
    ))

    # Task 3: Post Project Survey Questionnaire
    tasks.append(Task(
        description=(
            f"Below is the lessons_learned data:\n\n"
            f"{global_context['lessons_learned']}\n\n"
            "Use the above data to write a complete 'Post Project Survey Questionnaire' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: general issues, project communication, planning and schedule, design and implementation, testing process, training and documentation, general process questions. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=project_manager_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'lessons_learned'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided lessons_learned information",
            "expected_output": "Summary of lessons learned, general issues...",
            "input": global_context["lessons_learned"]
        }],
        callback=make_docx_callback(
            "Post Project Survey Questionnaire",
            f"{output_base_dir}/7_maintenance/Post_Project_Survey_Questionnaire.docx",
            shared_memory,
            "post_project_survey"
        )
    ))

    # Task 4: Post Project Review
    tasks.append(Task(
        description=(
            f"Below is the lessons_learned data:\n\n"
            f"{global_context['lessons_learned']}\n\n"
            f"Below is the project_status_report data:\n\n"
            f"{global_context['project_status_report']}\n\n"
            "Use the above data to write a complete 'Post Project Review' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: general issues, project communication, schedule and timeline, design and implementation, testing, training, documentation, cost (budget and actual), approval. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=project_manager_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'lessons_learned' and 'project_status_report'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided lessons_learned information",
                "expected_output": "Summary of lessons learned, general issues...",
                "input": global_context["lessons_learned"]
            },
            {
                "description": "User-provided project_status_report information",
                "expected_output": "Summary of project status report, project communication...",
                "input": global_context["project_status_report"]
            }
        ],
        callback=make_docx_callback(
            "Post Project Review",
            f"{output_base_dir}/7_maintenance/Post_Project_Review.docx",
            shared_memory,
            "post_project_review"
        )
    ))

    # Task 5: Change Request Document (CCR)
    tasks.append(Task(
        description=(
            f"Below is the requirements_changes_impact_analysis data:\n\n"
            f"{global_context['requirements_changes_impact_analysis']}\n\n"
            f"Below is the bug_report data:\n\n"
            f"{global_context['bug_report']}\n\n"
            "Use the above data to write a complete 'Change Request Document (CCR)' with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: reason for change, description, assumptions, project impact, schedule impact, effort and cost estimation, capital/cost allocation table, approval. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'requirements_changes_impact_analysis' and 'bug_report'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided requirements_changes_impact_analysis information",
                "expected_output": "Summary of requirements change impact analysis, reason for change...",
                "input": global_context["requirements_changes_impact_analysis"]
            },
            {
                "description": "User-provided bug_report information",
                "expected_output": "Summary of bug report, change description...",
                "input": global_context["bug_report"]
            }
        ],
        callback=make_docx_callback(
            "Change Request Document",
            f"{output_base_dir}/7_maintenance/Change_Request_Document.docx",
            shared_memory,
            "change_request"
        )
    ))

    # Task 6: Disaster Recovery Plan
    tasks.append(Task(
        description=(
            f"Below is the security_architecture data:\n\n"
            f"{global_context['security_architecture']}\n\n"
            f"Below is the system_admin_guide data:\n\n"
            f"{global_context['system_admin_guide']}\n\n"
            "Use the above data to write a complete 'Disaster Recovery Plan' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: definition, objectives, scope, recovery team, recovery time and location, critical services, priority levels, response process (notification, assessment, handling), disaster declaration, recovery process, network/system/email/server recovery plan. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'security_architecture' and 'system_admin_guide'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided security_architecture information",
                "expected_output": "Summary of security architecture, recovery objectives...",
                "input": global_context["security_architecture"]
            },
            {
                "description": "User-provided system_admin_guide information",
                "expected_output": "Summary of system admin guide, recovery team...",
                "input": global_context["system_admin_guide"]
            }
        ],
        callback=make_docx_callback(
            "Disaster Recovery Plan",
            f"{output_base_dir}/7_maintenance/Disaster_Recovery_Plan.docx",
            shared_memory,
            "disaster_recovery_plan"
        )
    ))

    # Task 7: Certificate Of Compliance
    tasks.append(Task(
        description=(
            f"Below is the test_summary_report data:\n\n"
            f"{global_context['test_summary_report']}\n\n"
            f"Below is the project_acceptance data:\n\n"
            f"{global_context['project_acceptance']}\n\n"
            "Use the above data to write a complete 'Certificate Of Compliance' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: contractor section (order code, delivered product name), project management section (handover information), contract department (confirmation), signatures of contractor and project manager representatives. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'test_summary_report' and 'project_acceptance'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided test_summary_report information",
                "expected_output": "Summary of test report, handover information...",
                "input": global_context["test_summary_report"]
            },
            {
                "description": "User-provided project_acceptance information",
                "expected_output": "Summary of project acceptance document, order code...",
                "input": global_context["project_acceptance"]
            }
        ],
        callback=make_docx_callback(
            "Certificate Of Compliance",
            f"{output_base_dir}/7_maintenance/Certificate_Of_Compliance.docx",
            shared_memory,
            "certificate_of_compliance"
        )
    ))

    # Task 8: Request For Enhancement
    tasks.append(Task(
        description=(
            f"Below is the bug_report data:\n\n"
            f"{global_context['bug_report']}\n\n"
            f"Below is the non_functional_requirements data:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Use the above data to write a complete 'Request For Enhancement' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: requester information, request type (new, upgrade, minor edit), detailed description, priority, potential risks, funding source, related projects, attachments (if any). "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'bug_report' and 'non_functional_requirements'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided bug_report information",
                "expected_output": "Summary of bug report, requester information...",
                "input": global_context["bug_report"]
            },
            {
                "description": "User-provided non_functional_requirements information",
                "expected_output": "Summary of non-functional requirements, detailed enhancement description...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Request For Enhancement",
            f"{output_base_dir}/7_maintenance/Request_For_Enhancement.docx",
            shared_memory,
            "request_for_enhancement"
        )
    ))

    # Task 9: Product Retirement Plan
    tasks.append(Task(
        description=(
            f"Below is the lessons_learned data:\n\n"
            f"{global_context['lessons_learned']}\n\n"
            f"Below is the transition_out_plan data:\n\n"
            f"{global_context['transition_out_plan']}\n\n"
            "Use the above data to write a complete 'Product Retirement Plan' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: system/product information, reason for retirement, costs and benefits, assumptions, constraints, stakeholder list, risks, schedule. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'lessons_learned' and 'transition_out_plan'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided lessons_learned information",
                "expected_output": "Summary of lessons learned, system information...",
                "input": global_context["lessons_learned"]
            },
            {
                "description": "User-provided transition_out_plan information",
                "expected_output": "Summary of transition out plan, reason for retirement...",
                "input": global_context["transition_out_plan"]
            }
        ],
        callback=make_docx_callback(
            "Product Retirement Plan",
            f"{output_base_dir}/7_maintenance/Product_Retirement_Plan.docx",
            shared_memory,
            "product_retirement_plan"
        )
    ))

    # Task 10: Global Application Support Summary
    tasks.append(Task(
        description=(
            f"Below is the operations_guide data:\n\n"
            f"{global_context['operations_guide']}\n\n"
            f"Below is the sla_warranty_policies data:\n\n"
            f"{global_context['sla_warranty_policies']}\n\n"
            "Use the above data to write a complete 'Global Application Support Summary' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: application data, design, development and integration, production support, infrastructure, security, information filling instructions. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'operations_guide' and 'sla_warranty_policies'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided operations_guide information",
                "expected_output": "Summary of operations guide, application data...",
                "input": global_context["operations_guide"]
            },
            {
                "description": "User-provided sla_warranty_policies information",
                "expected_output": "Summary of SLA and warranty policies, production support...",
                "input": global_context["sla_warranty_policies"]
            }
        ],
        callback=make_docx_callback(
            "Global Application Support Summary",
            f"{output_base_dir}/7_maintenance/Global_Application_Support_Summary.docx",
            shared_memory,
            "global_support_summary"
        )
    ))

    # Task 11: Developer Knowledge Transfer Report
    tasks.append(Task(
        description=(
            f"Below is the source_code_documentation data:\n\n"
            f"{global_context['source_code_documentation']}\n\n"
            f"Below is the middleware_documentation data:\n\n"
            f"{global_context['middleware_documentation']}\n\n"
            "Use the above data to write a complete 'Developer Knowledge Transfer Report' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: reference documents, key personnel (users, experts, developers), technical knowledge (languages, tools, DBMS, OS), business knowledge, application knowledge (functions, process flows, client/server, usage environment). "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'source_code_documentation' and 'middleware_documentation'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided source_code_documentation information",
                "expected_output": "Summary of source code documentation, reference documents...",
                "input": global_context["source_code_documentation"]
            },
            {
                "description": "User-provided middleware_documentation information",
                "expected_output": "Summary of middleware documentation, key personnel...",
                "input": global_context["middleware_documentation"]
            }
        ],
        callback=make_docx_callback(
            "Developer Knowledge Transfer Report",
            f"{output_base_dir}/7_maintenance/Developer_Knowledge_Transfer_Report.docx",
            shared_memory,
            "knowledge_transfer_report"
        )
    ))

    # Task 12: Maintenance Checklist
    tasks.append(Task(
        description=(
            f"Below is the operations_guide data:\n\n"
            f"{global_context['operations_guide']}\n\n"
            f"Below is the system_admin_guide data:\n\n"
            f"{global_context['system_admin_guide']}\n\n"
            "Use the above data to write a complete 'Maintenance Checklist' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: maintenance task list, frequency, responsible person, tools used, performance check, security check, backup and recovery. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'operations_guide' and 'system_admin_guide'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided operations_guide information",
                "expected_output": "Summary of operations guide, maintenance tasks...",
                "input": global_context["operations_guide"]
            },
            {
                "description": "User-provided system_admin_guide information",
                "expected_output": "Summary of system admin guide, frequency...",
                "input": global_context["system_admin_guide"]
            }
        ],
        callback=make_docx_callback(
            "Maintenance Checklist",
            f"{output_base_dir}/7_maintenance/Maintenance_Checklist.docx",
            shared_memory,
            "maintenance_checklist"
        )
    ))

    # Task 13: Issue Reporting Template
    tasks.append(Task(
        description=(
            f"Below is the bug_report data:\n\n"
            f"{global_context['bug_report']}\n\n"
            "Use the above data to write a complete 'Issue Reporting Template' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: issue description, location, severity, status, priority, environment, detection method, responsible person. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'bug_report'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided bug_report information",
            "expected_output": "Summary of bug report, issue description...",
            "input": global_context["bug_report"]
        }],
        callback=make_docx_callback(
            "Issue Reporting Template",
            f"{output_base_dir}/7_maintenance/Issue_Reporting_Template.docx",
            shared_memory,
            "issue_reporting_template"
        )
    ))

    # Task 14: SLA and Warranty Policies
    tasks.append(Task(
        description=(
            f"Below is the sla_template data:\n\n"
            f"{global_context['sla_template']}\n\n"
            f"Below is the non_functional_requirements data:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Use the above data to write a complete 'SLA and Warranty Policies' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: purpose, scope, SLA terms, warranty policies, response time, resolution time, responsibilities, service request process. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'sla_template' and 'non_functional_requirements'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided sla_template information",
                "expected_output": "Summary of SLA template, purpose and SLA terms...",
                "input": global_context["sla_template"]
            },
            {
                "description": "User-provided non_functional_requirements information",
                "expected_output": "Summary of non-functional requirements, response time...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "SLA and Warranty Policies",
            f"{output_base_dir}/7_maintenance/SLA_and_Warranty_Policies.docx",
            shared_memory,
            "sla_warranty_policies"
        )
    ))

    # Task 15: Security Patch Management Guide
    tasks.append(Task(
        description=(
            f"Below is the security_architecture data:\n\n"
            f"{global_context['security_architecture']}\n\n"
            f"Below is the system_admin_guide data:\n\n"
            f"{global_context['system_admin_guide']}\n\n"
            "Use the above data to write a complete 'Security Patch Management Guide' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: purpose, patch management process, tools used, patch schedule, patch testing, rollback process, patch management reporting. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'security_architecture' and 'system_admin_guide'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided security_architecture information",
                "expected_output": "Summary of security architecture, patch management purpose...",
                "input": global_context["security_architecture"]
            },
            {
                "description": "User-provided system_admin_guide information",
                "expected_output": "Summary of system admin guide, patch management process...",
                "input": global_context["system_admin_guide"]
            }
        ],
        callback=make_docx_callback(
            "Security Patch Management Guide",
            f"{output_base_dir}/7_maintenance/Security_Patch_Management_Guide.docx",
            shared_memory,
            "security_patch_management"
        )
    ))

    # Task 16: Usage Analytics Report
    tasks.append(Task(
        description=(
            f"Below is the monitoring_alerting_guide data:\n\n"
            f"{global_context['monitoring_alerting_guide']}\n\n"
            "Use the above data to write a complete 'Usage Analytics Report' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: usage overview, performance metrics, usage trends, detected issues, improvement recommendations, detailed report. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'monitoring_alerting_guide'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided monitoring_alerting_guide information",
            "expected_output": "Summary of monitoring and alerting guide, usage overview...",
            "input": global_context["monitoring_alerting_guide"]
        }],
        callback=make_docx_callback(
            "Usage Analytics Report",
            f"{output_base_dir}/7_maintenance/Usage_Analytics_Report.docx",
            shared_memory,
            "usage_analytics_report"
        )
    ))

    # Task 17: Maintenance and Support Plan
    tasks.append(Task(
        description=(
            f"Below is the operations_guide data:\n\n"
            f"{global_context['operations_guide']}\n\n"
            f"Below is the sla_warranty_policies data:\n\n"
            f"{global_context['sla_warranty_policies']}\n\n"
            "Use the above data to write a complete 'Maintenance and Support Plan' document with specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: purpose, scope, maintenance plan, support plan, maintenance schedule, responsibilities, incident handling process, maintenance reporting. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=maintenance_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'operations_guide' and 'sla_warranty_policies'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content."
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided operations_guide information",
                "expected_output": "Summary of operations guide, maintenance plan...",
                "input": global_context["operations_guide"]
            },
            {
                "description": "User-provided sla_warranty_policies information",
                "expected_output": "Summary of SLA and warranty policies, support plan...",
                "input": global_context["sla_warranty_policies"]
            }
        ],
        callback=make_docx_callback(
            "Maintenance and Support Plan",
            f"{output_base_dir}/7_maintenance/Maintenance_and_Support_Plan.docx",
            shared_memory,
            "maintenance_support_plan"
        )
    ))

    return tasks
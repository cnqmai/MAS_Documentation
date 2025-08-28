import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx, create_xlsx, create_image
from graphviz import Digraph
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

# --- XLSX Callback Function ---
def make_docx_xlsx_callback(title, filename, shared_memory, save_key, content_type="docx"):
    def callback(output_from_agent_object):
        print(f"Starting {content_type.upper()} creation for: {title}...")
        content_raw = (
            getattr(output_from_agent_object, "result", None)
            or getattr(output_from_agent_object, "response", None)
            or getattr(output_from_agent_object, "final_output", None)
            or output_from_agent_object
        )
        content_raw_string = str(content_raw)
        if not content_raw_string.strip():
            print(f"⚠️  Note: Agent did not return content for task '{title}'.")
            return False
        success = False
        if content_type == "xlsx":
            try:
                content_data = json.loads(content_raw_string)
                file_path = create_xlsx(content_data, filename)
                shared_memory.save(save_key, content_raw_string)
                success = bool(file_path)
            except json.JSONDecodeError:
                print(f"❌ Error: Unable to parse JSON for '{title}'.")
                return False
        else:
            content_paragraphs = content_raw_string.split('\n')
            file_path = create_docx(title, content_paragraphs, filename)
            shared_memory.save(save_key, content_raw_string)
            success = bool(file_path)
        if success:
            print(f"✅ {content_type.upper()} '{filename}' created successfully and saved to SharedMemory '{save_key}'.")
            return True
        else:
            print(f"❌ System error: Unable to create {content_type.upper()} '{filename}'.")
            return False
    return callback

# --- Main Task Creation Function ---
def create_testing_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, testing_agent):
    tasks = []
    os.makedirs(f"{output_base_dir}/5_testing", exist_ok=True)

    global_context = {
        "dev_standards": shared_memory.load("dev_standards"),
        "functional_requirements": shared_memory.load("functional_requirements"),
        "use_case_template": shared_memory.load("use_case_template"),
        "rtm": shared_memory.load("rtm"),
        "project_plan": shared_memory.load("project_plan"),
        "non_functional_requirements": shared_memory.load("non_functional_requirements"),
        "test_plan": shared_memory.load("test_plan"),
        "srs": shared_memory.load("srs"),
        "test_scenarios": shared_memory.load("test_scenarios"),
        "test_case_spec": shared_memory.load("test_case_spec"),
        "system_test_plan": shared_memory.load("system_test_plan"),
        "bug_report": shared_memory.load("bug_report"),
        "test_summary_report": shared_memory.load("test_summary_report"),
        "uat_plan": shared_memory.load("uat_plan"),
        "brd": shared_memory.load("brd"),
        "risk_analysis_plan": shared_memory.load("risk_analysis_plan"),
        "dev_progress_report": shared_memory.load("dev_progress_report")
    }

    # Task 1: Documentation Quality Assurance Checklist
    tasks.append(Task(
        description=(
            f"Below is the dev_standards data:\n\n"
            f"{global_context['dev_standards']}\n\n"
            "Use the above data to write the 'Documentation Quality Assurance Checklist' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: document properties, track changes, cover page, table of contents, header/footer, spelling and grammar, formatting and layout, abbreviations, appendix, contact information, cross-reference, footnotes, images, links, index, page breaks, process diagrams, tables. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=project_manager_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'dev_standards'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[{
            "description": "User-provided dev_standards information",
            "expected_output": "Summary of development standards, document requirements...",
            "input": global_context["dev_standards"]
        }],
        callback=make_docx_callback(
            "Documentation Quality Assurance Checklist",
            f"{output_base_dir}/5_testing/Documentation_QA_Checklist.docx",
            shared_memory,
            "doc_qa_checklist"
        )
    ))

    # Task 2: Building Test Scenarios
    tasks.append(Task(
        description=(
            f"Below is the functional_requirements data:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Below is the use_case_template data:\n\n"
            f"{global_context['use_case_template']}\n\n"
            "Use the above data to write the 'Building Test Scenarios' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: difference between test case and scenario, how to build good test scenarios, version code, build code, scenario ID, description, objectives, test data, revision date, tester, reviewer, test steps. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=testing_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'functional_requirements' and 'use_case_template'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided functional_requirements information",
                "expected_output": "Summary of functional requirements, test objectives...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "User-provided use_case_template information",
                "expected_output": "Summary of usage scenarios, test steps...",
                "input": global_context["use_case_template"]
            }
        ],
        callback=make_docx_callback(
            "Building Test Scenarios",
            f"{output_base_dir}/5_testing/Building_Test_Scenarios.docx",
            shared_memory,
            "test_scenarios"
        )
    ))

    # Task 3: Test Plan
    tasks.append(Task(
        description=(
            f"Below is the rtm data:\n\n"
            f"{global_context['rtm']}\n\n"
            f"Below is the project_plan data:\n\n"
            f"{global_context['project_plan']}\n\n"
            f"Below is the non_functional_requirements data:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Use the above data to write the 'Test Plan' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: description of testing methods, classification of tests (unit, integration, UAT,...), constraints, assumptions, issue reporting process, escalation process, quality metrics, test pause and resume criteria, approval. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=testing_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'rtm', 'project_plan', and 'non_functional_requirements'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided rtm information",
                "expected_output": "Summary of traceability matrix, testing methods...",
                "input": global_context["rtm"]
            },
            {
                "description": "User-provided project_plan information",
                "expected_output": "Summary of project plan, test classification...",
                "input": global_context["project_plan"]
            },
            {
                "description": "User-provided non_functional_requirements information",
                "expected_output": "Summary of non-functional requirements, quality metrics...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Test Plan",
            f"{output_base_dir}/5_testing/Test_Plan.docx",
            shared_memory,
            "test_plan"
        )
    ))

    # Task 4: System Quality Assurance Checklist
    tasks.append(Task(
        description=(
            f"Below is the test_plan data:\n\n"
            f"{global_context['test_plan']}\n\n"
            f"Below is the srs data:\n\n"
            f"{global_context['srs']}\n\n"
            "Use the above data to write the 'System Quality Assurance Checklist' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: project management (resources, processes, monitoring), software/hardware development methods, technical reviews, requirements information, design, source code, maintenance history, performance, third-party products/software/hardware, security, compatibility, virus-free. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=testing_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'test_plan' and 'srs'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided test_plan information",
                "expected_output": "Summary of test plan, project management...",
                "input": global_context["test_plan"]
            },
            {
                "description": "User-provided srs information",
                "expected_output": "Summary of system requirements, requirements information...",
                "input": global_context["srs"]
            }
        ],
        callback=make_docx_callback(
            "System Quality Assurance Checklist",
            f"{output_base_dir}/5_testing/System_QA_Checklist.docx",
            shared_memory,
            "system_qa_checklist"
        )
    ))

    # Task 5: System Test Plan
    tasks.append(Task(
        description=(
            f"Below is the test_plan data:\n\n"
            f"{global_context['test_plan']}\n\n"
            f"Below is the srs data:\n\n"
            f"{global_context['srs']}\n\n"
            "Use the above data to write the 'System Test Plan' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: test entry/exit criteria, test scope and types, risk analysis, test environment (hardware/software), test schedule, test matrix (conditions, risks, instructions). "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=testing_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'test_plan' and 'srs'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided test_plan information",
                "expected_output": "Summary of test plan, test objectives...",
                "input": global_context["test_plan"]
            },
            {
                "description": "User-provided srs information",
                "expected_output": "Summary of system requirements, test scope...",
                "input": global_context["srs"]
            }
        ],
        callback=make_docx_callback(
            "System Test Plan",
            f"{output_base_dir}/5_testing/System_Test_Plan.docx",
            shared_memory,
            "system_test_plan"
        )
    ))

    # Task 6: User Acceptance Test Plan (UAT)
    tasks.append(Task(
        description=(
            f"Below is the functional_requirements data:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Below is the brd data:\n\n"
            f"{global_context['brd']}\n\n"
            "Use the above data to write the 'User Acceptance Test Plan (UAT)' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: purpose, reference documents, test description, entry/exit criteria, scope, test items, risks, assumptions, constraints, test environment, functional testing, test schedule, roles and responsibilities. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=testing_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'functional_requirements' and 'brd'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided functional_requirements information",
                "expected_output": "Summary of functional requirements, test description...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "User-provided brd information",
                "expected_output": "Summary of business requirements, UAT purpose...",
                "input": global_context["brd"]
            }
        ],
        callback=make_docx_callback(
            "User Acceptance Test Plan (UAT)",
            f"{output_base_dir}/5_testing/User_Acceptance_Test_Plan.docx",
            shared_memory,
            "uat_plan"
        )
    ))

    # Task 7: Test Case Specification
    tasks.append(Task(
        description=(
            f"Below is the test_scenarios data:\n\n"
            f"{global_context['test_scenarios']}\n\n"
            f"Below is the rtm data:\n\n"
            f"{global_context['rtm']}\n\n"
            "Use the above data to write the 'Test Case Specification' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: test case ID, description, objectives, prerequisites, test data, steps, expected results, pass/fail status. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=testing_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'test_scenarios' and 'rtm'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided test_scenarios information",
                "expected_output": "Summary of test scenarios, test case IDs...",
                "input": global_context["test_scenarios"]
            },
            {
                "description": "User-provided rtm information",
                "expected_output": "Summary of traceability matrix, prerequisites...",
                "input": global_context["rtm"]
            }
        ],
        callback=make_docx_callback(
            "Test Case Specification",
            f"{output_base_dir}/5_testing/Test_Case_Specification.docx",
            shared_memory,
            "test_case_spec"
        )
    ))

    # Task 8: Testing Bug Report
    tasks.append(Task(
        description=(
            f"Below is the test_case_spec data:\n\n"
            f"{global_context['test_case_spec']}\n\n"
            f"Below is the system_test_plan data:\n\n"
            f"{global_context['system_test_plan']}\n\n"
            "Use the above data to write the 'Testing Bug Report' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: bug description, location, severity, status, priority, testing environment, method and responsible person. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=testing_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'test_case_spec' and 'system_test_plan'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided test_case_spec information",
                "expected_output": "Summary of test case specifications, bug descriptions...",
                "input": global_context["test_case_spec"]
            },
            {
                "description": "User-provided system_test_plan information",
                "expected_output": "Summary of system test plan, testing environment...",
                "input": global_context["system_test_plan"]
            }
        ],
        callback=make_docx_callback(
            "Testing Bug Report",
            f"{output_base_dir}/5_testing/Testing_Bug_Report.docx",
            shared_memory,
            "bug_report"
        )
    ))

    # Task 9: Testing Bug List
    tasks.append(Task(
        description=(
            f"Below is the bug_report data:\n\n"
            f"{global_context['bug_report']}\n\n"
            "Use the above data to write the 'Testing Bug List' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: discovery date, bug ID, test case ID, bug name and description, severity, status, tester, testing method. "
            "The document must be formatted as a table and ready to be exported to XLSX. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=testing_agent,
        expected_output=(
            "A complete table, fully filled out based on actual data in 'bug_report'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to XLSX."
        ),
        context=[{
            "description": "User-provided bug_report information",
            "expected_output": "Summary of bug reports, bug IDs, bug descriptions...",
            "input": global_context["bug_report"]
        }],
        callback=make_docx_xlsx_callback(
            "Testing Bug List",
            f"{output_base_dir}/5_testing/Testing_Bug_List.xlsx",
            shared_memory,
            "bug_list",
            content_type="xlsx"
        )
    ))

    # Task 10: Regression Testing Plan
    tasks.append(Task(
        description=(
            f"Below is the bug_report data:\n\n"
            f"{global_context['bug_report']}\n\n"
            f"Below is the rtm data:\n\n"
            f"{global_context['rtm']}\n\n"
            "Use the above data to write the 'Regression Testing Plan' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: definition and scope of regression testing, testing methods, types of tests, risks, assumptions, constraints, schedule (tasks, duration, start/end dates), instructions (test steps, expected results, pass/fail). "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=testing_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'bug_report' and 'rtm'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided bug_report information",
                "expected_output": "Summary of bug reports, regression testing definition...",
                "input": global_context["bug_report"]
            },
            {
                "description": "User-provided rtm information",
                "expected_output": "Summary of traceability matrix, test scope...",
                "input": global_context["rtm"]
            }
        ],
        callback=make_docx_callback(
            "Regression Testing Plan",
            f"{output_base_dir}/5_testing/Regression_Testing_Plan.docx",
            shared_memory,
            "regression_test_plan"
        )
    ))

    # Task 11: Project Acceptance Document
    tasks.append(Task(
        description=(
            f"Below is the test_summary_report data:\n\n"
            f"{global_context['test_summary_report']}\n\n"
            f"Below is the uat_plan data:\n\n"
            f"{global_context['uat_plan']}\n\n"
            "Use the above data to write the 'Project Acceptance Document' with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: project name and code, user department, sponsor, project manager, project description, acceptance statement, signature confirmation. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=testing_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'test_summary_report' and 'uat_plan'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided test_summary_report information",
                "expected_output": "Summary of test summary report, project description...",
                "input": global_context["test_summary_report"]
            },
            {
                "description": "User-provided uat_plan information",
                "expected_output": "Summary of UAT plan, sponsor, project manager...",
                "input": global_context["uat_plan"]
            }
        ],
        callback=make_docx_callback(
            "Project Acceptance Document",
            f"{output_base_dir}/5_testing/Project_Acceptance_Document.docx",
            shared_memory,
            "project_acceptance"
        )
    ))

    # Task 12: Test Summary Report
    tasks.append(Task(
        description=(
            f"Below is the bug_report data:\n\n"
            f"{global_context['bug_report']}\n\n"
            f"Below is the test_case_spec data:\n\n"
            f"{global_context['test_case_spec']}\n\n"
            "Use the above data to write the 'Test Summary Report' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: test overview, test results, number of test cases (pass/fail), list of major bugs, improvement recommendations, deployment readiness status. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=testing_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'bug_report' and 'test_case_spec'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided bug_report information",
                "expected_output": "Summary of bug reports, major bugs...",
                "input": global_context["bug_report"]
            },
            {
                "description": "User-provided test_case_spec information",
                "expected_output": "Summary of test case specifications, test results...",
                "input": global_context["test_case_spec"]
            }
        ],
        callback=make_docx_callback(
            "Test Summary Report",
            f"{output_base_dir}/5_testing/Test_Summary_Report.docx",
            shared_memory,
            "test_summary_report"
        )
    ))

    # Task 13: Risk Management Register
    tasks.append(Task(
        description=(
            f"Below is the risk_analysis_plan data:\n\n"
            f"{global_context['risk_analysis_plan']}\n\n"
            f"Below is the bug_report data:\n\n"
            f"{global_context['bug_report']}\n\n"
            "Use the above data to write the 'Risk Management Register' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: risk description, responsible person, report date, update date, impact level, probability, impact duration, response status, actions taken/planned, current risk status. "
            "The document must be formatted as a table and ready to be exported to XLSX. "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=testing_agent,
        expected_output=(
            "A complete table, fully filled out based on actual data in 'risk_analysis_plan' and 'bug_report'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to XLSX."
        ),
        context=[
            {
                "description": "User-provided risk_analysis_plan information",
                "expected_output": "Summary of risk analysis plan, risk descriptions...",
                "input": global_context["risk_analysis_plan"]
            },
            {
                "description": "User-provided bug_report information",
                "expected_output": "Summary of bug reports, impact levels...",
                "input": global_context["bug_report"]
            }
        ],
        callback=make_docx_xlsx_callback(
            "Risk Management Register",
            f"{output_base_dir}/5_testing/Risk_Management_Register.xlsx",
            shared_memory,
            "risk_management_register",
            content_type="xlsx"
        )
    ))

    # Task 14: Project Status Report
    tasks.append(Task(
        description=(
            f"Below is the test_summary_report data:\n\n"
            f"{global_context['test_summary_report']}\n\n"
            f"Below is the dev_progress_report data:\n\n"
            f"{global_context['dev_progress_report']}\n\n"
            "Use the above data to write the 'Project Status Report' document with complete and specific content, leaving no section blank. "
            "Do not create a template or instructions, provide actual content for each section: report distribution, project overview, administrative management, completed activities, issues or delays, issues to be addressed, planned activities for the next period, deliverables status, completion according to WBS, WBS tasks (completed, overdue, upcoming), changes (open/approved/rejected), issues (open/closed), risks (open/addressed). "
            "If data is missing, infer or make reasonable assumptions instead of leaving blank."
        ),
        agent=testing_agent,
        expected_output=(
            "A complete document, fully filled out based on actual data in 'test_summary_report' and 'dev_progress_report'. "
            "The document is not a template, does not contain placeholders or [], but is specific and clear content. "
            "Ready to be exported to DOCX."
        ),
        context=[
            {
                "description": "User-provided test_summary_report information",
                "expected_output": "Summary of test summary report, deliverables status...",
                "input": global_context["test_summary_report"]
            },
            {
                "description": "User-provided dev_progress_report information",
                "expected_output": "Summary of development progress report, completed activities...",
                "input": global_context["dev_progress_report"]
            }
        ],
        callback=make_docx_callback(
            "Project Status Report",
            f"{output_base_dir}/5_testing/Project_Status_Report.docx",
            shared_memory,
            "project_status_report"
        )
    ))


    # New Task: Testing Flow for Test Plan (Graphviz)
    tasks.append(Task(
        description=(
            f"Based on the test_plan data:\n\n"
            f"test_plan:\n{global_context['test_plan']}\n\n"
            f"Create a Testing Flow diagram for the Test Plan to illustrate the steps in the testing process (e.g., Planning, Test Case Design, Execution, Reporting). "
            f"The diagram must include at least 4 steps, with links showing the order of execution. "
            f"The result is Graphviz DOT code formatting a directed diagram (digraph), saved to 'Testing_Flow.dot' in the '{output_base_dir}/5_testing' directory. "
            f"Render the DOT file to a PNG image using the create_image function. "
            f"Save the DOT code to SharedMemory with the key 'graphviz_testing_flow' and the PNG image path to SharedMemory with the key 'image_testing_flow'."
        ),
        agent=testing_agent,
        expected_output=(
            f"Complete Graphviz DOT code illustrating the testing flow diagram, saved in '{output_base_dir}/5_testing/Testing_Flow.dot' and SharedMemory with the key 'graphviz_testing_flow'. "
            f"The PNG image rendered from DOT, saved in '{output_base_dir}/5_testing/Testing_Flow.png' and SharedMemory with the key 'image_testing_flow'. "
            f"The diagram is clear, has at least 4 steps and order links."
        ),
        context=[
            {
                "description": "Information from test_plan",
                "expected_output": "Summary of test plan information to determine steps.",
                "input": global_context["test_plan"]
            }
        ],
        callback=lambda output: (
            shared_memory.save("graphviz_testing_flow", output) and
            (open(os.path.join(output_base_dir, "5_testing", "Testing_Flow.dot"), "w", encoding="utf-8").write(output), True)[-1] and
            shared_memory.save("image_testing_flow", create_image(Digraph(body=output.split('\n')[1:-1]), os.path.join(output_base_dir, "5_testing", "Testing_Flow")))
        )
    ))

    return tasks
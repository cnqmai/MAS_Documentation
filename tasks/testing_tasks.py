# tasks/testing_tasks.py

import os
import logging
from crewai import Task
from utils.file_writer import write_output
from memory.shared_memory import shared_memory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_testing_tasks(qa_automation_engineer_agent, project_manager_agent, researcher_agent, output_base_dir):
    """
    Tạo các task liên quan đến giai đoạn Kiểm thử.
    Args:
        qa_automation_engineer_agent: Agent chính cho Testing.
        project_manager_agent, researcher_agent: Các agent chung.
        output_base_dir: Đường dẫn thư mục base.
    Returns:
        list: Danh sách các Task đã tạo.
    """
    srs_content = shared_memory.get("phase_2_requirements", "srs_document")
    system_design_doc_path = shared_memory.get("phase_3_design", "system_design_doc_path")

    testing_context = f"SRS Content: {srs_content[:500] if srs_content else 'N/A'}\n" \
                      f"System Design Document Path: {system_design_doc_path if system_design_doc_path else 'N/A'}"
    if not srs_content and not system_design_doc_path:
        logging.warning("Requirements and Design documents missing for testing tasks.")
        testing_context = "Không có tài liệu yêu cầu hoặc thiết kế nào được tìm thấy."


    # Tạo thư mục con cho Phase 5 Testing (nếu chưa có)
    phase_output_dir = os.path.join(output_base_dir, "5_testing")
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục đầu ra cho Phase 5: {phase_output_dir}")


    # Task: Test Plan Creation
    test_plan_task = Task(
        description=(
            f"Dựa trên các tài liệu yêu cầu và thiết kế, tạo Kế hoạch Kiểm thử (Test Plan) chi tiết. "
            f"Bao gồm mục tiêu kiểm thử, phạm vi, các loại kiểm thử, môi trường, tiêu chí pass/fail, và lịch trình.\n"
            f"--- Context: {testing_context}"
        ),
        expected_output="Tài liệu tiếng Việt 'Test_Plan.docx' đầy đủ và có cấu trúc.",
        agent=qa_automation_engineer_agent,
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Test Plan Task ---"),
            write_output(os.path.join(phase_output_dir, "Test_Plan.docx"), str(output)),
            shared_memory.set("phase_5_testing", "test_plan", str(output)),
            logging.info(f"Đã lưu Test_Plan.docx và cập nhật shared_memory.")
        )
    )

    # Task: Test Case Generation
    test_case_task = Task(
        description=(
            f"Từ Test Plan và các yêu cầu chức năng (SRS, Use Cases), phát triển các Test Cases chi tiết. "
            f"Mỗi Test Case bao gồm: ID, mô tả, điều kiện tiên quyết, các bước thực hiện, dữ liệu kiểm thử, và kết quả mong muốn.\n"
            f"--- Context: {testing_context}\n"
            f"--- Test Plan: {test_plan_task.output.raw_output if test_plan_task.output else 'Chưa có Test Plan.'}"
        ),
        expected_output="Tài liệu tiếng Việt 'Test_Cases.xlsx' (hoặc markdown) chứa danh sách các Test Case.",
        agent=qa_automation_engineer_agent,
        context=[test_plan_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Test Case Generation Task ---"),
            write_output(os.path.join(phase_output_dir, "Test_Cases.md"), str(output)), # Hoặc .xlsx
            shared_memory.set("phase_5_testing", "test_cases", str(output)),
            logging.info(f"Đã lưu Test_Cases.md và cập nhật shared_memory.")
        )
    )

    # Task: Test Execution and Report (Simulated)
    test_execution_task = Task(
        description=(
            f"Mô phỏng việc thực hiện các Test Cases đã tạo và ghi lại kết quả. "
            f"Tạo một báo cáo 'Test_Execution_Report.md' tóm tắt kết quả kiểm thử, "
            f"liệt kê các lỗi (defects) tìm thấy và trạng thái của các Test Case.\n"
            f"--- Test Cases: {test_case_task.output.raw_output if test_case_task.output else 'Chưa có Test Cases.'}"
        ),
        expected_output="Tài liệu tiếng Việt 'Test_Execution_Report.md' tóm tắt kết quả thực hiện kiểm thử.",
        agent=qa_automation_engineer_agent,
        context=[test_case_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Test Execution Task ---"),
            write_output(os.path.join(phase_output_dir, "Test_Execution_Report.md"), str(output)),
            shared_memory.set("phase_5_testing", "test_execution_report", str(output)),
            logging.info(f"Đã lưu Test_Execution_Report.md và cập nhật shared_memory.")
        )
    )

    # Task: Testing Quality Gate (Project Manager)
    testing_validation_task = Task(
        description=(
            f"Đánh giá kỹ lưỡng các tài liệu kiểm thử (Test Plan, Test Cases, Test Execution Report). "
            f"Kiểm tra tính đầy đủ của kiểm thử, mức độ bao phủ, và chất lượng tổng thể của hệ thống. "
            f"Tạo báo cáo 'Validation_Report_Phase_5.md' tóm tắt kết quả đánh giá, "
            f"liệt kê các điểm cần cải thiện nếu có và xác nhận hoàn thành giai đoạn."
        ),
        expected_output="Tài liệu tiếng Việt 'Validation_Report_Phase_5.md' tóm tắt kết quả đánh giá giai đoạn kiểm thử.",
        agent=project_manager_agent,
        context=[test_plan_task, test_case_task, test_execution_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Testing Validation Task ---"),
            write_output(os.path.join(phase_output_dir, "Validation_Report_Phase_5.md"), str(output)),
            shared_memory.set("phase_5_testing", "validation_report", str(output)),
            logging.info(f"Đã lưu Validation_Report_Phase_5.md và cập nhật shared_memory.")
        )
    )

    # Task: Research Testing Best Practices (Researcher)
    research_testing_best_practices = Task(
        description=(
            f"Nghiên cứu các phương pháp hay nhất (best practices) trong kiểm thử phần mềm "
            f"(ví dụ: TDD, BDD, automation testing, performance testing, security testing). "
            f"Tổng hợp kiến thức hỗ trợ các agent khác.\n"
            f"--- Test Plan: {test_plan_task.output.raw_output if test_plan_task.output else 'Chưa có Test Plan.'}"
        ),
        expected_output="Tài liệu tiếng Việt 'Testing_Research_Summary.md' tổng hợp các kiến thức nghiên cứu hữu ích.",
        agent=researcher_agent,
        context=[test_plan_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Research Testing Best Practices Task ---"),
            write_output(os.path.join(phase_output_dir, "Testing_Research_Summary.md"), str(output)),
            shared_memory.set("phase_5_testing", "research_summary", str(output)),
            logging.info(f"Đã lưu Testing_Research_Summary.md và cập nhật shared_memory.")
        )
    )

    return [
        test_plan_task,
        test_case_task,
        test_execution_task,
        testing_validation_task,
        research_testing_best_practices
    ]
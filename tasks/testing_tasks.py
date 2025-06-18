import os
import logging
import re # Added for potential regex in callbacks
from crewai import Task
from textwrap import dedent # Import dedent for cleaner multi-line strings
from utils.file_writer import write_output
from memory.shared_memory import shared_memory
from docx import Document
from docx.shared import Inches
import graphviz

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Đã đổi tên tham số đầu tiên từ qa_automation_engineer_agent thành testing_agent
def create_testing_tasks(testing_agent, project_manager_agent, researcher_agent, output_base_dir):
    """
    Tạo các task liên quan đến giai đoạn Kiểm thử.
    Args:
        testing_agent: Agent chính cho Testing.
        project_manager_agent, researcher_agent: Các agent chung.
        output_base_dir: Đường dẫn thư mục base.
    Returns:
        list: Danh sách các Task đã tạo.
    """
    # Fetching necessary inputs from shared_memory, mirroring the table's "Inputs"
    srs_content = shared_memory.get("phase_2_requirements", "srs_document") or "N/A" # F.R.D.docx implicitly included in SRS content
    use_case_diagram_path = shared_memory.get("phase_2_requirements", "use_case_diagram_path") or "N/A"
    project_plan_xml = "Project_Plan.xml (Mock Content)" # Placeholder, assuming it's available
    source_code_path = shared_memory.get("phase_4_development", "final_source_code_path") or "N/A"
    design_doc_path = shared_memory.get("phase_3_design", "high_level_design_path") or "N/A"

    phase_output_dir = os.path.join(output_base_dir, "5_testing")
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đảm bảo thư mục output cho Phase 5: Testing tồn tại tại: {phase_output_dir}")

    # Helper to read file content safely
    def read_file_content(file_path):
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logging.warning(f"Không thể đọc file {file_path}: {e}")
                return "N/A (Lỗi đọc file)"
        return "N/A (File không tồn tại)"

    # Context string for tasks to refer to
    testing_context_str = dedent(f"""
        Dựa trên các tài liệu đã có:
        - Yêu cầu phần mềm (SRS): {srs_content[:500]}... (hoặc từ file: {shared_memory.get("phase_2_requirements", "srs_document_path")})
        - Sơ đồ Use Case: {use_case_diagram_path}
        - Kế hoạch dự án (nếu có liên quan đến việc triển khai Test): {project_plan_xml}
        - Mã nguồn (để thực hiện kiểm thử): {source_code_path}
        - Tài liệu thiết kế (HLD/LLD): {design_doc_path}
        - Các kết quả từ giai đoạn Phát triển: {shared_memory.get("phase_4_development", "development_summary") or "Chưa có."}
    """)

    # --- 1. Task: QA Checklist Creation (testing_agent) ---
    def qa_checklist_callback(output):
        logging.info(f"--- Hoàn thành QA Checklist Creation Task ---")
        file_path = os.path.join(phase_output_dir, "QA_Checklist.md")
        write_output(file_path, str(output))
        shared_memory.set("phase_5_testing", "qa_checklist", file_path)
        logging.info(f"Đã lưu QA_Checklist.md và cập nhật shared_memory.")

    qa_checklist_task = Task(
        description=dedent(f"""
            Tạo một danh sách kiểm tra chất lượng (QA Checklist) chi tiết dựa trên Tài liệu Yêu cầu Phần mềm (SRS),
            tài liệu thiết kế, và các tiêu chuẩn ngành liên quan đến chất lượng phần mềm.
            Danh sách này sẽ được sử dụng để hướng dẫn toàn bộ quá trình kiểm thử.
            Hãy tập trung vào các khía cạnh: tính năng, hiệu năng, bảo mật, khả năng sử dụng, và khả năng tương thích.
            Đầu ra phải là một tài liệu Markdown rõ ràng, có cấu trúc tốt.
            {testing_context_str}
        """),
        expected_output="Một tài liệu Markdown tiếng Việt có cấu trúc tốt 'QA_Checklist.md' bao gồm các hạng mục kiểm tra chi tiết.",
        agent=testing_agent, # Sử dụng testing_agent
        callback=qa_checklist_callback
    )

    # --- 2. Task: Test Plan Document Creation (testing_agent) ---
    def test_plan_callback(output):
        logging.info(f"--- Hoàn thành Test Plan Document Creation Task ---")
        file_path = os.path.join(phase_output_dir, "Test_Plan.docx")
        # Extract text and DOT code
        dot_blocks = re.findall(r'```dot\s*([\s\S]*?)\s*```', output)
        text_content = re.sub(r'```dot\s*[\s\S]*?```', '', output).strip()

        doc = Document()
        doc.add_heading('Kế hoạch Kiểm thử (Test Plan)', level=1)
        doc.add_paragraph(text_content) # Add extracted text content

        if dot_blocks:
            dot_code = dot_blocks[0]
            graph_path = os.path.join(phase_output_dir, "Test_Strategy_Diagram")
            try:
                src = graphviz.Source(dot_code, format='png')
                src.render(graph_path, view=False, cleanup=True)
                doc.add_heading('Chiến lược Kiểm thử', level=2)
                doc.add_picture(graph_path + '.png', width=Inches(6))
                logging.info(f"Đã tạo và nhúng sơ đồ chiến lược kiểm thử.")
            except Exception as e:
                logging.error(f"Lỗi khi tạo sơ đồ DOT cho Test Plan: {e}")
                doc.add_paragraph(f"Không thể tạo sơ đồ chiến lược kiểm thử. Mã DOT: {dot_code}")

        doc.save(file_path)
        shared_memory.set("phase_5_testing", "test_plan_document", file_path)
        logging.info(f"Đã lưu Test_Plan.docx và cập nhật shared_memory.")


    test_plan_task = Task(
        description=dedent(f"""
            Xây dựng một Tài liệu Kế hoạch Kiểm thử (Test Plan Document) toàn diện, bao gồm:
            - Chiến lược kiểm thử: loại hình kiểm thử (functional, non-functional, security, performance), tiếp cận.
            - Phạm vi kiểm thử.
            - Môi trường kiểm thử.
            - Tiêu chí chấp nhận và kết thúc kiểm thử.
            - Lịch trình và tài nguyên.
            - Vẽ một sơ đồ DOT mô tả luồng/chiến lược kiểm thử chính.
            Sử dụng thông tin từ SRS, tài liệu thiết kế và QA Checklist.
            Đảm bảo output được định dạng tốt để ghi vào file .docx.
            {testing_context_str}
        """),
        expected_output="Một tài liệu Word tiếng Việt 'Test_Plan.docx' chứa kế hoạch kiểm thử chi tiết và một sơ đồ DOT cho chiến lược kiểm thử.",
        agent=testing_agent, # Sử dụng testing_agent
        callback=test_plan_callback
    )

    # --- 3. Task: Test Case Development (testing_agent) ---
    def test_case_callback(output):
        logging.info(f"--- Hoàn thành Test Case Development Task ---")
        file_path = os.path.join(phase_output_dir, "Test_Cases.xlsx")
        # Giả định output là nội dung CSV hoặc bảng markdown có thể chuyển đổi thành XLSX
        # Cho ví dụ này, chỉ lưu raw output hoặc yêu cầu agent tạo XLSX trực tiếp
        write_output(file_path, str(output)) # Cần một hàm xử lý để tạo XLSX thực tế
        shared_memory.set("phase_5_testing", "test_cases", file_path)
        logging.info(f"Đã lưu Test_Cases.xlsx và cập nhật shared_memory.")

    test_case_task = Task(
        description=dedent(f"""
            Phát triển các trường hợp kiểm thử (Test Cases) chi tiết dựa trên Tài liệu Yêu cầu Phần mềm (SRS),
            Tài liệu Thiết kế (HLD/LLD), và Kế hoạch Kiểm thử.
            Mỗi Test Case cần bao gồm: ID, Mô tả, Điều kiện tiên quyết, Các bước thực hiện, Kết quả mong đợi, Mức độ ưu tiên.
            Tạo các test case cho cả kiểm thử chức năng và phi chức năng.
            Cung cấp output dưới dạng bảng, có thể chuyển đổi thành file Excel.
            {testing_context_str}
            --- Test Plan Context: {read_file_content(shared_memory.get("phase_5_testing", "test_plan_document"))}
        """),
        expected_output="Một tài liệu tiếng Việt 'Test_Cases.xlsx' chứa danh sách các trường hợp kiểm thử chi tiết ở định dạng bảng (ví dụ: Markdown table có thể parse thành XLSX).",
        agent=testing_agent, # Sử dụng testing_agent
        context=[test_plan_task, qa_checklist_task],
        callback=test_case_callback
    )

    # --- 4. Task: Test Execution and Defect Reporting (testing_agent) ---
    def test_exec_callback(output):
        logging.info(f"--- Hoàn thành Test Execution and Defect Reporting Task ---")
        file_path = os.path.join(phase_output_dir, "Test_Execution_Report.md")
        write_output(file_path, str(output))
        shared_memory.set("phase_5_testing", "test_execution_report", file_path)
        logging.info(f"Đã lưu Test_Execution_Report.md và cập nhật shared_memory.")

    test_exec_task = Task(
        description=dedent(f"""
            Giả lập việc thực thi các trường hợp kiểm thử đã tạo và báo cáo kết quả.
            Xác định các lỗi (defects) nếu có và ghi lại chúng dưới dạng Báo cáo Lỗi (Defect Report)
            với các thông tin: ID lỗi, Mô tả, Các bước tái hiện, Mức độ ưu tiên, Mức độ nghiêm trọng, Trạng thái.
            Đưa ra một bản tóm tắt về tiến độ kiểm thử và tỷ lệ lỗi.
            Giả định bạn có thể truy cập và chạy mã nguồn để kiểm thử (trong môi trường ảo).
            {testing_context_str}
            --- Test Cases Context: {read_file_content(shared_memory.get("phase_5_testing", "test_cases"))}
            --- Source Code Context: {read_file_content(source_code_path)[:500]}
        """),
        expected_output="Một tài liệu Markdown tiếng Việt 'Test_Execution_Report.md' tóm tắt kết quả thực thi kiểm thử và danh sách các lỗi (nếu có).",
        agent=testing_agent, # Sử dụng testing_agent
        context=[test_case_task],
        callback=test_exec_callback
    )

    # --- 5. Task: Security and Performance Testing (testing_agent) ---
    def security_perf_test_callback(output):
        logging.info(f"--- Hoàn thành Security and Performance Testing Task ---")
        file_path = os.path.join(phase_output_dir, "Security_Performance_Test_Report.md")
        write_output(file_path, str(output))
        shared_memory.set("phase_5_testing", "security_performance_report", file_path)
        logging.info(f"Đã lưu Security_Performance_Test_Report.md và cập nhật shared_memory.")

    security_perf_test_task = Task(
        description=dedent(f"""
            Thực hiện đánh giá cơ bản về bảo mật (ví dụ: các lỗ hổng OWASP Top 10 phổ biến)
            và kiểm thử hiệu năng (ví dụ: tải, stress test) cho hệ thống.
            Giả lập các công cụ kiểm thử tự động và báo cáo các phát hiện quan trọng.
            Đầu ra là một báo cáo tóm tắt các kết quả này.
            {testing_context_str}
            --- Test Plan Context: {read_file_content(shared_memory.get("phase_5_testing", "test_plan_document"))}
        """),
        expected_output="Một tài liệu Markdown tiếng Việt 'Security_Performance_Test_Report.md' tóm tắt các phát hiện về bảo mật và hiệu năng.",
        agent=testing_agent, # Sử dụng testing_agent
        context=[test_plan_task],
        callback=security_perf_test_callback
    )

    # --- 6. Task: Quality Assurance Audit (Project Manager) ---
    def audit_callback(output):
        logging.info(f"--- Hoàn thành Quality Assurance Audit Task ---")
        file_path = os.path.join(phase_output_dir, "Quality_Assurance_Audit_Report.md")
        write_output(file_path, str(output))
        shared_memory.set("phase_5_testing", "qa_audit_report", file_path)
        logging.info(f"Đã lưu Quality_Assurance_Audit_Report.md và cập nhật shared_memory.")

    audit_task = Task(
        description=dedent(f"""
            Thực hiện một cuộc kiểm toán chất lượng (QA Audit) độc lập.
            Đánh giá toàn bộ quy trình kiểm thử, bao gồm kế hoạch kiểm thử, trường hợp kiểm thử,
            báo cáo thực thi và báo cáo lỗi, để đảm bảo chúng tuân thủ các tiêu chuẩn dự án và ngành.
            Xác định các điểm mạnh và các khu vực cần cải thiện trong quy trình QA.
            {testing_context_str}
            --- QA Checklist: {read_file_content(shared_memory.get("phase_5_testing", "qa_checklist"))}
            --- Test Plan: {read_file_content(shared_memory.get("phase_5_testing", "test_plan_document"))}
            --- Test Execution Report: {read_file_content(shared_memory.get("phase_5_testing", "test_execution_report"))}
        """),
        expected_output="Một tài liệu Markdown tiếng Việt 'Quality_Assurance_Audit_Report.md' báo cáo kết quả kiểm toán QA.",
        agent=project_manager_agent, # Task này do Project Manager thực hiện
        context=[qa_checklist_task, test_plan_task, test_exec_task],
        callback=audit_callback
    )

    # --- 7. Task: Test Management Reporting (Project Manager) ---
    def test_management_callback(output):
        logging.info(f"--- Hoàn thành Test Management Reporting Task ---")
        file_path = os.path.join(phase_output_dir, "Test_Management_Report.docx")
        # Assuming the output is primarily text for a DOCX
        doc = Document()
        doc.add_heading('Báo cáo Quản lý Kiểm thử', level=1)
        doc.add_paragraph(output)
        doc.save(file_path)
        shared_memory.set("phase_5_testing", "test_management_report", file_path)
        logging.info(f"Đã lưu Test_Management_Report.docx và cập nhật shared_memory.")

    test_management_task = Task(
        description=dedent(f"""
            Tổng hợp tất cả các báo cáo kiểm thử (Test Execution Report, Security/Performance Report, QA Audit Report)
            thành một báo cáo quản lý tổng thể cho Project Manager.
            Báo cáo này cần cung cấp cái nhìn tổng quan về tình trạng chất lượng sản phẩm, các rủi ro còn tồn đọng,
            và khuyến nghị để đưa ra quyết định "Go/No-Go" cho giai đoạn tiếp theo.
            {testing_context_str}
            --- All Test Reports:
            - Test Execution: {read_file_content(shared_memory.get("phase_5_testing", "test_execution_report"))}
            - Security/Performance: {read_file_content(shared_memory.get("phase_5_testing", "security_performance_report"))}
            - QA Audit: {read_file_content(shared_memory.get("phase_5_testing", "qa_audit_report"))}
        """),
        expected_output="Một tài liệu Word tiếng Việt 'Test_Management_Report.docx' tóm tắt toàn bộ tình hình kiểm thử và đề xuất quyết định.",
        agent=project_manager_agent, # Task này do Project Manager thực hiện
        context=[test_exec_task, security_perf_test_task, audit_task],
        callback=test_management_callback
    )

    # --- 8. Task: Quality Gate Review (Project Manager) ---
    def quality_gate_callback(output):
        logging.info(f"--- Hoàn thành Quality Gate Review Task for Testing ---")
        file_path = os.path.join(phase_output_dir, "Validation_Report_Phase_5.md")
        write_output(file_path, str(output))
        shared_memory.set("phase_5_testing", "validation_report_path", file_path)
        logging.info(f"Đã lưu Validation_Report_Phase_5.md và cập nhật shared_memory.")

    # Quality Gate Task for Phase 5 (Testing)
    quality_gate_testing_task = Task(
        description=dedent(f"""
            Thực hiện Quality Gate cuối cùng cho giai đoạn Kiểm thử.
            Bạn, với vai trò Project Manager, hãy đánh giá kỹ lưỡng Tài liệu Kế hoạch Kiểm thử, các trường hợp kiểm thử,
            báo cáo thực thi kiểm thử, báo cáo bảo mật/hiệu năng, và báo cáo kiểm toán QA.
            Kiểm tra tính đầy đủ, chính xác, nhất quán và tuân thủ các tiêu chuẩn chất lượng.
            Xác nhận giai đoạn Kiểm thử có đủ điều kiện để chuyển tiếp sang giai đoạn Triển khai và Giao nộp hay không.
            {testing_context_str}
            --- Deliverables to Validate:
            - QA Checklist: {read_file_content(shared_memory.get("phase_5_testing", "qa_checklist"))}
            - Test Plan: {read_file_content(shared_memory.get("phase_5_testing", "test_plan_document"))}
            - Test Cases: {read_file_content(shared_memory.get("phase_5_testing", "test_cases"))}
            - Test Execution Report: {read_file_content(shared_memory.get("phase_5_testing", "test_execution_report"))}
            - Security/Performance Report: {read_file_content(shared_memory.get("phase_5_testing", "security_performance_report"))}
            - QA Audit Report: {read_file_content(shared_memory.get("phase_5_testing", "qa_audit_report"))}
            - Test Management Report: {read_file_content(shared_memory.get("phase_5_testing", "test_management_report"))}
        """),
        expected_output="Một tài liệu Markdown tiếng Việt 'Validation_Report_Phase_5.md' nêu rõ kết quả kiểm tra Quality Gate, lý do và các đề xuất cải thiện.",
        agent=project_manager_agent,
        context=[qa_checklist_task, test_plan_task, test_case_task, test_exec_task,
                 security_perf_test_task, audit_task, test_management_task],
        callback=quality_gate_callback
    )

    # --- 9. Task: Research Testing Best Practices (Researcher) ---
    def research_testing_best_practices_callback(output):
        logging.info(f"--- Hoàn thành Research Testing Best Practices Task ---")
        write_output(os.path.join(phase_output_dir, "Testing_Research_Summary.md"), str(output))
        shared_memory.set("phase_5_testing", "research_summary", str(output))
        logging.info(f"Đã lưu Testing_Research_Summary.md và cập nhật shared_memory.")

    research_testing_best_practices = Task(
        description=dedent(f"""
            Nghiên cứu các phương pháp hay nhất (best practices) trong kiểm thử phần mềm
            (ví dụ: TDD, BDD, automation testing, performance testing, security testing, interoperability testing, COBIT audit practices).
            Tổng hợp kiến thức hỗ trợ các agent khác.
            --- Context: {testing_context_str}
        """),
        expected_output="Tài liệu tiếng Việt 'Testing_Research_Summary.md' tổng hợp các kiến thức nghiên cứu hữu ích.",
        agent=researcher_agent,
        context=[
            test_plan_task,
            test_case_task,
            security_perf_test_task,
            audit_task
        ], # Context from relevant tasks
        callback=research_testing_best_practices_callback
    )

    return [
        qa_checklist_task,
        test_plan_task,
        test_case_task,
        test_exec_task,
        security_perf_test_task,
        test_management_task,
        audit_task,
        quality_gate_testing_task,
        research_testing_best_practices
    ]
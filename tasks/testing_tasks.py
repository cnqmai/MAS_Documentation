import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx, create_xlsx
import json

# --- Hàm Callback cho DOCX ---
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

# --- Hàm Callback cho XLSX ---
def make_docx_xlsx_callback(title, filename, shared_memory, save_key, content_type="docx"):
    def callback(output_from_agent_object):
        print(f"Bắt đầu tạo {content_type.upper()} cho: {title}...")
        content_raw = (
            getattr(output_from_agent_object, "result", None)
            or getattr(output_from_agent_object, "response", None)
            or getattr(output_from_agent_object, "final_output", None)
            or output_from_agent_object
        )
        content_raw_string = str(content_raw)
        if not content_raw_string.strip():
            print(f"⚠️  Lưu ý: Agent không trả về nội dung cho task '{title}'.")
            return False
        success = False
        if content_type == "xlsx":
            try:
                content_data = json.loads(content_raw_string)
                file_path = create_xlsx(content_data, filename)
                shared_memory.save(save_key, content_raw_string)
                success = bool(file_path)
            except json.JSONDecodeError:
                print(f"❌ Lỗi: Không thể phân tích JSON cho '{title}'.")
                return False
        else:
            content_paragraphs = content_raw_string.split('\n')
            file_path = create_docx(title, content_paragraphs, filename)
            shared_memory.save(save_key, content_raw_string)
            success = bool(file_path)
        if success:
            print(f"✅ {content_type.upper()} '{filename}' đã tạo thành công và lưu vào SharedMemory '{save_key}'.")
            return True
        else:
            print(f"❌ Lỗi hệ thống: Không thể tạo {content_type.upper()} '{filename}'.")
            return False
    return callback

# --- Hàm tạo Task chính ---
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
            f"Dưới đây là dữ liệu dev_standards:\n\n"
            f"{global_context['dev_standards']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách kiểm tra đảm bảo chất lượng tài liệu' (Documentation Quality Assurance Checklist) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: thuộc tính tài liệu, track changes, trang bìa, mục lục, header/footer, chính tả và ngữ pháp, định dạng và bố cục, từ viết tắt, phụ lục, thông tin liên hệ, cross-reference, chú thích, hình ảnh, liên kết, chỉ mục, ngắt trang, sơ đồ quy trình, bảng biểu. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'dev_standards'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả dev_standards từ người dùng",
            "expected_output": "Tóm tắt tiêu chuẩn phát triển, yêu cầu tài liệu...",
            "input": global_context["dev_standards"]
        }],
        callback=make_docx_callback(
            "Danh sách kiểm tra đảm bảo chất lượng tài liệu",
            f"{output_base_dir}/5_testing/Documentation_QA_Checklist.docx",
            shared_memory,
            "doc_qa_checklist"
        )
    ))

    # Task 2: Building Test Scenarios
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Dưới đây là dữ liệu use_case_template:\n\n"
            f"{global_context['use_case_template']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Xây dựng kịch bản kiểm thử' (Building Test Scenarios) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: phân biệt test case và scenario, cách xây dựng test scenario tốt, mã phiên bản, mã build, ID kịch bản, mô tả, mục tiêu, dữ liệu thử nghiệm, ngày sửa đổi, người kiểm thử, người duyệt, các bước kiểm thử. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=testing_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'functional_requirements' và 'use_case_template'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu chức năng, mục tiêu kiểm thử...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Thông tin mô tả use_case_template từ người dùng",
                "expected_output": "Tóm tắt kịch bản sử dụng, các bước kiểm thử...",
                "input": global_context["use_case_template"]
            }
        ],
        callback=make_docx_callback(
            "Xây dựng kịch bản kiểm thử",
            f"{output_base_dir}/5_testing/Building_Test_Scenarios.docx",
            shared_memory,
            "test_scenarios"
        )
    ))

    # Task 3: Test Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu rtm:\n\n"
            f"{global_context['rtm']}\n\n"
            f"Dưới đây là dữ liệu project_plan:\n\n"
            f"{global_context['project_plan']}\n\n"
            f"Dưới đây là dữ liệu non_functional_requirements:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch kiểm thử' (Test Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mô tả phương pháp kiểm thử, phân loại kiểm thử (đơn vị, tích hợp, UAT,...), các ràng buộc, giả định, quy trình thông báo, leo thang vấn đề, các thước đo chất lượng, tiêu chí tạm dừng và khôi phục kiểm thử, phê duyệt. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=testing_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'rtm', 'project_plan', và 'non_functional_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả rtm từ người dùng",
                "expected_output": "Tóm tắt ma trận truy xuất nguồn gốc, phương pháp kiểm thử...",
                "input": global_context["rtm"]
            },
            {
                "description": "Thông tin mô tả project_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch dự án, phân loại kiểm thử...",
                "input": global_context["project_plan"]
            },
            {
                "description": "Thông tin mô tả non_functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu phi chức năng, thước đo chất lượng...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch kiểm thử",
            f"{output_base_dir}/5_testing/Test_Plan.docx",
            shared_memory,
            "test_plan"
        )
    ))

    # Task 4: System Quality Assurance Checklist
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu test_plan:\n\n"
            f"{global_context['test_plan']}\n\n"
            f"Dưới đây là dữ liệu srs:\n\n"
            f"{global_context['srs']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách kiểm tra đảm bảo chất lượng hệ thống' (System Quality Assurance Checklist) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: quản lý dự án (nguồn lực, quy trình, giám sát), phương pháp phát triển phần mềm/phần cứng, rà soát kỹ thuật, thông tin yêu cầu, thiết kế, mã nguồn, lịch sử bảo trì, hiệu năng, sản phẩm/phần cứng/phần mềm mua ngoài, bảo mật, tương thích, sạch virus. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=testing_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'test_plan' và 'srs'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả test_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch kiểm thử, quản lý dự án...",
                "input": global_context["test_plan"]
            },
            {
                "description": "Thông tin mô tả srs từ người dùng",
                "expected_output": "Tóm tắt yêu cầu hệ thống, thông tin yêu cầu...",
                "input": global_context["srs"]
            }
        ],
        callback=make_docx_callback(
            "Danh sách kiểm tra đảm bảo chất lượng hệ thống",
            f"{output_base_dir}/5_testing/System_QA_Checklist.docx",
            shared_memory,
            "system_qa_checklist"
        )
    ))

    # Task 5: System Test Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu test_plan:\n\n"
            f"{global_context['test_plan']}\n\n"
            f"Dưới đây là dữ liệu srs:\n\n"
            f"{global_context['srs']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch kiểm thử hệ thống' (System Test Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục tiêu và tiêu chí vào/ra kiểm thử, phạm vi và loại kiểm thử, phân tích rủi ro, môi trường kiểm thử (phần cứng/phần mềm), lịch kiểm thử, ma trận kiểm thử (điều kiện, rủi ro, hướng dẫn). "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=testing_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'test_plan' và 'srs'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả test_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch kiểm thử, mục tiêu kiểm thử...",
                "input": global_context["test_plan"]
            },
            {
                "description": "Thông tin mô tả srs từ người dùng",
                "expected_output": "Tóm tắt yêu cầu hệ thống, phạm vi kiểm thử...",
                "input": global_context["srs"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch kiểm thử hệ thống",
            f"{output_base_dir}/5_testing/System_Test_Plan.docx",
            shared_memory,
            "system_test_plan"
        )
    ))

    # Task 6: User Acceptance Test Plan (UAT)
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Dưới đây là dữ liệu brd:\n\n"
            f"{global_context['brd']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch kiểm thử chấp nhận người dùng' (User Acceptance Test Plan - UAT) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục đích, tài liệu tham chiếu, mô tả kiểm thử, tiêu chí vào/ra, phạm vi, hạng mục kiểm thử, rủi ro, giả định, ràng buộc, môi trường kiểm thử, kiểm thử chức năng, lịch kiểm thử, vai trò và trách nhiệm. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=testing_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'functional_requirements' và 'brd'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu chức năng, mô tả kiểm thử...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Thông tin mô tả brd từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kinh doanh, mục đích UAT...",
                "input": global_context["brd"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch kiểm thử chấp nhận người dùng",
            f"{output_base_dir}/5_testing/User_Acceptance_Test_Plan.docx",
            shared_memory,
            "uat_plan"
        )
    ))

    # Task 7: Test Case Specification
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu test_scenarios:\n\n"
            f"{global_context['test_scenarios']}\n\n"
            f"Dưới đây là dữ liệu rtm:\n\n"
            f"{global_context['rtm']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Đặc tả trường hợp kiểm thử' (Test Case Specification) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: ID test case, mô tả, mục tiêu, điều kiện tiên quyết, dữ liệu kiểm thử, các bước thực hiện, kết quả mong đợi, trạng thái pass/fail. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=testing_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'test_scenarios' và 'rtm'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả test_scenarios từ người dùng",
                "expected_output": "Tóm tắt kịch bản kiểm thử, ID test case...",
                "input": global_context["test_scenarios"]
            },
            {
                "description": "Thông tin mô tả rtm từ người dùng",
                "expected_output": "Tóm tắt ma trận truy xuất nguồn gốc, điều kiện tiên quyết...",
                "input": global_context["rtm"]
            }
        ],
        callback=make_docx_callback(
            "Đặc tả trường hợp kiểm thử",
            f"{output_base_dir}/5_testing/Test_Case_Specification.docx",
            shared_memory,
            "test_case_spec"
        )
    ))

    # Task 8: Testing Bug Report
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu test_case_spec:\n\n"
            f"{global_context['test_case_spec']}\n\n"
            f"Dưới đây là dữ liệu system_test_plan:\n\n"
            f"{global_context['system_test_plan']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Báo cáo lỗi kiểm thử' (Testing Bug Report) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mô tả lỗi, vị trí xuất hiện, mức độ nghiêm trọng, trạng thái, mức ưu tiên, môi trường thử nghiệm, phương pháp và người phụ trách. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=testing_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'test_case_spec' và 'system_test_plan'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả test_case_spec từ người dùng",
                "expected_output": "Tóm tắt đặc tả trường hợp kiểm thử, mô tả lỗi...",
                "input": global_context["test_case_spec"]
            },
            {
                "description": "Thông tin mô tả system_test_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch kiểm thử hệ thống, môi trường thử nghiệm...",
                "input": global_context["system_test_plan"]
            }
        ],
        callback=make_docx_callback(
            "Báo cáo lỗi kiểm thử",
            f"{output_base_dir}/5_testing/Testing_Bug_Report.docx",
            shared_memory,
            "bug_report"
        )
    ))

    # Task 9: Testing Bug List
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu bug_report:\n\n"
            f"{global_context['bug_report']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách lỗi kiểm thử' (Testing Bug List) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: ngày phát hiện, ID lỗi, ID test case, tên và mô tả lỗi, mức độ nghiêm trọng, trạng thái, người kiểm thử, phương pháp thử nghiệm. "
            "Tài liệu phải được định dạng dưới dạng bảng và sẵn sàng để chuyển sang file XLSX. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=testing_agent,
        expected_output=(
            "Một bảng hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'bug_report'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file XLSX."
        ),
        context=[{
            "description": "Thông tin mô tả bug_report từ người dùng",
            "expected_output": "Tóm tắt báo cáo lỗi, ID lỗi, mô tả lỗi...",
            "input": global_context["bug_report"]
        }],
        callback=make_docx_xlsx_callback(
            "Danh sách lỗi kiểm thử",
            f"{output_base_dir}/5_testing/Testing_Bug_List.xlsx",
            shared_memory,
            "bug_list",
            content_type="xlsx"
        )
    ))

    # Task 10: Regression Testing Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu bug_report:\n\n"
            f"{global_context['bug_report']}\n\n"
            f"Dưới đây là dữ liệu rtm:\n\n"
            f"{global_context['rtm']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch kiểm thử hồi quy' (Regression Testing Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: định nghĩa và phạm vi kiểm thử hồi quy, phương pháp kiểm thử, loại kiểm thử, rủi ro, giả định, ràng buộc, lịch trình (công việc, số ngày, ngày bắt đầu/kết thúc), hướng dẫn (bước kiểm thử, kết quả mong đợi, pass/fail). "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=testing_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'bug_report' và 'rtm'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả bug_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo lỗi, định nghĩa kiểm thử hồi quy...",
                "input": global_context["bug_report"]
            },
            {
                "description": "Thông tin mô tả rtm từ người dùng",
                "expected_output": "Tóm tắt ma trận truy xuất nguồn gốc, phạm vi kiểm thử...",
                "input": global_context["rtm"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch kiểm thử hồi quy",
            f"{output_base_dir}/5_testing/Regression_Testing_Plan.docx",
            shared_memory,
            "regression_test_plan"
        )
    ))

    # Task 11: Project Acceptance Document
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu test_summary_report:\n\n"
            f"{global_context['test_summary_report']}\n\n"
            f"Dưới đây là dữ liệu uat_plan:\n\n"
            f"{global_context['uat_plan']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Văn bản nghiệm thu dự án' (Project Acceptance Document) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: tên và mã dự án, bộ phận sử dụng, người bảo trợ, quản lý dự án, mô tả dự án, tuyên bố chấp thuận, chữ ký xác nhận. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=testing_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'test_summary_report' và 'uat_plan'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả test_summary_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo kiểm thử, mô tả dự án...",
                "input": global_context["test_summary_report"]
            },
            {
                "description": "Thông tin mô tả uat_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch UAT, người bảo trợ, quản lý dự án...",
                "input": global_context["uat_plan"]
            }
        ],
        callback=make_docx_callback(
            "Văn bản nghiệm thu dự án",
            f"{output_base_dir}/5_testing/Project_Acceptance_Document.docx",
            shared_memory,
            "project_acceptance"
        )
    ))

    # Task 12: Test Summary Report
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu bug_report:\n\n"
            f"{global_context['bug_report']}\n\n"
            f"Dưới đây là dữ liệu test_case_spec:\n\n"
            f"{global_context['test_case_spec']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Báo cáo tóm tắt kiểm thử' (Test Summary Report) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: tổng quan kiểm thử, kết quả kiểm thử, số lượng test case (pass/fail), danh sách lỗi chính, khuyến nghị cải tiến, trạng thái sẵn sàng triển khai. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=testing_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'bug_report' và 'test_case_spec'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả bug_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo lỗi, danh sách lỗi chính...",
                "input": global_context["bug_report"]
            },
            {
                "description": "Thông tin mô tả test_case_spec từ người dùng",
                "expected_output": "Tóm tắt đặc tả trường hợp kiểm thử, kết quả kiểm thử...",
                "input": global_context["test_case_spec"]
            }
        ],
        callback=make_docx_callback(
            "Báo cáo tóm tắt kiểm thử",
            f"{output_base_dir}/5_testing/Test_Summary_Report.docx",
            shared_memory,
            "test_summary_report"
        )
    ))

    # Task 13: Risk Management Register
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu risk_analysis_plan:\n\n"
            f"{global_context['risk_analysis_plan']}\n\n"
            f"Dưới đây là dữ liệu bug_report:\n\n"
            f"{global_context['bug_report']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Sổ đăng ký quản lý rủi ro' (Risk Management Register) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mô tả rủi ro, người chịu trách nhiệm, ngày báo cáo, ngày cập nhật, mức độ ảnh hưởng, xác suất xảy ra, thời gian tác động, trạng thái phản hồi, hành động đã/thực hiện/đang lên kế hoạch, tình trạng rủi ro hiện tại. "
            "Tài liệu phải được định dạng dưới dạng bảng và sẵn sàng để chuyển sang file XLSX. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=testing_agent,
        expected_output=(
            "Một bảng hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'risk_analysis_plan' và 'bug_report'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file XLSX."
        ),
        context=[
            {
                "description": "Thông tin mô tả risk_analysis_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch phân tích rủi ro, mô tả rủi ro...",
                "input": global_context["risk_analysis_plan"]
            },
            {
                "description": "Thông tin mô tả bug_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo lỗi, mức độ ảnh hưởng...",
                "input": global_context["bug_report"]
            }
        ],
        callback=make_docx_xlsx_callback(
            "Sổ đăng ký quản lý rủi ro",
            f"{output_base_dir}/5_testing/Risk_Management_Register.xlsx",
            shared_memory,
            "risk_management_register",
            content_type="xlsx"
        )
    ))

    # Task 14: Project Status Report
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu test_summary_report:\n\n"
            f"{global_context['test_summary_report']}\n\n"
            f"Dưới đây là dữ liệu dev_progress_report:\n\n"
            f"{global_context['dev_progress_report']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Báo cáo tình trạng dự án' (Project Status Report) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: phân phối báo cáo, tổng quan dự án, quản trị hành chính, hoạt động đã thực hiện, vấn đề hoặc chậm trễ, vấn đề cần xử lý, hoạt động dự kiến kỳ tới, trạng thái deliverables, hoàn thành theo WBS, nhiệm vụ WBS (hoàn thành, quá hạn, sắp đến), thay đổi đang mở/đã duyệt/bị từ chối, vấn đề đang mở/đã đóng, rủi ro đang mở/đã xử lý. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=testing_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'test_summary_report' và 'dev_progress_report'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả test_summary_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo kiểm thử, trạng thái deliverables...",
                "input": global_context["test_summary_report"]
            },
            {
                "description": "Thông tin mô tả dev_progress_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo tiến độ phát triển, hoạt động đã thực hiện...",
                "input": global_context["dev_progress_report"]
            }
        ],
        callback=make_docx_callback(
            "Báo cáo tình trạng dự án",
            f"{output_base_dir}/5_testing/Project_Status_Report.docx",
            shared_memory,
            "project_status_report"
        )
    ))

    return tasks
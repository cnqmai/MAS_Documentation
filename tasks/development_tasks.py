import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx
import json

# --- Hàm Callback đã điều chỉnh ---
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

# --- Hàm tạo Task chính ---
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
            f"Dưới đây là dữ liệu technical_requirements:\n\n"
            f"{global_context['technical_requirements']}\n\n"
            f"Dưới đây là dữ liệu project_plan:\n\n"
            f"{global_context['project_plan']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Tiêu chuẩn phát triển' (Development Standards Document) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục đích, phạm vi, tiêu chuẩn mã hóa, công cụ phát triển, quy trình kiểm soát chất lượng, yêu cầu tài liệu, tiêu chuẩn hiệu suất và bảo mật. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=development_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'technical_requirements' và 'project_plan'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả technical_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kỹ thuật, tiêu chuẩn mã hóa, bảo mật...",
                "input": global_context["technical_requirements"]
            },
            {
                "description": "Thông tin mô tả project_plan từ người dùng",
                "expected_output": "Tóm tắt mục tiêu, quy trình kiểm soát chất lượng...",
                "input": global_context["project_plan"]
            }
        ],
        callback=make_docx_callback(
            "Tiêu chuẩn phát triển",
            f"{output_base_dir}/4_development/Development_Standards_Document.docx",
            shared_memory,
            "dev_standards"
        )
    ))

    # Task 2: Coding Guidelines
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu dev_standards:\n\n"
            f"{global_context['dev_standards']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Hướng dẫn mã hóa' (Coding Guidelines) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: phong cách mã hóa, quy ước đặt tên, cấu trúc mã, quản lý lỗi, bình luận mã, và các ví dụ minh họa. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=development_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'dev_standards'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả dev_standards từ người dùng",
            "expected_output": "Tóm tắt tiêu chuẩn mã hóa, quy ước đặt tên, bình luận mã...",
            "input": global_context["dev_standards"]
        }],
        callback=make_docx_callback(
            "Hướng dẫn mã hóa",
            f"{output_base_dir}/4_development/Coding_Guidelines.docx",
            shared_memory,
            "coding_guidelines"
        )
    ))

    # Task 3: Version Control Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu dev_standards:\n\n"
            f"{global_context['dev_standards']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch kiểm soát phiên bản' (Version Control Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục đích, công cụ kiểm soát phiên bản, quy trình branch và merge, quy tắc commit, quản lý tag và release, quy trình sao lưu. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=development_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'dev_standards'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả dev_standards từ người dùng",
            "expected_output": "Tóm tắt tiêu chuẩn phát triển, công cụ kiểm soát phiên bản...",
            "input": global_context["dev_standards"]
        }],
        callback=make_docx_callback(
            "Kế hoạch kiểm soát phiên bản",
            f"{output_base_dir}/4_development/Version_Control_Plan.docx",
            shared_memory,
            "version_control_plan"
        )
    ))

    # Task 4: Integration Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu system_architecture:\n\n"
            f"{global_context['system_architecture']}\n\n"
            f"Dưới đây là dữ liệu api_design:\n\n"
            f"{global_context['api_design']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch tích hợp' (Integration Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục đích, phạm vi, chiến lược tích hợp, lịch trình tích hợp, các thành phần tích hợp, yêu cầu môi trường, quy trình kiểm thử tích hợp. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=development_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'system_architecture' và 'api_design'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả system_architecture từ người dùng",
                "expected_output": "Tóm tắt kiến trúc hệ thống, thành phần tích hợp...",
                "input": global_context["system_architecture"]
            },
            {
                "description": "Thông tin mô tả api_design từ người dùng",
                "expected_output": "Tóm tắt thiết kế API, tích hợp API...",
                "input": global_context["api_design"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch tích hợp",
            f"{output_base_dir}/4_development/Integration_Plan.docx",
            shared_memory,
            "integration_plan"
        )
    ))

    # Task 5: Code Review Checklist
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu coding_guidelines:\n\n"
            f"{global_context['coding_guidelines']}\n\n"
            f"Dưới đây là dữ liệu technical_requirements:\n\n"
            f"{global_context['technical_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách kiểm tra đánh giá mã nguồn' (Code Review Checklist) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: cấu trúc mã, tài liệu, biến, kiểu dữ liệu, phong cách lập trình, cấu trúc điều khiển, vòng lặp, bảo trì, bảo mật, kiểm tra lỗi, xử lý ngoại lệ, thử nghiệm, xác thực. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'coding_guidelines' và 'technical_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả coding_guidelines từ người dùng",
                "expected_output": "Tóm tắt hướng dẫn mã hóa, phong cách lập trình...",
                "input": global_context["coding_guidelines"]
            },
            {
                "description": "Thông tin mô tả technical_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kỹ thuật, bảo mật, kiểm thử...",
                "input": global_context["technical_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Danh sách kiểm tra đánh giá mã nguồn",
            f"{output_base_dir}/4_development/Code_Review_Checklist.docx",
            shared_memory,
            "code_review_checklist"
        )
    ))

    # Task 6: Source Code Repository Checklist
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu version_control_plan:\n\n"
            f"{global_context['version_control_plan']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách kiểm tra kho mã nguồn' (Source Code Repository Checklist) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: cấu hình kho mã, quyền truy cập, cấu trúc thư mục, quy tắc commit, kiểm tra bảo mật, sao lưu, và giám sát kho. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=development_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'version_control_plan'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả version_control_plan từ người dùng",
            "expected_output": "Tóm tắt kế hoạch kiểm soát phiên bản, cấu hình kho mã...",
            "input": global_context["version_control_plan"]
        }],
        callback=make_docx_callback(
            "Danh sách kiểm tra kho mã nguồn",
            f"{output_base_dir}/4_development/Source_Code_Repository_Checklist.docx",
            shared_memory,
            "source_code_repo_checklist"
        )
    ))

    # Task 7: Development Progress Report
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu project_plan:\n\n"
            f"{global_context['project_plan']}\n\n"
            f"Dưới đây là dữ liệu wbs:\n\n"
            f"{global_context['wbs']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Báo cáo tiến độ phát triển' (Development Progress Report) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: tổng quan tiến độ, nhiệm vụ hoàn thành, nhiệm vụ đang thực hiện, rủi ro và vấn đề, kế hoạch tiếp theo. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=development_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_plan' và 'wbs'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project_plan từ người dùng",
                "expected_output": "Tóm tắt mục tiêu, tiến độ dự án...",
                "input": global_context["project_plan"]
            },
            {
                "description": "Thông tin mô tả wbs từ người dùng",
                "expected_output": "Tóm tắt cấu trúc công việc, nhiệm vụ hoàn thành...",
                "input": global_context["wbs"]
            }
        ],
        callback=make_docx_callback(
            "Báo cáo tiến độ phát triển",
            f"{output_base_dir}/4_development/Development_Progress_Report.docx",
            shared_memory,
            "dev_progress_report"
        )
    ))

    # Task 8: Build and Deployment Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu integration_plan:\n\n"
            f"{global_context['integration_plan']}\n\n"
            f"Dưới đây là dữ liệu system_architecture:\n\n"
            f"{global_context['system_architecture']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch xây dựng và triển khai' (Build and Deployment Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục đích, chiến lược xây dựng, công cụ xây dựng, quy trình triển khai, môi trường triển khai, kiểm thử sau triển khai, kế hoạch rollback. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=development_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'integration_plan' và 'system_architecture'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả integration_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch tích hợp, chiến lược xây dựng...",
                "input": global_context["integration_plan"]
            },
            {
                "description": "Thông tin mô tả system_architecture từ người dùng",
                "expected_output": "Tóm tắt kiến trúc hệ thống, công cụ CI/CD...",
                "input": global_context["system_architecture"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch xây dựng và triển khai",
            f"{output_base_dir}/4_development/Build_and_Deployment_Plan.docx",
            shared_memory,
            "build_deployment_plan"
        )
    ))

    # Task 9: Middleware Documentation
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu integration_plan:\n\n"
            f"{global_context['integration_plan']}\n\n"
            f"Dưới đây là dữ liệu api_design:\n\n"
            f"{global_context['api_design']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Tài liệu middleware' (Middleware Documentation) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: tổng quan middleware, các thành phần middleware, cấu hình, tích hợp API, hiệu suất và bảo mật, quy trình bảo trì. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=development_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'integration_plan' và 'api_design'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả integration_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch tích hợp, vai trò middleware...",
                "input": global_context["integration_plan"]
            },
            {
                "description": "Thông tin mô tả api_design từ người dùng",
                "expected_output": "Tóm tắt thiết kế API, tích hợp API...",
                "input": global_context["api_design"]
            }
        ],
        callback=make_docx_callback(
            "Tài liệu middleware",
            f"{output_base_dir}/4_development/Middleware_Documentation.docx",
            shared_memory,
            "middleware_documentation"
        )
    ))

    # Task 10: Source Code Documentation
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu lld:\n\n"
            f"{global_context['lld']}\n\n"
            f"Dưới đây là dữ liệu coding_guidelines:\n\n"
            f"{global_context['coding_guidelines']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Tài liệu mã nguồn' (Source Code Documentation) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: tổng quan mã nguồn, cấu trúc module, mô tả chức năng, bình luận mã, hướng dẫn sử dụng, các ví dụ mã. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=development_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'lld' và 'coding_guidelines'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả lld từ người dùng",
                "expected_output": "Tóm tắt thiết kế cấp thấp, cấu trúc module...",
                "input": global_context["lld"]
            },
            {
                "description": "Thông tin mô tả coding_guidelines từ người dùng",
                "expected_output": "Tóm tắt hướng dẫn mã hóa, bình luận mã...",
                "input": global_context["coding_guidelines"]
            }
        ],
        callback=make_docx_callback(
            "Tài liệu mã nguồn",
            f"{output_base_dir}/4_development/Source_Code_Documentation.docx",
            shared_memory,
            "source_code_documentation"
        )
    ))

    return tasks
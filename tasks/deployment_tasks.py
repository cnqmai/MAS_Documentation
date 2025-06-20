import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx
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

# --- Hàm tạo Task chính ---
def create_deployment_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, deployment_agent):
    tasks = []
    os.makedirs(f"{output_base_dir}/6_deploy", exist_ok=True)

    global_context = {
        "build_deployment_plan": shared_memory.load("build_deployment_plan"),
        "system_architecture": shared_memory.load("system_architecture"),
        "functional_requirements": shared_memory.load("functional_requirements"),
        "ui_design_template": shared_memory.load("ui_design_template"),
        "security_architecture": shared_memory.load("security_architecture"),
        "test_summary_report": shared_memory.load("test_summary_report"),
        "project_acceptance": shared_memory.load("project_acceptance"),
        "production_implementation_plan": shared_memory.load("production_implementation_plan"),
        "system_admin_guide": shared_memory.load("system_admin_guide"),
        "non_functional_requirements": shared_memory.load("non_functional_requirements")
    }

    # Task 1: Process Guide
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu build_deployment_plan:\n\n"
            f"{global_context['build_deployment_plan']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Hướng dẫn quy trình' (Process Guide) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: giới thiệu, mục đích và phạm vi, bối cảnh, đối tượng sử dụng, tài liệu tham chiếu, thông tin quy trình, các thủ tục chính, các nhiệm vụ, chức năng, thông tin bổ sung về quy trình."
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=deployment_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'build_deployment_plan'."
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng."
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả build_deployment_plan từ người dùng",
            "expected_output": "Tóm tắt kế hoạch xây dựng và triển khai, chi tiết quy trình...",
            "input": global_context["build_deployment_plan"]
}],
        callback=make_docx_callback(
            "Hướng dẫn quy trình",
            f"{output_base_dir}/6_deploy/Process_Guide.docx",
            shared_memory,
            "process_guideline"
        )
    ))

    # Task 2: Installation Guide
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu build_deployment_plan:\n\n"
            f"{global_context['build_deployment_plan']}\n\n"
            f"Dưới đây là dữ liệu system_architecture:\n\n"
            f"{global_context['system_architecture']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Hướng dẫn cài đặt' (Installation Guide) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào."
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: giới thiệu, mục đích, mục tiêu, các bên liên quan, người liên hệ, thông tin cài đặt, tổng quan hệ thống, phạm vi, môi trường, rủi ro, bảo mật, kế hoạch và yêu cầu tiền cài đặt, lịch trình cài đặt, hướng dẫn cài đặt, các giai đoạn chính, nhiệm vụ, sao lưu và phục hồi, quy trình thay đổi và rollback, hỗ trợ cài đặt, danh sách phần cứng, phần mềm, mạng, cơ sở vật chất."
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=deployment_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'build_deployment_plan' và 'system_architecture'."
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng."
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả build_deployment_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch xây dựng và triển khai, yêu cầu cài đặt...",
                "input": global_context["build_deployment_plan"]
            },
            {
                "description": "Thông tin mô tả system_architecture từ người dùng",
                "expected_output": "Tóm tắt kiến trúc hệ thống, môi trường cài đặt...",
                "input": global_context["system_architecture"]
            }
        ],
        callback=make_docx_callback(
            "Hướng dẫn cài đặt",
            f"{output_base_dir}/6_deploy/Installation_Guide.docx",
            shared_memory,
            "installation_guideline"
        )
    ))

    # Task 3: Software User Guide
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Dưới đây là dữ liệu ui_design_template:\n\n"
            f"{global_context['ui_design_template']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Hướng dẫn sử dụng phần mềm' (Software User Guide) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: giới thiệu, mục đích và phạm vi, bối cảnh, đối tượng, tài liệu tham chiếu, tổng quan ứng dụng, thành phần chính, chức năng, lợi ích, phân quyền người dùng, thông tin truy cập, điều hướng, hướng dẫn menu, trang chính, các hành động, thủ tục và chức năng chính. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=deployment_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'functional_requirements' và 'ui_design_template'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu chức năng, chức năng chính...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Thông tin mô tả ui_design_template từ người dùng",
                "expected_output": "Tóm tắt mẫu thiết kế giao diện, điều hướng...",
                "input": global_context["ui_design_template"]
            }
        ],
        callback=make_docx_callback(
            "Hướng dẫn sử dụng phần mềm",
            f"{output_base_dir}/6_deploy/Software_User_Guide.docx",
            shared_memory,
            "software_user_guideline"
        )
    ))

    # Task 4: System Administration Guide
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu system_architecture:\n\n"
            f"{global_context['system_architecture']}\n\n"
            f"Dưới đây là dữ liệu security_architecture:\n\n"
            f"{global_context['security_architecture']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Hướng dẫn quản trị hệ thống' (System Administration Guide) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: giới thiệu, mục đích, mục tiêu, tài liệu tham chiếu, thông tin chung hệ thống, tổng quan, tài sản dữ liệu, quy trình xử lý, môi trường (cơ sở vật chất, phần cứng, phần mềm, mạng), quản trị và bảo trì, quản trị máy chủ, tài khoản người dùng, quản trị phần mềm/hệ thống, quản trị cơ sở dữ liệu, sao lưu phục hồi. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=deployment_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'system_architecture' và 'security_architecture'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả system_architecture từ người dùng",
                "expected_output": "Tóm tắt kiến trúc hệ thống, môi trường quản trị...",
                "input": global_context["system_architecture"]
            },
            {
                "description": "Thông tin mô tả security_architecture từ người dùng",
                "expected_output": "Tóm tắt kiến trúc bảo mật, tài sản dữ liệu...",
                "input": global_context["security_architecture"]
            }
        ],
        callback=make_docx_callback(
            "Hướng dẫn quản trị hệ thống",
            f"{output_base_dir}/6_deploy/System_Administration_Guide.docx",
            shared_memory,
            "system_admin_guideline"
        )
    ))

    # Task 5: Operations Guide
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu system_architecture:\n\n"
            f"{global_context['system_architecture']}\n\n"
            f"Dưới đây là dữ liệu build_deployment_plan:\n\n"
            f"{global_context['build_deployment_plan']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Hướng dẫn vận hành' (Operations Guide) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: giới thiệu, mục đích, đối tượng, thông tin hệ thống, tổng quan, người liên hệ, môi trường, tài sản, giao diện hệ thống, vận hành, quản trị và bảo trì, lịch trình vận hành, phân công trách nhiệm, quy trình vận hành chi tiết, bảo trì và xử lý sự cố, quản lý thay đổi, cấu hình, quản trị hệ thống, phần mềm, máy chủ, cơ sở dữ liệu. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=deployment_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'system_architecture' và 'build_deployment_plan'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả system_architecture từ người dùng",
                "expected_output": "Tóm tắt kiến trúc hệ thống, giao diện hệ thống...",
                "input": global_context["system_architecture"]
            },
            {
                "description": "Thông tin mô tả build_deployment_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch xây dựng và triển khai, quy trình vận hành...",
                "input": global_context["build_deployment_plan"]
            }
        ],
        callback=make_docx_callback(
            "Hướng dẫn vận hành",
            f"{output_base_dir}/6_deploy/Operations_Guide.docx",
            shared_memory,
            "operations_guideline"
        )
    ))

    # Task 6: Production Implementation Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu build_deployment_plan:\n\n"
            f"{global_context['build_deployment_plan']}\n\n"
            f"Dưới đây là dữ liệu test_summary_report:\n\n"
            f"{global_context['test_summary_report']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch triển khai sản phẩm' (Production Implementation Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mô tả triển khai sản phẩm, mục tiêu, thiết bị bị ảnh hưởng, các bước bàn giao sản phẩm, thông tin hỗ trợ kỹ thuật, tác động tiềm tàng, thành phần phần mềm, phần cứng và bước triển khai tương ứng, kiểm thử và chấp nhận, kế hoạch rollback và dự phòng, đào tạo người dùng và tài liệu, liên hệ khẩn cấp khác. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=deployment_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'build_deployment_plan' và 'test_summary_report'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả build_deployment_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch xây dựng và triển khai, mô tả triển khai...",
                "input": global_context["build_deployment_plan"]
            },
            {
                "description": "Thông tin mô tả test_summary_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo kiểm thử, thiết bị bị ảnh hưởng...",
                "input": global_context["test_summary_report"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch triển khai sản phẩm",
            f"{output_base_dir}/6_deploy/Production_Implementation_Plan.docx",
            shared_memory,
            "production_implementation_plan"
        )
    ))

    # Task 7: Production Turnover Approval
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu project_acceptance:\n\n"
            f"{global_context['project_acceptance']}\n\n"
            f"Dưới đây là dữ liệu test_summary_report:\n\n"
            f"{global_context['test_summary_report']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Phê duyệt bàn giao sản xuất' (Production Turnover Approval) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: giới thiệu, mục đích, tổng quan hệ thống/dự án, phạm vi, yêu cầu phê duyệt bàn giao, phê duyệt và ký xác nhận. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=deployment_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_acceptance' và 'test_summary_report'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project_acceptance từ người dùng",
                "expected_output": "Tóm tắt văn bản nghiệm thu dự án, yêu cầu phê duyệt...",
                "input": global_context["project_acceptance"]
            },
            {
                "description": "Thông tin mô tả test_summary_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo kiểm thử, tổng quan hệ thống...",
                "input": global_context["test_summary_report"]
            }
        ],
        callback=make_docx_callback(
            "Phê duyệt bàn giao sản xuất",
            f"{output_base_dir}/6_deploy/Production_Turnover_Approval.docx",
            shared_memory,
            "production_turnover_approval"
        )
    ))

    # Task 8: Deployment Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu build_deployment_plan:\n\n"
            f"{global_context['build_deployment_plan']}\n\n"
            f"Dưới đây là dữ liệu production_implementation_plan:\n\n"
            f"{global_context['production_implementation_plan']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch triển khai' (Deployment Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục đích, phạm vi, chiến lược triển khai, lịch trình triển khai, các bước triển khai, môi trường triển khai, kiểm thử sau triển khai, kế hoạch rollback, hỗ trợ sau triển khai. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=deployment_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'build_deployment_plan' và 'production_implementation_plan'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả build_deployment_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch xây dựng và triển khai, chiến lược triển khai...",
                "input": global_context["build_deployment_plan"]
            },
            {
                "description": "Thông tin mô tả production_implementation_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch triển khai sản phẩm, lịch trình triển khai...",
                "input": global_context["production_implementation_plan"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch triển khai",
            f"{output_base_dir}/6_deploy/Deployment_Plan.docx",
            shared_memory,
            "deployment_plan"
        )
    ))

    # Task 9: Monitoring and Alerting Setup Guide
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu system_admin_guide:\n\n"
            f"{global_context['system_admin_guide']}\n\n"
            f"Dưới đây là dữ liệu non_functional_requirements:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Hướng dẫn thiết lập giám sát và cảnh báo' (Monitoring and Alerting Setup Guide) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục đích, công cụ giám sát, cấu hình giám sát, các chỉ số cần theo dõi, thiết lập cảnh báo, quy trình xử lý sự cố, báo cáo giám sát. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=deployment_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'system_admin_guide' và 'non_functional_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả system_admin_guide từ người dùng",
                "expected_output": "Tóm tắt hướng dẫn quản trị hệ thống, công cụ giám sát...",
                "input": global_context["system_admin_guide"]
            },
            {
                "description": "Thông tin mô tả non_functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu phi chức năng, chỉ số theo dõi...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Hướng dẫn thiết lập giám sát và cảnh báo",
            f"{output_base_dir}/6_deploy/Monitoring_and_Alerting_Setup_Guide.docx",
            shared_memory,
            "monitoring_alerting_guideline"
        )
    ))

    return tasks
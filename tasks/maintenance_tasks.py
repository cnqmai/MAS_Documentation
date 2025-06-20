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
            f"Dưới đây là dữ liệu test_summary_report:\n\n"
            f"{global_context['test_summary_report']}\n\n"
            f"Dưới đây là dữ liệu project_status_report:\n\n"
            f"{global_context['project_status_report']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Đúc kết kinh nghiệm' (Lessons Learned) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: thảo luận đóng dự án, thành phần tham dự, thành công lớn nhất, các bài học kinh nghiệm, các lĩnh vực (khởi động dự án, lập kế hoạch, quản lý dự án, nhân sự, giao tiếp, kinh phí, chi phí, tiến độ, vai trò và trách nhiệm, quản lý rủi ro, mua sắm, yêu cầu, phạm vi, phát triển, kiểm thử, đào tạo, tài liệu, phê duyệt). "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'test_summary_report' và 'project_status_report'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả test_summary_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo kiểm thử, thành công lớn nhất...",
                "input": global_context["test_summary_report"]
            },
            {
                "description": "Thông tin mô tả project_status_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo tình trạng dự án, thảo luận đóng dự án...",
                "input": global_context["project_status_report"]
            }
        ],
        callback=make_docx_callback(
            "Đúc kết kinh nghiệm",
            f"{output_base_dir}/7_maintenance/Lessons_Learned.docx",
            shared_memory,
            "lessons_learned"
        )
    ))

    # Task 2: Transition Out Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu operations_guide:\n\n"
            f"{global_context['operations_guide']}\n\n"
            f"Dưới đây là dữ liệu system_admin_guide:\n\n"
            f"{global_context['system_admin_guide']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch chuyển giao' (Transition Out Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: cách tiếp cận chuyển giao, mục tiêu chuyển giao, tổ chức nhóm chuyển giao, các nhiệm vụ chuyển giao, quy trình chuyển giao kiến thức, triển khai sản phẩm (rollout, di chuyển dữ liệu), kế hoạch truyền thông, lịch trình và bàn giao. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'operations_guide' và 'system_admin_guide'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả operations_guide từ người dùng",
                "expected_output": "Tóm tắt hướng dẫn vận hành, cách tiếp cận chuyển giao...",
                "input": global_context["operations_guide"]
            },
            {
                "description": "Thông tin mô tả system_admin_guide từ người dùng",
                "expected_output": "Tóm tắt hướng dẫn quản trị hệ thống, tổ chức nhóm chuyển giao...",
                "input": global_context["system_admin_guide"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch chuyển giao",
            f"{output_base_dir}/7_maintenance/Transition_Out_Plan.docx",
            shared_memory,
            "transition_out_plan"
        )
    ))

    # Task 3: Post Project Survey Questionnaire
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu lessons_learned:\n\n"
            f"{global_context['lessons_learned']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Bảng khảo sát đánh giá dự án' (Post Project Survey Questionnaire) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: vấn đề chung, giao tiếp dự án, lập kế hoạch và tiến độ, thiết kế và triển khai, quy trình kiểm thử, đào tạo và tài liệu, câu hỏi quy trình tổng quát. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'lessons_learned'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả lessons_learned từ người dùng",
            "expected_output": "Tóm tắt đúc kết kinh nghiệm, vấn đề chung...",
            "input": global_context["lessons_learned"]
        }],
        callback=make_docx_callback(
            "Bảng khảo sát đánh giá dự án",
            f"{output_base_dir}/7_maintenance/Post_Project_Survey_Questionnaire.docx",
            shared_memory,
            "post_project_survey"
        )
    ))

    # Task 4: Post Project Review
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu lessons_learned:\n\n"
            f"{global_context['lessons_learned']}\n\n"
            f"Dưới đây là dữ liệu project_status_report:\n\n"
            f"{global_context['project_status_report']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Đánh giá sau dự án' (Post Project Review) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: các vấn đề tổng quát, giao tiếp trong dự án, tiến độ và thời gian thực hiện, thiết kế và triển khai, kiểm thử, đào tạo, tài liệu, chi phí (ngân sách và thực tế), phê duyệt. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'lessons_learned' và 'project_status_report'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả lessons_learned từ người dùng",
                "expected_output": "Tóm tắt đúc kết kinh nghiệm, các vấn đề tổng quát...",
                "input": global_context["lessons_learned"]
            },
            {
                "description": "Thông tin mô tả project_status_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo tình trạng dự án, giao tiếp trong dự án...",
                "input": global_context["project_status_report"]
            }
        ],
        callback=make_docx_callback(
            "Đánh giá sau dự án",
            f"{output_base_dir}/7_maintenance/Post_Project_Review.docx",
            shared_memory,
            "post_project_review"
        )
    ))

    # Task 5: Change Request Document (CCR)
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu requirements_changes_impact_analysis:\n\n"
            f"{global_context['requirements_changes_impact_analysis']}\n\n"
            f"Dưới đây là dữ liệu bug_report:\n\n"
            f"{global_context['bug_report']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Yêu cầu thay đổi' (Change Request Document - CCR) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: lý do thay đổi, mô tả, giả định, tác động tới dự án, tác động tiến độ, ước lượng công và chi phí, bảng phân bổ vốn/chi phí, phê duyệt. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'requirements_changes_impact_analysis' và 'bug_report'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả requirements_changes_impact_analysis từ người dùng",
                "expected_output": "Tóm tắt phân tích tác động thay đổi yêu cầu, lý do thay đổi...",
                "input": global_context["requirements_changes_impact_analysis"]
            },
            {
                "description": "Thông tin mô tả bug_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo lỗi, mô tả thay đổi...",
                "input": global_context["bug_report"]
            }
        ],
        callback=make_docx_callback(
            "Yêu cầu thay đổi",
            f"{output_base_dir}/7_maintenance/Change_Request_Document.docx",
            shared_memory,
            "change_request"
        )
    ))

    # Task 6: Disaster Recovery Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu security_architecture:\n\n"
            f"{global_context['security_architecture']}\n\n"
            f"Dưới đây là dữ liệu system_admin_guide:\n\n"
            f"{global_context['system_admin_guide']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch khắc phục thảm họa' (Disaster Recovery Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: định nghĩa, mục tiêu, phạm vi, nhóm phục hồi, thời gian và địa điểm khôi phục, dịch vụ quan trọng, mức độ ưu tiên, quy trình phản hồi (thông báo, đánh giá, xử lý), tuyên bố thảm họa, quy trình phục hồi, kế hoạch phục hồi hệ thống mạng, email, server. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'security_architecture' và 'system_admin_guide'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả security_architecture từ người dùng",
                "expected_output": "Tóm tắt kiến trúc bảo mật, mục tiêu phục hồi...",
                "input": global_context["security_architecture"]
            },
            {
                "description": "Thông tin mô tả system_admin_guide từ người dùng",
                "expected_output": "Tóm tắt hướng dẫn quản trị hệ thống, nhóm phục hồi...",
                "input": global_context["system_admin_guide"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch khắc phục thảm họa",
            f"{output_base_dir}/7_maintenance/Disaster_Recovery_Plan.docx",
            shared_memory,
            "disaster_recovery_plan"
        )
    ))

    # Task 7: Certificate Of Compliance
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu test_summary_report:\n\n"
            f"{global_context['test_summary_report']}\n\n"
            f"Dưới đây là dữ liệu project_acceptance:\n\n"
            f"{global_context['project_acceptance']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Giấy chứng nhận nghiệm thu' (Certificate Of Compliance) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: phần nhà thầu (mã đơn hàng, tên sản phẩm bàn giao), phần quản lý dự án (thông tin bàn giao), phòng hợp đồng (xác nhận), chữ ký đại diện nhà thầu và quản lý dự án. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'test_summary_report' và 'project_acceptance'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả test_summary_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo kiểm thử, thông tin bàn giao...",
                "input": global_context["test_summary_report"]
            },
            {
                "description": "Thông tin mô tả project_acceptance từ người dùng",
                "expected_output": "Tóm tắt văn bản nghiệm thu dự án, mã đơn hàng...",
                "input": global_context["project_acceptance"]
            }
        ],
        callback=make_docx_callback(
            "Giấy chứng nhận nghiệm thu",
            f"{output_base_dir}/7_maintenance/Certificate_Of_Compliance.docx",
            shared_memory,
            "certificate_of_compliance"
        )
    ))

    # Task 8: Request For Enhancement
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu bug_report:\n\n"
            f"{global_context['bug_report']}\n\n"
            f"Dưới đây là dữ liệu non_functional_requirements:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Yêu cầu nâng cấp' (Request For Enhancement) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: thông tin người yêu cầu, loại yêu cầu (mới, nâng cấp, chỉnh sửa nhỏ), mô tả chi tiết, mức độ ưu tiên, rủi ro tiềm ẩn, nguồn tài trợ, dự án liên quan, file đính kèm (nếu có). "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'bug_report' và 'non_functional_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả bug_report từ người dùng",
                "expected_output": "Tóm tắt báo cáo lỗi, thông tin người yêu cầu...",
                "input": global_context["bug_report"]
            },
            {
                "description": "Thông tin mô tả non_functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu phi chức năng, mô tả chi tiết nâng cấp...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Yêu cầu nâng cấp",
            f"{output_base_dir}/7_maintenance/Request_For_Enhancement.docx",
            shared_memory,
            "request_for_enhancement"
        )
    ))

    # Task 9: Product Retirement Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu lessons_learned:\n\n"
            f"{global_context['lessons_learned']}\n\n"
            f"Dưới đây là dữ liệu transition_out_plan:\n\n"
            f"{global_context['transition_out_plan']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch ngừng sử dụng sản phẩm' (Product Retirement Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: thông tin hệ thống/sản phẩm, lý do ngừng sử dụng, chi phí và lợi ích, giả định, ràng buộc, danh sách bên liên quan, rủi ro, lịch trình. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'lessons_learned' và 'transition_out_plan'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả lessons_learned từ người dùng",
                "expected_output": "Tóm tắt đúc kết kinh nghiệm, thông tin hệ thống...",
                "input": global_context["lessons_learned"]
            },
            {
                "description": "Thông tin mô tả transition_out_plan từ người dùng",
                "expected_output": "Tóm tắt kế hoạch chuyển giao, lý do ngừng sử dụng...",
                "input": global_context["transition_out_plan"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch ngừng sử dụng sản phẩm",
            f"{output_base_dir}/7_maintenance/Product_Retirement_Plan.docx",
            shared_memory,
            "product_retirement_plan"
        )
    ))

    # Task 10: Global Application Support Summary
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu operations_guide:\n\n"
            f"{global_context['operations_guide']}\n\n"
            f"Dưới đây là dữ liệu sla_warranty_policies:\n\n"
            f"{global_context['sla_warranty_policies']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Tóm tắt hỗ trợ ứng dụng toàn cầu' (Global Application Support Summary) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: dữ liệu ứng dụng, thiết kế, phát triển và tích hợp, hỗ trợ sản xuất, hạ tầng, bảo mật, hướng dẫn điền thông tin. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'operations_guide' và 'sla_warranty_policies'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả operations_guide từ người dùng",
                "expected_output": "Tóm tắt hướng dẫn vận hành, dữ liệu ứng dụng...",
                "input": global_context["operations_guide"]
            },
            {
                "description": "Thông tin mô tả sla_warranty_policies từ người dùng",
                "expected_output": "Tóm tắt chính sách SLA và bảo hành, hỗ trợ sản xuất...",
                "input": global_context["sla_warranty_policies"]
            }
        ],
        callback=make_docx_callback(
            "Tóm tắt hỗ trợ ứng dụng toàn cầu",
            f"{output_base_dir}/7_maintenance/Global_Application_Support_Summary.docx",
            shared_memory,
            "global_support_summary"
        )
    ))

    # Task 11: Developer Knowledge Transfer Report
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu source_code_documentation:\n\n"
            f"{global_context['source_code_documentation']}\n\n"
            f"Dưới đây là dữ liệu middleware_documentation:\n\n"
            f"{global_context['middleware_documentation']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Báo cáo chuyển giao kiến thức' (Developer Knowledge Transfer Report) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: tài liệu tham khảo, nhân sự chính (người dùng, chuyên gia, lập trình viên), kiến thức kỹ thuật (ngôn ngữ, công cụ, CSDL, hệ điều hành), kiến thức nghiệp vụ, kiến thức ứng dụng (chức năng, luồng xử lý, client/server, môi trường sử dụng). "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'source_code_documentation' và 'middleware_documentation'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả source_code_documentation từ người dùng",
                "expected_output": "Tóm tắt tài liệu mã nguồn, tài liệu tham khảo...",
                "input": global_context["source_code_documentation"]
            },
            {
                "description": "Thông tin mô tả middleware_documentation từ người dùng",
                "expected_output": "Tóm tắt tài liệu middleware, nhân sự chính...",
                "input": global_context["middleware_documentation"]
            }
        ],
        callback=make_docx_callback(
            "Báo cáo chuyển giao kiến thức",
            f"{output_base_dir}/7_maintenance/Developer_Knowledge_Transfer_Report.docx",
            shared_memory,
            "knowledge_transfer_report"
        )
    ))

    # Task 12: Maintenance Checklist
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu operations_guide:\n\n"
            f"{global_context['operations_guide']}\n\n"
            f"Dưới đây là dữ liệu system_admin_guide:\n\n"
            f"{global_context['system_admin_guide']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách kiểm tra bảo trì' (Maintenance Checklist) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: danh sách nhiệm vụ bảo trì, tần suất thực hiện, người phụ trách, công cụ sử dụng, kiểm tra hiệu suất, kiểm tra bảo mật, sao lưu và phục hồi. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'operations_guide' và 'system_admin_guide'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả operations_guide từ người dùng",
                "expected_output": "Tóm tắt hướng dẫn vận hành, nhiệm vụ bảo trì...",
                "input": global_context["operations_guide"]
            },
            {
                "description": "Thông tin mô tả system_admin_guide từ người dùng",
                "expected_output": "Tóm tắt hướng dẫn quản trị hệ thống, tần suất thực hiện...",
                "input": global_context["system_admin_guide"]
            }
        ],
        callback=make_docx_callback(
            "Danh sách kiểm tra bảo trì",
            f"{output_base_dir}/7_maintenance/Maintenance_Checklist.docx",
            shared_memory,
            "maintenance_checklist"
        )
    ))

    # Task 13: Issue Reporting Template
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu bug_report:\n\n"
            f"{global_context['bug_report']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Mẫu báo cáo sự cố' (Issue Reporting Template) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mô tả sự cố, vị trí xuất hiện, mức độ nghiêm trọng, trạng thái, mức ưu tiên, môi trường xảy ra, phương pháp phát hiện, người phụ trách. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'bug_report'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả bug_report từ người dùng",
            "expected_output": "Tóm tắt báo cáo lỗi, mô tả sự cố...",
            "input": global_context["bug_report"]
        }],
        callback=make_docx_callback(
            "Mẫu báo cáo sự cố",
            f"{output_base_dir}/7_maintenance/Issue_Reporting_Template.docx",
            shared_memory,
            "issue_reporting_template"
        )
    ))

    # Task 14: SLA and Warranty Policies
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu sla_template:\n\n"
            f"{global_context['sla_template']}\n\n"
            f"Dưới đây là dữ liệu non_functional_requirements:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Chính sách SLA và bảo hành' (SLA and Warranty Policies) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục đích, phạm vi, các điều khoản SLA, chính sách bảo hành, thời gian phản hồi, thời gian giải quyết, trách nhiệm các bên, quy trình yêu cầu dịch vụ. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'sla_template' và 'non_functional_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả sla_template từ người dùng",
                "expected_output": "Tóm tắt mẫu SLA, mục đích và điều khoản SLA...",
                "input": global_context["sla_template"]
            },
            {
                "description": "Thông tin mô tả non_functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu phi chức năng, thời gian phản hồi...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Chính sách SLA và bảo hành",
            f"{output_base_dir}/7_maintenance/SLA_and_Warranty_Policies.docx",
            shared_memory,
            "sla_warranty_policies"
        )
    ))

    # Task 15: Security Patch Management Guide
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu security_architecture:\n\n"
            f"{global_context['security_architecture']}\n\n"
            f"Dưới đây là dữ liệu system_admin_guide:\n\n"
            f"{global_context['system_admin_guide']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Hướng dẫn quản lý bản vá bảo mật' (Security Patch Management Guide) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục đích, quy trình quản lý bản vá, công cụ sử dụng, lịch trình áp dụng bản vá, kiểm thử bản vá, quy trình rollback, báo cáo quản lý bản vá. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'security_architecture' và 'system_admin_guide'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả security_architecture từ người dùng",
                "expected_output": "Tóm tắt kiến trúc bảo mật, mục đích quản lý bản vá...",
                "input": global_context["security_architecture"]
            },
            {
                "description": "Thông tin mô tả system_admin_guide từ người dùng",
                "expected_output": "Tóm tắt hướng dẫn quản trị hệ thống, quy trình quản lý bản vá...",
                "input": global_context["system_admin_guide"]
            }
        ],
        callback=make_docx_callback(
            "Hướng dẫn quản lý bản vá bảo mật",
            f"{output_base_dir}/7_maintenance/Security_Patch_Management_Guide.docx",
            shared_memory,
            "security_patch_management"
        )
    ))

    # Task 16: Usage Analytics Report
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu monitoring_alerting_guide:\n\n"
            f"{global_context['monitoring_alerting_guide']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Báo cáo phân tích sử dụng' (Usage Analytics Report) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: tổng quan sử dụng, các chỉ số hiệu suất, xu hướng sử dụng, vấn đề phát hiện, khuyến nghị cải tiến, báo cáo chi tiết. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'monitoring_alerting_guide'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả monitoring_alerting_guide từ người dùng",
            "expected_output": "Tóm tắt hướng dẫn giám sát và cảnh báo, tổng quan sử dụng...",
            "input": global_context["monitoring_alerting_guide"]
        }],
        callback=make_docx_callback(
            "Báo cáo phân tích sử dụng",
            f"{output_base_dir}/7_maintenance/Usage_Analytics_Report.docx",
            shared_memory,
            "usage_analytics_report"
        )
    ))

    # Task 17: Maintenance and Support Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu operations_guide:\n\n"
            f"{global_context['operations_guide']}\n\n"
            f"Dưới đây là dữ liệu sla_warranty_policies:\n\n"
            f"{global_context['sla_warranty_policies']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch bảo trì và hỗ trợ' (Maintenance and Support Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục đích, phạm vi, kế hoạch bảo trì, kế hoạch hỗ trợ, lịch trình bảo trì, trách nhiệm các bên, quy trình xử lý sự cố, báo cáo bảo trì. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'operations_guide' và 'sla_warranty_policies'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng."
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả operations_guide từ người dùng",
                "expected_output": "Tóm tắt hướng dẫn vận hành, kế hoạch bảo trì...",
                "input": global_context["operations_guide"]
            },
            {
                "description": "Thông tin mô tả sla_warranty_policies từ người dùng",
                "expected_output": "Tóm tắt chính sách SLA và bảo hành, kế hoạch hỗ trợ...",
                "input": global_context["sla_warranty_policies"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch bảo trì và hỗ trợ",
            f"{output_base_dir}/7_maintenance/Maintenance_and_Support_Plan.docx",
            shared_memory,
            "maintenance_support_plan"
        )
    ))

    return tasks
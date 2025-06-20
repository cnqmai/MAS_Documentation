import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx, create_xlsx, create_image
from graphviz import Digraph
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
def create_design_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, design_agent):
    tasks = []
    os.makedirs(f"{output_base_dir}/3_design", exist_ok=True)

    global_context = {
        "brd": shared_memory.load("brd"),
        "functional_requirements": shared_memory.load("functional_requirements"),
        "non_functional_requirements": shared_memory.load("non_functional_requirements"),
        "project_plan": shared_memory.load("project_plan"),
        "wbs": shared_memory.load("wbs"),
        "srs": shared_memory.load("srs"),
        "software_architecture_plan": shared_memory.load("software_architecture_plan"),
        "use_case_template": shared_memory.load("use_case_template"),
        "privacy_security_requirements": shared_memory.load("privacy_security_requirements"),
        "system_architecture": shared_memory.load("system_architecture"),
        "hld": shared_memory.load("hld"),
        "technical_requirements": shared_memory.load("technical_requirements"),
        "system_requirements": shared_memory.load("system_requirements")
    }

    # Task 1: System Requirements Specification
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu brd:\n\n"
            f"{global_context['brd']}\n\n"
            f"Dưới đây là dữ liệu functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Dưới đây là dữ liệu non_functional_requirements:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Đặc tả yêu cầu hệ thống' (System Requirements Specification - SRS) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: giới thiệu, mục đích, phạm vi, vai trò và trách nhiệm, yêu cầu hệ thống, yêu cầu chức năng, yêu cầu phần mềm/phần cứng, đặc điểm người dùng, khả năng sử dụng, môi trường vận hành, bảo mật, tuân thủ quy định, khôi phục thảm họa, thông số dữ liệu, ảnh hưởng đến mạng. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'brd', 'functional_requirements', và 'non_functional_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả brd từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kinh doanh, mục tiêu, phạm vi...",
                "input": global_context["brd"]
            },
            {
                "description": "Thông tin mô tả functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu chức năng, đặc điểm người dùng...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Thông tin mô tả non_functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu phi chức năng, bảo mật, hiệu suất...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Đặc tả yêu cầu hệ thống",
            f"{output_base_dir}/3_design/System_Requirements_Specifications.docx",
            shared_memory,
            "srs"
        )
    ))

    # Task 2: Analysis and Design Document
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu srs:\n\n"
            f"{global_context['srs']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Phân tích và thiết kế' (Analysis and Design Document) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần điền nội dung thực tế cho từng mục: tổng quan hệ thống, hạ tầng, giả định thiết kế, tóm tắt thay đổi từ khởi tạo, tác động đến kinh doanh, ứng dụng, kiến trúc hiện tại và đề xuất, bảo mật và kiểm toán, thiết kế giao diện, tầng ứng dụng, thông tin triển khai, cải tiến trong tương lai, phê duyệt. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'srs'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả srs từ người dùng",
            "expected_output": "Tóm tắt yêu cầu hệ thống, kiến trúc, bảo mật...",
            "input": global_context["srs"]
        }],
        callback=make_docx_callback(
            "Phân tích và thiết kế",
            f"{output_base_dir}/3_design/Analysis_and_Design_Document.docx",
            shared_memory,
            "analysis_design"
        )
    ))

    # Task 3: Application Development Project List
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu project_plan:\n\n"
            f"{global_context['project_plan']}\n\n"
            f"Dưới đây là dữ liệu wbs:\n\n"
            f"{global_context['wbs']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách dự án phát triển ứng dụng' (Application Development Project List) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần điền nội dung thực tế cho từng mục: mô tả hệ thống, kiến trúc phần mềm hiện tại và đề xuất, thiết kế giao diện, các lớp ứng dụng, tác động hạ tầng, an ninh, tích hợp, triển khai, các cải tiến đề xuất, phê duyệt. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_plan' và 'wbs'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project_plan từ người dùng",
                "expected_output": "Tóm tắt mục tiêu, mô tả hệ thống...",
                "input": global_context["project_plan"]
            },
            {
                "description": "Thông tin mô tả wbs từ người dùng",
                "expected_output": "Tóm tắt cấu trúc công việc, kiến trúc phần mềm...",
                "input": global_context["wbs"]
            }
        ],
        callback=make_docx_callback(
            "Danh sách dự án phát triển ứng dụng",
            f"{output_base_dir}/3_design/Application_Development_Project_List.docx",
            shared_memory,
            "app_dev_project_list"
        )
    ))

    # Task 4: Technical Requirements Document
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu srs:\n\n"
            f"{global_context['srs']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Yêu cầu kỹ thuật' (Technical Requirements Document) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục đích, phạm vi, tài liệu tham chiếu, giả định, yêu cầu kỹ thuật cụ thể (hệ thống, mạng, cơ sở dữ liệu, giao diện người dùng, giao diện hệ thống, bảo mật). "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'srs'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả srs từ người dùng",
            "expected_output": "Tóm tắt yêu cầu kỹ thuật, hệ thống, bảo mật...",
            "input": global_context["srs"]
        }],
        callback=make_docx_callback(
            "Yêu cầu kỹ thuật",
            f"{output_base_dir}/3_design/Technical_Requirements_Document.docx",
            shared_memory,
            "technical_requirements"
        )
    ))

    # Task 5: Database Design Document
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu srs:\n\n"
            f"{global_context['srs']}\n\n"
            f"Dưới đây là dữ liệu software_architecture:\n\n"
            f"{global_context['software_architecture_plan']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Thiết kế cơ sở dữ liệu' (Database Design Document) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục tiêu, đối tượng sử dụng, nhân sự và chủ sở hữu dữ liệu, giả định, ràng buộc, tổng quan hệ thống, kiến trúc phần cứng/phần mềm, quyết định thiết kế tổng thể, chức năng quản trị CSDL, thiết kế chi tiết (mapping dữ liệu, backup, phục hồi), yêu cầu báo cáo. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'srs' và 'software_architecture_plan'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả srs từ người dùng",
                "expected_output": "Tóm tắt yêu cầu hệ thống, dữ liệu...",
                "input": global_context["srs"]
            },
            {
                "description": "Thông tin mô tả software_architecture_plan từ người dùng",
                "expected_output": "Tóm tắt kiến trúc phần cứng/phần mềm...",
                "input": global_context["software_architecture_plan"]
            }
        ],
        callback=make_docx_callback(
            "Thiết kế cơ sở dữ liệu",
            f"{output_base_dir}/3_design/Database_Design_Document.docx",
            shared_memory,
            "database_design"
        )
    ))

    # Task 6: Website Planning Checklist
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Dưới đây là dữ liệu non_functional_requirements:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách kiểm tra lập kế hoạch website' (Website Planning Checklist) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: phân tích đối tượng, phân tích đối thủ, chiến lược nội dung, quảng bá và bảo trì, cấu trúc trang, dẫn hướng, thiết kế hình ảnh và bố cục, thiết kế giao diện người dùng, kỹ thuật kiểm thử. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'functional_requirements' và 'non_functional_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu chức năng, đối tượng, giao diện...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Thông tin mô tả non_functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu phi chức năng, thiết kế, kiểm thử...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Danh sách kiểm tra lập kế hoạch website",
            f"{output_base_dir}/3_design/Website_Planning_Checklist.docx",
            shared_memory,
            "website_planning_checklist"
        )
    ))

    # Task 7: User Interface Design Template
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Mẫu thiết kế giao diện người dùng' (User Interface Design Template) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: tên sản phẩm/hệ thống, lý do thiết kế lại, chi tiết màn hình (tên, chức năng, tab, điều hướng), các thành phần (trường dữ liệu, kiểu dữ liệu, độ dài, tính toán, dropdown, font chữ, màu, kích thước, nút hành động, popup, định dạng, sự kiện), ràng buộc, rủi ro, các bên liên quan. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'functional_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả functional_requirements từ người dùng",
            "expected_output": "Tóm tắt yêu cầu chức năng, giao diện, thành phần...",
            "input": global_context["functional_requirements"]
        }],
        callback=make_docx_callback(
            "Mẫu thiết kế giao diện người dùng",
            f"{output_base_dir}/3_design/User_Interface_Design_Template.docx",
            shared_memory,
            "ui_design_template"
        )
    ))

    # Task 8: Report Design Template
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Mẫu thiết kế báo cáo' (Report Design Template) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: tên hệ thống, mục đích báo cáo, tần suất, quyền truy cập, giả định, ràng buộc, rủi ro, các bên liên quan, các thành phần (tham số đầu vào, tính toán, công thức, trường báo cáo, nguồn dữ liệu, nhóm dữ liệu, tiêu đề/trang, mẫu báo cáo). "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'functional_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả functional_requirements từ người dùng",
            "expected_output": "Tóm tắt yêu cầu chức năng, báo cáo, nguồn dữ liệu...",
            "input": global_context["functional_requirements"]
        }],
        callback=make_docx_callback(
            "Mẫu thiết kế báo cáo",
            f"{output_base_dir}/3_design/Report_Design_Template.docx",
            shared_memory,
            "report_design_template"
        )
    ))

    # Task 9: Code Review Checklist
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu technical_requirements:\n\n"
            f"{global_context['technical_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách kiểm tra đánh giá mã nguồn' (Code Review Checklist) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: cấu trúc, tài liệu, biến, kiểu dữ liệu, phong cách lập trình, cấu trúc điều khiển, vòng lặp, bảo trì, bảo mật, tính khả dụng, kiểm tra lỗi, xử lý ngoại lệ, rò rỉ tài nguyên, thời gian, thử nghiệm, xác thực. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'technical_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả technical_requirements từ người dùng",
            "expected_output": "Tóm tắt yêu cầu kỹ thuật, bảo mật, kiểm thử...",
            "input": global_context["technical_requirements"]
        }],
        callback=make_docx_callback(
            "Danh sách kiểm tra đánh giá mã nguồn",
            f"{output_base_dir}/3_design/Code_Review_Checklist.docx",
            shared_memory,
            "code_review_checklist"
        )
    ))

    # Task 10: Conversion Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu srs:\n\n"
            f"{global_context['srs']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch chuyển đổi' (Conversion Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mục đích, tài liệu tham khảo, mô tả hệ thống và chiến lược chuyển đổi, các loại chuyển đổi, yếu tố rủi ro, lịch trình chuyển đổi, hỗ trợ chuyển đổi (phần cứng, phần mềm, nhân lực), đảm bảo an ninh và chất lượng dữ liệu. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'srs'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả srs từ người dùng",
            "expected_output": "Tóm tắt yêu cầu hệ thống, chiến lược chuyển đổi...",
            "input": global_context["srs"]
        }],
        callback=make_docx_callback(
            "Kế hoạch chuyển đổi",
            f"{output_base_dir}/3_design/Conversion_Plan.docx",
            shared_memory,
            "conversion_plan"
        )
    ))

    # Task 11: System Architecture
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu software_architecture_plan:\n\n"
            f"{global_context['software_architecture_plan']}\n\n"
            f"Dưới đây là dữ liệu non_functional_requirements:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kiến trúc hệ thống' (System Architecture) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: tổng quan kiến trúc, các thành phần hệ thống, mối quan hệ giữa các thành phần, yêu cầu hiệu suất, bảo mật, khả năng mở rộng. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'software_architecture_plan' và 'non_functional_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả software_architecture_plan từ người dùng",
                "expected_output": "Tóm tắt kiến trúc hệ thống, các thành phần...",
                "input": global_context["software_architecture_plan"]
            },
            {
                "description": "Thông tin mô tả non_functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu phi chức năng, hiệu suất, bảo mật...",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Kiến trúc hệ thống",
            f"{output_base_dir}/3_design/System_Architecture.docx",
            shared_memory,
            "system_architecture"
        )
    ))

    # Task 12: Data Flow Diagrams (DFD)
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu srs:\n\n"
            f"{global_context['srs']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Sơ đồ luồng dữ liệu' (Data Flow Diagrams - DFD) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: sơ đồ DFD cấp 0, các sơ đồ DFD cấp thấp hơn, mô tả các quá trình, lưu trữ dữ liệu, và luồng dữ liệu. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'srs'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả srs từ người dùng",
            "expected_output": "Tóm tắt yêu cầu hệ thống, luồng dữ liệu...",
            "input": global_context["srs"]
        }],
        callback=make_docx_callback(
            "Sơ đồ luồng dữ liệu",
            f"{output_base_dir}/3_design/Data_Flow_Diagrams.docx",
            shared_memory,
            "dfd"
        )
    ))

    # Task 13: Sequence Diagrams
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Dưới đây là dữ liệu use_case_template:\n\n"
            f"{global_context['use_case_template']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Sơ đồ tuần tự' (Sequence Diagrams) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: sơ đồ tuần tự cho các kịch bản chính, mô tả các đối tượng, thông điệp, và trình tự tương tác. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'functional_requirements' và 'use_case_template'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu chức năng, đối tượng tương tác...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Thông tin mô tả use_case_template từ người dùng",
                "expected_output": "Tóm tắt kịch bản sử dụng, trình tự tương tác...",
                "input": global_context["use_case_template"]
            }
        ],
        callback=make_docx_callback(
            "Sơ đồ tuần tự",
            f"{output_base_dir}/3_design/Sequence_Diagrams.docx",
            shared_memory,
            "sequence_diagrams"
        )
    ))

    # Task 14: Security Architecture Document
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu privacy_security_requirements:\n\n"
            f"{global_context['privacy_security_requirements']}\n\n"
            f"Dưới đây là dữ liệu system_architecture:\n\n"
            f"{global_context['system_architecture']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kiến trúc bảo mật' (Security Architecture Document) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: yêu cầu bảo mật, kiến trúc bảo mật, biện pháp kiểm soát truy cập, mã hóa dữ liệu, và tuân thủ quy định. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'privacy_security_requirements' và 'system_architecture'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả privacy_security_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu bảo mật, kiểm soát truy cập...",
                "input": global_context["privacy_security_requirements"]
            },
            {
                "description": "Thông tin mô tả system_architecture từ người dùng",
                "expected_output": "Tóm tắt kiến trúc hệ thống, thành phần bảo mật...",
                "input": global_context["system_architecture"]
            }
        ],
        callback=make_docx_callback(
            "Kiến trúc bảo mật",
            f"{output_base_dir}/3_design/Security_Architecture_Document.docx",
            shared_memory,
            "security_architecture"
        )
    ))

    # Task 15: High-Level Design (HLD)
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu srs:\n\n"
            f"{global_context['srs']}\n\n"
            f"Dưới đây là dữ liệu software_architecture_plan:\n\n"
            f"{global_context['software_architecture_plan']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Thiết kế cấp cao' (High-Level Design - HLD) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: tổng quan hệ thống, các thành phần chính, mối quan hệ giữa các thành phần, kiến trúc phần mềm và phần cứng. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'srs' và 'software_architecture_plan'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả srs từ người dùng",
                "expected_output": "Tóm tắt yêu cầu hệ thống, tổng quan...",
                "input": global_context["srs"]
            },
            {
                "description": "Thông tin mô tả software_architecture_plan từ người dùng",
                "expected_output": "Tóm tắt kiến trúc phần mềm, thành phần chính...",
                "input": global_context["software_architecture_plan"]
            }
        ],
        callback=make_docx_callback(
            "Thiết kế cấp cao",
            f"{output_base_dir}/3_design/High_Level_Design.docx",
            shared_memory,
            "hld"
        )
    ))

    # Task 16: Low-Level Design (LLD)
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu hld:\n\n"
            f"{global_context['hld']}\n\n"
            f"Dưới đây là dữ liệu technical_requirements:\n\n"
            f"{global_context['technical_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Thiết kế cấp thấp' (Low-Level Design - LLD) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mô tả chi tiết các module, giao diện, thuật toán, cấu trúc dữ liệu. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'hld' và 'technical_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả hld từ người dùng",
                "expected_output": "Tóm tắt thiết kế cấp cao, module...",
                "input": global_context["hld"]
            },
            {
                "description": "Thông tin mô tả technical_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kỹ thuật, thuật toán, cấu trúc dữ liệu...",
                "input": global_context["technical_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Thiết kế cấp thấp",
            f"{output_base_dir}/3_design/Low_Level_Design.docx",
            shared_memory,
            "lld"
        )
    ))

    # Task 17: API Design Document
    tasks.append(Task(
        description=(
            f"Dưới đây là dữ liệu functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Dưới đây là dữ liệu technical_requirements:\n\n"
            f"{global_context['technical_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Thiết kế API' (API Design Document) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, cần nội dung thực tế cho từng mục: mô tả API, endpoint, phương thức, tham số, phản hồi, và bảo mật. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=design_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'functional_requirements' và 'technical_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc [], mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu chức năng, mô tả API...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Thông tin mô tả technical_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kỹ thuật, bảo mật, endpoint...",
                "input": global_context["technical_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Thiết kế API",
            f"{output_base_dir}/3_design/API_Design_Document.docx",
            shared_memory,
            "api_design"
        )
    ))


    # New Task: System Architecture Diagram for System Architecture (Graphviz)
    tasks.append(Task(
        description=(
            f"Dựa trên dữ liệu system_requirements:\n\n"
            f"system_requirements:\n{global_context['system_requirements']}\n\n"
            f"Tạo một sơ đồ kiến trúc hệ thống (System Architecture Diagram) cho System Architecture để minh họa các thành phần chính của hệ thống (e.g., Frontend, Backend, Database, API Gateway). "
            f"Sơ đồ phải bao gồm ít nhất 4 thành phần và các liên kết thể hiện luồng tương tác giữa chúng. "
            f"Kết quả là mã Graphviz DOT định dạng một sơ đồ hướng (digraph), lưu vào file 'System_Architecture_Diagram.dot' trong thư mục '{output_base_dir}/4_design'. "
            f"Render file DOT thành hình ảnh PNG bằng hàm create_image. "
            f"Lưu mã DOT vào SharedMemory với khóa 'graphviz_system_architecture' và đường dẫn hình ảnh PNG vào SharedMemory với khóa 'image_system_architecture'."
        ),
        agent=design_agent,
        expected_output=(
            f"Mã Graphviz DOT hoàn chỉnh minh họa sơ đồ kiến trúc hệ thống, lưu trong '{output_base_dir}/3_design/System_Architecture_Diagram.dot' và SharedMemory với khóa 'graphviz_system_architecture'. "
            f"Hình ảnh PNG được render từ DOT, lưu trong '{output_base_dir}/3_design/System_Architecture_Diagram.png' và SharedMemory với khóa 'image_system_architecture'. "
            f"Sơ đồ rõ ràng, có ít nhất 4 thành phần và các liên kết tương tác."
        ),
        context=[
            {
                "description": "Thông tin từ system_requirements",
                "expected_output": "Tóm tắt yêu cầu hệ thống để xác định các thành phần kiến trúc.",
                "input": global_context["system_requirements"]
            }
        ],
        callback=lambda output: (
            shared_memory.save("graphviz_system_architecture", output) and
            (open(os.path.join(output_base_dir, "3_design", "System_Architecture_Diagram.dot"), "w", encoding="utf-8").write(output), True)[-1] and
            shared_memory.save("image_system_architecture", create_image(Digraph(body=output.split('\n')[1:-1]), os.path.join(output_base_dir, "4_design", "System_Architecture_Diagram")))
        )
    ))

    # New Task: Wireframe for User Interface Design Template (Graphviz)
    tasks.append(Task(
        description=(
            f"Dựa trên dữ liệu functional_requirements:\n\n"
            f"functional_requirements:\n{global_context['functional_requirements']}\n\n"
            f"Tạo một wireframe mẫu cho User Interface Design Template để minh họa bố cục giao diện người dùng (e.g., Header, Sidebar, Content Area, Footer). "
            f"Wireframe phải bao gồm ít nhất 4 thành phần giao diện và các liên kết thể hiện cách điều hướng. "
            f"Kết quả là mã Graphviz DOT định dạng một sơ đồ hướng (digraph), lưu vào file 'UI_Wireframe.dot' trong thư mục '{output_base_dir}/4_design'. "
            f"Render file DOT thành hình ảnh PNG bằng hàm create_image. "
            f"Lưu mã DOT vào SharedMemory với khóa 'graphviz_ui_wireframe' và đường dẫn hình ảnh PNG vào SharedMemory với khóa 'image_ui_wireframe'."
        ),
        agent=design_agent,
        expected_output=(
            f"Mã Graphviz DOT hoàn chỉnh minh họa wireframe giao diện người dùng, lưu trong '{output_base_dir}/3_design/UI_Wireframe.dot' và SharedMemory với khóa 'graphviz_ui_wireframe'. "
            f"Hình ảnh PNG được render từ DOT, lưu trong '{output_base_dir}/3_design/UI_Wireframe.png' và SharedMemory với khóa 'image_ui_wireframe'. "
            f"Sơ đồ rõ ràng, có ít nhất 4 thành phần giao diện và luồng điều hướng."
        ),
        context=[
            {
                "description": "Thông tin từ functional_requirements",
                "expected_output": "Tóm tắt yêu cầu chức năng để xác định bố cục giao diện.",
                "input": global_context["functional_requirements"]
            }
        ],
        callback=lambda output: (
            shared_memory.save("graphviz_ui_wireframe", output) and
            (open(os.path.join(output_base_dir, "3_design", "UI_Wireframe.dot"), "w", encoding="utf-8").write(output), True)[-1] and
            shared_memory.save("image_ui_wireframe", create_image(Digraph(body=output.split('\n')[1:-1]), os.path.join(output_base_dir, "4_design", "UI_Wireframe")))
        )
    ))

    return tasks
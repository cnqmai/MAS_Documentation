import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx, create_xlsx, create_image
from graphviz import Digraph
import json

# --- Các hàm Callback đã điều chỉnh ---
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
            print(f"❌ Lỗi: Không thể tạo DOCX '{filename}'.")
            return False
    return callback

def make_docx_xlsx_callback(title, docx_filename, xlsx_filename, shared_memory, save_key):
    def callback(output_from_agent_object): 
        print(f"🚀 Bắt đầu tạo DOCX và XLSX cho: {title}...")
        try:
            raw_output_json_string = (
                getattr(output_from_agent_object, "result", None)
                or getattr(output_from_agent_object, "response", None)
                or getattr(output_from_agent_object, "final_output", None)
                or str(output_from_agent_object)
            )
            raw_output_json_string = str(raw_output_json_string)
            if not raw_output_json_string.strip():
                print(f"⚠️ Agent không trả về dữ liệu JSON cho task '{title}'.")
                return False
            parsed_output = json.loads(raw_output_json_string)
            docx_content_raw = parsed_output.get("docx_content", "")
            xlsx_data_raw = parsed_output.get("xlsx_data", [])
            docx_paragraphs = docx_content_raw.split('\n')
            docx_path = create_docx(title, docx_paragraphs, docx_filename)
            xlsx_path = create_xlsx(xlsx_data_raw, xlsx_filename)
            shared_memory.save(save_key, raw_output_json_string)
            if docx_path and xlsx_path:
                print(f"✅ DOCX '{docx_filename}' và XLSX '{xlsx_filename}' đã được tạo và lưu thành công.")
                return True
            else:
                print(f"❌ Lỗi khi tạo file DOCX hoặc XLSX cho task '{title}'.")
                return False
        except json.JSONDecodeError as e:
            print(f"❌ Lỗi JSON: Không thể phân tích nội dung agent cho '{title}': {e}")
            print(f"🪵 Output nhận được: {raw_output_json_string[:500]}...")
            return False
        except Exception as e:
            print(f"❌ Lỗi không xác định khi xử lý callback cho '{title}': {e}")
            return False
    return callback

# --- Hàm tạo Task chính ---
def create_requirements_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, requirement_agent):
    tasks = []
    os.makedirs(f"{output_base_dir}/2_requirements", exist_ok=True)

    global_context = {
        "project_plan": shared_memory.load("project_plan"),
        "project_charter": shared_memory.load("project_charter"),
        "statement_of_work": shared_memory.load("statement_of_work"),
        "business_case": shared_memory.load("business_case"),
        "brd": shared_memory.load("brd"),
        "functional_requirements": shared_memory.load("functional_requirements"),
        "non_functional_requirements": shared_memory.load("non_functional_requirements"),
        "wbs": shared_memory.load("wbs"),
        "rtm": shared_memory.load("rtm")
    }

    # Task 1: Managing Scope and Requirements Checklist
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_plan:\n\n"
            f"{global_context['project_plan']}\n\n"
            f"Dưới đây là thông tin project_charter:\n\n"
            f"{global_context['project_charter']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách kiểm tra quản lý phạm vi và yêu cầu' (Managing Scope and Requirements Checklist) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: mục đích, tổng quan sản phẩm/hệ thống, lý do triển khai dự án, giả định, phụ thuộc, ràng buộc, danh sách các bên liên quan, rủi ro, bảng kiểm phạm vi/yêu cầu. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=requirement_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_plan' và 'project_charter'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project_plan từ người dùng",
                "expected_output": "Tóm tắt mục tiêu, phạm vi, rủi ro...",
                "input": global_context["project_plan"]
            },
            {
                "description": "Thông tin mô tả project_charter từ người dùng",
                "expected_output": "Tóm tắt tổng quan sản phẩm, lý do, giả định...",
                "input": global_context["project_charter"]
            }
        ],
        callback=make_docx_callback(
            "Danh sách kiểm tra quản lý phạm vi và yêu cầu",
            f"{output_base_dir}/2_requirements/Managing_Scope_and_Requirements_Checklist.docx",
            shared_memory,
            "scope_requirements_checklist"
        )
    ))

    # Task 2: Business Requirements Document (BRD)
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_plan:\n\n"
            f"{global_context['project_plan']}\n\n"
            f"Dưới đây là thông tin statement_of_work:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            f"Dưới đây là thông tin business_case:\n\n"
            f"{global_context['business_case']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Yêu cầu kinh doanh' (Business Requirements Document - BRD) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: thông tin dự án, quy trình hiện tại và cải tiến, yêu cầu hệ thống và người dùng cuối, yêu cầu khác. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=requirement_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_plan', 'statement_of_work', và 'business_case'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project_plan từ người dùng",
                "expected_output": "Tóm tắt mục tiêu, chi phí, rủi ro...",
                "input": global_context["project_plan"]
            },
            {
                "description": "Thông tin mô tả statement_of_work từ người dùng",
                "expected_output": "Tóm tắt quy trình cải tiến, phạm vi...",
                "input": global_context["statement_of_work"]
            },
            {
                "description": "Thông tin mô tả business_case từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kinh doanh, lợi ích...",
                "input": global_context["business_case"]
            }
        ],
        callback=make_docx_callback(
            "Yêu cầu kinh doanh",
            f"{output_base_dir}/2_requirements/Business_Requirements_Document.docx",
            shared_memory,
            "brd"
        )
    ))

    # Task 3: Business Requirements Presentation To Stakeholders
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin brd:\n\n"
            f"{global_context['brd']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Thuyết trình yêu cầu kinh doanh cho các bên liên quan' (Business Requirements Presentation To Stakeholders) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: lý do yêu cầu kinh doanh quan trọng, thông tin và mô tả dự án, mục tiêu và phạm vi, các bên liên quan, chi phí, bảo trì hàng năm, mốc thời gian, luồng xử lý hiện tại/tương lai, yêu cầu kinh doanh cấp cao, giao diện hệ thống, hạ tầng, các yêu cầu khác. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=requirement_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'brd'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả brd từ người dùng",
            "expected_output": "Tóm tắt lý do, mục tiêu, phạm vi, yêu cầu...",
            "input": global_context["brd"]
        }],
        callback=make_docx_callback(
            "Thuyết trình yêu cầu kinh doanh",
            f"{output_base_dir}/2_requirements/Business_Requirements_Presentation.docx",
            shared_memory,
            "brd_presentation"
        )
    ))

    # Task 4: Functional Requirements Document
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin brd:\n\n"
            f"{global_context['brd']}\n\n"
            f"Dưới đây là thông tin project_plan:\n\n"
            f"{global_context['project_plan']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Yêu cầu chức năng' (Functional Requirements Document) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Tài liệu này xác định các yêu cầu chức năng, bao gồm: mục tiêu, thông tin quy trình, yêu cầu chức năng và phi chức năng, giao diện hệ thống, phần mềm, phần cứng, giao tiếp. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=requirement_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'brd' và 'project_plan'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả brd từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kinh doanh, mục tiêu, quy trình...",
                "input": global_context["brd"]
            },
            {
                "description": "Thông tin mô tả project_plan từ người dùng",
                "expected_output": "Tóm tắt mục tiêu, phạm vi, quy trình kinh doanh...",
                "input": global_context["project_plan"]
            }
        ],
        callback=make_docx_callback(
            "Yêu cầu chức năng",
            f"{output_base_dir}/2_requirements/Functional_Requirements_Document.docx",
            shared_memory,
            "functional_requirements"
        )
    ))

    # Task 5: Software Architecture Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin brd:\n\n"
            f"{global_context['brd']}\n\n"
            f"Dưới đây là thông tin functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch kiến trúc phần mềm' (Software Architecture Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Tài liệu này mô tả tổng quan kiến trúc phần mềm của hệ thống từ nhiều góc độ, bao gồm: phạm vi, ký hiệu, thuật ngữ, mục tiêu kiến trúc, các góc nhìn (Use-case, Logic, Quy trình, Triển khai, Triển khai dữ liệu, Hiệu năng, Kích thước, Chất lượng). "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=requirement_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'brd' và 'functional_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả brd từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kinh doanh, phạm vi...",
                "input": global_context["brd"]
            },
            {
                "description": "Thông tin mô tả functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu chức năng, góc nhìn kỹ thuật...",
                "input": global_context["functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch kiến trúc phần mềm",
            f"{output_base_dir}/2_requirements/Software_Architecture_Plan.docx",
            shared_memory,
            "software_architecture_plan"
        )
    ))

    # Task 6: Use Case Template
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Mẫu Use Case' (Use Case Template) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Tài liệu này mô tả yêu cầu dự án dưới dạng kịch bản người dùng sử dụng hệ thống để đạt mục tiêu, bao gồm: mục tiêu, thông tin dự án, yêu cầu kinh doanh cấp cao, giao diện, hạ tầng, mô tả Use Case (đơn giản, truyền thống, ví dụ), các yêu cầu liên quan (màn hình, nội dung, đào tạo). "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=requirement_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'functional_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả functional_requirements từ người dùng",
            "expected_output": "Tóm tắt yêu cầu chức năng, kịch bản sử dụng, giao diện...",
            "input": global_context["functional_requirements"]
        }],
        callback=make_docx_callback(
            "Mẫu Use Case",
            f"{output_base_dir}/2_requirements/Use_Case_Template.docx",
            shared_memory,
            "use_case_template"
        )
    ))

    # Task 7: Requirements Inspection Checklist
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin brd:\n\n"
            f"{global_context['brd']}\n\n"
            f"Dưới đây là thông tin functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách kiểm tra kiểm tra yêu cầu' (Requirements Inspection Checklist) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Tài liệu này đảm bảo yêu cầu dự án được xác định rõ ràng và chất lượng cao, bao gồm: tính đúng đắn, truy vết, giao diện, yêu cầu hành vi, phi hành vi. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'brd' và 'functional_requirements'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả brd từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kinh doanh, mục tiêu...",
                "input": global_context["brd"]
            },
            {
                "description": "Thông tin mô tả functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu chức năng, giao diện, hành vi...",
                "input": global_context["functional_requirements"]
            }
        ],
        callback=make_docx_callback(
            "Danh sách kiểm tra kiểm tra yêu cầu",
            f"{output_base_dir}/2_requirements/Requirements_Inspection_Checklist.docx",
            shared_memory,
            "requirements_inspection_checklist"
        )
    ))

    # Task 8: Requirements Traceability Matrix (RTM)
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin brd:\n\n"
            f"{global_context['brd']}\n\n"
            f"Dưới đây là thông tin functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Dưới đây là thông tin wbs:\n\n"
            f"{global_context['wbs']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Ma trận truy vết yêu cầu' (Requirements Traceability Matrix - RTM) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Ma trận này truy vết yêu cầu từ yêu cầu ban đầu đến thiết kế và kiểm thử, đảm bảo sự đầy đủ và nhất quán, bao gồm: mục đích, ma trận yêu cầu (thông tin chung, giao diện, hành vi, phi hành vi, độ chính xác, truy vết). "
            "Yêu cầu trả về một chuỗi JSON chứa cả phần nội dung cho DOCX (dưới khóa 'docx_content') và dữ liệu cho XLSX (dưới khóa 'xlsx_data'). "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=requirement_agent,
        expected_output=(
            "Một chuỗi JSON hợp lệ chứa hai trường: "
            "'docx_content' là nội dung tài liệu ma trận truy vết yêu cầu (có cấu trúc, rõ ràng, đầy đủ các mục, không có phần trống hoặc placeholder), "
            "'xlsx_data' là dữ liệu bảng tính chi tiết các yêu cầu, nguồn, thiết kế, kiểm thử. "
            "Nội dung docx_content có thể trình bày dạng Markdown hoặc plain text."
        ),
        context=[
            {
                "description": "Thông tin mô tả brd từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kinh doanh, mục tiêu...",
                "input": global_context["brd"]
            },
            {
                "description": "Thông tin mô tả functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu chức năng, giao diện, hành vi...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Thông tin mô tả wbs từ người dùng",
                "expected_output": "Tóm tắt cấu trúc công việc, các hạng mục...",
                "input": global_context["wbs"]
            }
        ],
        callback=make_docx_xlsx_callback(
            "Ma trận truy vết yêu cầu",
            f"{output_base_dir}/2_requirements/Requirements_Traceability_Matrix.docx",
            f"{output_base_dir}/2_requirements/Requirements_Traceability_Matrix.xlsx",
            shared_memory,
            "rtm"
        )
    ))

    # Task 9: Requirements Changes Impact Analysis
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin rtm:\n\n"
            f"{global_context['rtm']}\n\n"
            f"Dưới đây là thông tin brd:\n\n"
            f"{global_context['brd']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Phân tích tác động thay đổi yêu cầu' (Requirements Changes Impact Analysis) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Tài liệu này phân tích tác động khi thay đổi yêu cầu, bao gồm: mục đích, mô tả thay đổi, rủi ro, giả định, các thành phần bị ảnh hưởng, ước lượng thời gian/chi phí. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=requirement_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'rtm' và 'brd'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả rtm từ người dùng",
                "expected_output": "Tóm tắt ma trận truy vết yêu cầu, các yêu cầu liên quan...",
                "input": global_context["rtm"]
            },
            {
                "description": "Thông tin mô tả brd từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kinh doanh, mục tiêu...",
                "input": global_context["brd"]
            }
        ],
        callback=make_docx_callback(
            "Phân tích tác động thay đổi yêu cầu",
            f"{output_base_dir}/2_requirements/Requirements_Changes_Impact_Analysis.docx",
            shared_memory,
            "requirements_changes_impact"
        )
    ))

    # Task 10: Training Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin functional_requirements:\n\n"
            f"{global_context['functional_requirements']}\n\n"
            f"Dưới đây là thông tin brd:\n\n"
            f"{global_context['brd']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch đào tạo' (Training Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Tài liệu này hỗ trợ sử dụng và duy trì hệ thống hoặc ứng dụng, bao gồm: giới thiệu, phạm vi, phương pháp đào tạo, khóa học đào tạo người dùng/kỹ thuật, yêu cầu môi trường, lịch đào tạo, phê duyệt và ký nhận. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=requirement_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'functional_requirements' và 'brd'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu chức năng, đào tạo kỹ thuật...",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Thông tin mô tả brd từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kinh doanh, mục tiêu, phạm vi...",
                "input": global_context["brd"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch đào tạo",
            f"{output_base_dir}/2_requirements/Training_Plan.docx",
            shared_memory,
            "training_plan"
        )
    ))

    # Task 11: Service Level Agreement Template
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin non_functional_requirements:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            f"Dưới đây là thông tin brd:\n\n"
            f"{global_context['brd']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Mẫu thỏa thuận mức dịch vụ' (Service Level Agreement Template) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Tài liệu này là thỏa thuận chính thức giữa tổ chức và khách hàng về dịch vụ được cung cấp, bao gồm: điều khoản, thời hạn, tổ chức liên quan, danh sách ứng dụng được hỗ trợ (khôi phục thảm họa, mức độ ưu tiên), trách nhiệm, hỗ trợ, báo cáo hiệu suất, điều kiện chấm dứt/hủy bỏ, sửa đổi SLA. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=requirement_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'non_functional_requirements' và 'brd'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả non_functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu phi chức năng, hiệu suất, hỗ trợ...",
                "input": global_context["non_functional_requirements"]
            },
            {
                "description": "Thông tin mô tả brd từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kinh doanh, tổ chức liên quan...",
                "input": global_context["brd"]
            }
        ],
        callback=make_docx_callback(
            "Mẫu thỏa thuận mức dịch vụ",
            f"{output_base_dir}/2_requirements/Service_Level_Agreement_Template.docx",
            shared_memory,
            "sla_template"
        )
    ))

    # Task 12: Non-functional Requirements
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin brd:\n\n"
            f"{global_context['brd']}\n\n"
            f"Dưới đây là thông tin project_plan:\n\n"
            f"{global_context['project_plan']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Yêu cầu phi chức năng' (Non-functional Requirements) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Tài liệu này xác định các yêu cầu phi chức năng như hiệu suất, bảo mật, khả năng mở rộng, và khả năng sử dụng, bao gồm: yêu cầu hiệu suất, bảo mật, khả năng mở rộng, khả năng sử dụng, các ràng buộc kỹ thuật và nghiệp vụ. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=requirement_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'brd' và 'project_plan'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả brd từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kinh doanh, hiệu suất, bảo mật...",
                "input": global_context["brd"]
            },
            {
                "description": "Thông tin mô tả project_plan từ người dùng",
                "expected_output": "Tóm tắt mục tiêu, ràng buộc kỹ thuật, nghiệp vụ...",
                "input": global_context["project_plan"]
            }
        ],
        callback=make_docx_callback(
            "Yêu cầu phi chức năng",
            f"{output_base_dir}/2_requirements/Non_functional_Requirements.docx",
            shared_memory,
            "non_functional_requirements"
        )
    ))

    # Task 13: Privacy & Security Requirements
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin non_functional_requirements:\n\n"
            f"{global_context['non_functional_requirements']}\n\n"
            f"Dưới đây là thông tin brd:\n\n"
            f"{global_context['brd']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Yêu cầu bảo mật và quyền riêng tư' (Privacy & Security Requirements) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Tài liệu này xác định các yêu cầu liên quan đến bảo mật và quyền riêng tư của hệ thống, bao gồm: yêu cầu bảo mật dữ liệu, quyền riêng tư của người dùng, tuân thủ quy định pháp lý, biện pháp kiểm soát truy cập. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=requirement_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'non_functional_requirements' và 'brd'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả non_functional_requirements từ người dùng",
                "expected_output": "Tóm tắt yêu cầu phi chức năng, bảo mật, quyền riêng tư...",
                "input": global_context["non_functional_requirements"]
            },
            {
                "description": "Thông tin mô tả brd từ người dùng",
                "expected_output": "Tóm tắt yêu cầu kinh doanh, thông tin người dùng...",
                "input": global_context["brd"]
            }
        ],
        callback=make_docx_callback(
            "Yêu cầu bảo mật và quyền riêng tư",
            f"{output_base_dir}/2_requirements/Privacy_and_Security_Requirements.docx",
            shared_memory,
            "privacy_security_requirements"
        )
    ))

    # New Task: Use Case Diagram for BRD
    tasks.append(Task(
        description=(
            f"Dựa trên dữ liệu project_charter và business_case:\n\n"
            f"project_charter:\n{global_context['project_charter']}\n\n"
            f"business_case:\n{global_context['business_case']}\n\n"
            f"Tạo một sơ đồ use case (Use Case Diagram) cho Business Requirements Document (BRD) để minh họa các actor và use case chính của hệ thống. "
            f"Sơ đồ phải bao gồm ít nhất 3 actor (e.g., Người dùng, Quản trị viên, Hệ thống bên ngoài) và 5 use case (e.g., Đăng nhập, Quản lý dữ liệu, Xuất báo cáo), với các liên kết thể hiện mối quan hệ. "
            f"Kết quả là mã Graphviz DOT định dạng một sơ đồ hướng (digraph), lưu vào file 'Use_Case_Diagram_BRD.dot' trong thư mục '{output_base_dir}/3_requirements'. "
            f"Render file DOT thành hình ảnh PNG bằng hàm create_image. "
            f"Lưu mã DOT vào SharedMemory với khóa 'graphviz_brd_use_case' và đường dẫn hình ảnh PNG vào SharedMemory với khóa 'image_brd_use_case'."
        ),
        agent=researcher_agent,
        expected_output=(
            f"Mã Graphviz DOT hoàn chỉnh minh họa sơ đồ use case cho BRD, lưu trong '{output_base_dir}/2_requirements/Use_Case_Diagram_BRD.dot' và SharedMemory với khóa 'graphviz_brd_use_case'. "
            f"Hình ảnh PNG được render từ DOT, lưu trong '{output_base_dir}/2_requirements/Use_Case_Diagram_BRD.png' và SharedMemory với khóa 'image_brd_use_case'. "
            f"Sơ đồ rõ ràng, có ít nhất 3 actor và 5 use case, với các liên kết được thể hiện."
        ),
        context=[
            {
                "description": "Thông tin từ project_charter",
                "expected_output": "Tóm tắt mục tiêu dự án và các actor liên quan.",
                "input": global_context["project_charter"]
            },
            {
                "description": "Thông tin từ business_case",
                "expected_output": "Tóm tắt các yêu cầu kinh doanh để xác định use case.",
                "input": global_context["business_case"]
            }
        ],
        callback=lambda output: (
            shared_memory.save("graphviz_brd_use_case", output) and
            (open(os.path.join(output_base_dir, "2_requirements", "Use_Case_Diagram_BRD.dot"), "w", encoding="utf-8").write(output), True)[-1] and
            shared_memory.save("image_brd_use_case", create_image(Digraph(body=output.split('\n')[1:-1]), os.path.join(output_base_dir, "3_requirements", "Use_Case_Diagram_BRD")))
        )
    ))

    # New Task: Traceability Matrix for RTM (Graphviz)
    tasks.append(Task(
        description=(
            f"Dựa trên dữ liệu functional_requirements và non_functional_requirements:\n\n"
            f"functional_requirements:\n{global_context['functional_requirements']}\n\n"
            f"non_functional_requirements:\n{global_context['non_functional_requirements']}\n\n"
            f"Tạo một ma trận truy xuất yêu cầu (Requirements Traceability Matrix) cho Requirements Traceability Matrix (RTM) để minh họa mối quan hệ giữa yêu cầu và test case. "
            f"Ma trận phải bao gồm ít nhất 5 yêu cầu (e.g., REQ-001, REQ-002) và 5 test case (e.g., TC-001, TC-002), với các liên kết thể hiện yêu cầu nào được kiểm tra bởi test case nào. "
            f"Kết quả là mã Graphviz DOT định dạng một sơ đồ hướng (digraph), lưu vào file 'Traceability_Matrix_RTM.dot' trong thư mục '{output_base_dir}/3_requirements'. "
            f"Render file DOT thành hình ảnh PNG bằng hàm create_image. "
            f"Lưu mã DOT vào SharedMemory với khóa 'graphviz_rtm_traceability' và đường dẫn hình ảnh PNG vào SharedMemory với khóa 'image_rtm_traceability'."
        ),
        agent=researcher_agent,
        expected_output=(
            f"Mã Graphviz DOT hoàn chỉnh minh họa ma trận truy xuất yêu cầu cho RTM, lưu trong '{output_base_dir}/2_requirements/Traceability_Matrix_RTM.dot' và SharedMemory với khóa 'graphviz_rtm_traceability'. "
            f"Hình ảnh PNG được render từ DOT, lưu trong '{output_base_dir}/2_requirements/Traceability_Matrix_RTM.png' và SharedMemory với khóa 'image_rtm_traceability'. "
            f"Sơ đồ rõ ràng, có ít nhất 5 yêu cầu và 5 test case, với các liên kết được thể hiện."
        ),
        context=[
            {
                "description": "Thông tin từ functional_requirements",
                "expected_output": "Tóm tắt các yêu cầu chức năng để xác định yêu cầu.",
                "input": global_context["functional_requirements"]
            },
            {
                "description": "Thông tin từ non_functional_requirements",
                "expected_output": "Tóm tắt các yêu cầu phi chức năng để bổ sung yêu cầu.",
                "input": global_context["non_functional_requirements"]
            }
        ],
        callback=lambda output: (
            shared_memory.save("graphviz_rtm_traceability", output) and
            (open(os.path.join(output_base_dir, "2_requirements", "Traceability_Matrix_RTM.dot"), "w", encoding="utf-8").write(output), True)[-1] and
            shared_memory.save("image_rtm_traceability", create_image(Digraph(body=output.split('\n')[1:-1]), os.path.join(output_base_dir, "3_requirements", "Traceability_Matrix_RTM")))
        )
    ))

    return tasks
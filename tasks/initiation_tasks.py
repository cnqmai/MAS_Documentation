import os
from crewai import Task
from memory.shared_memory import SharedMemory
from utils.output_formats import create_docx, create_xlsx, create_image, create_md
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
def create_initiation_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, initiation_agent):
    tasks = []
    os.makedirs(f"{output_base_dir}/0_initiation", exist_ok=True)

    global_context = {
        "system_request_summary": shared_memory.load("system_request_summary"),
        "business_case": shared_memory.load("business_case"),
        "project_charter": shared_memory.load("project_charter"),
        "project_team_definition": shared_memory.load("project_team_definition")
    }

    # context phải là một list các string, mỗi string là "key: value"
    # Cả 2 cách (list[str] hoặc list[dict]) đều có thể gây lỗi tùy phiên bản CrewAI.
    # Để chắc chắn, hãy thử context là 1 dict duy nhất (không phải list), ví dụ:
    # CrewAI có thể yêu cầu context là list các string, mỗi string là "key: value"
    # Nếu context là dict hoặc list[dict] đều lỗi, hãy thử lại:
    # Task 1: Project Initiation Agenda
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin tóm tắt yêu cầu hệ thống (system_request_summary):\n\n"
            f"{global_context['system_request_summary']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Chương trình nghị sự khởi tạo dự án' (Project Initiation Agenda) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: chủ đề họp, người khởi xướng, thời gian họp, danh sách người tham dự, tài liệu cần đọc, chủ đề thảo luận, người trình bày, tài liệu đính kèm. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=initiation_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'system_request_summary'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả yêu cầu hệ thống từ người dùng",
            "expected_output": "Tóm tắt thông tin hệ thống cần xây dựng (mục tiêu, người dùng, tính năng...)",
            "input": global_context["system_request_summary"]
        }],
        callback=make_docx_callback(
            "Chương trình nghị sự khởi tạo dự án",
            f"{output_base_dir}/0_initiation/Project_Initiation_Agenda.docx",
            shared_memory,
            "project_initiation_agenda"
        )
    ))

    # Task 2: Project Charter
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin tóm tắt yêu cầu hệ thống (system_request_summary):\n\n"
            f"{global_context['system_request_summary']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Bản điều lệ dự án' (Project Charter) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: tuyên bố cơ hội, mục tiêu, phạm vi dự án, quy trình trong và ngoài phạm vi, nhóm dự án, các bên liên quan, mốc thời gian, chi phí ước tính. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=initiation_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'system_request_summary'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả yêu cầu hệ thống từ người dùng",
            "expected_output": "Tóm tắt thông tin hệ thống cần xây dựng (mục tiêu, người dùng, tính năng...)",
            "input": global_context["system_request_summary"]
        }],
        callback=make_docx_callback(
            "Bản điều lệ dự án",
            f"{output_base_dir}/0_initiation/Project_Charter.docx",
            shared_memory,
            "project_charter"
        )
    ))

    # Task 3: Business Case Document
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin tóm tắt yêu cầu hệ thống (system_request_summary):\n\n"
            f"{global_context['system_request_summary']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Trường hợp kinh doanh' (Business Case Document) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: mô tả nhu cầu, vấn đề, giải pháp; lợi ích định lượng và định tính; rủi ro; yêu cầu; chi phí; tiến độ; chất lượng; khuyến nghị và lựa chọn thay thế; phê duyệt từ các bên liên quan. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=initiation_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'system_request_summary'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả yêu cầu hệ thống từ người dùng",
            "expected_output": "Tóm tắt thông tin hệ thống cần xây dựng (mục tiêu, người dùng, tính năng...)",
            "input": global_context["system_request_summary"]
        }],
        callback=make_docx_callback(
            "Tài liệu trường hợp kinh doanh",
            f"{output_base_dir}/0_initiation/Business_Case_Document.docx",
            shared_memory,
            "business_case"
        )
    ))

    # Task 4: Feasibility Study
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin tóm tắt yêu cầu hệ thống (system_request_summary):\n\n"
            f"{global_context['system_request_summary']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Nghiên cứu khả thi' (Feasibility Study) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: giới thiệu, mục tiêu, phạm vi; hệ thống hiện tại; môi trường vận hành; tổ chức người dùng; sản phẩm cuối cùng; giải pháp và lựa chọn thay thế; phê duyệt; phân tích khả thi kỹ thuật, tài chính, tổ chức, pháp lý; rủi ro khả thi. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=initiation_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'system_request_summary'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả yêu cầu hệ thống từ người dùng",
            "expected_output": "Tóm tắt thông tin hệ thống cần xây dựng (mục tiêu, người dùng, tính năng...)",
            "input": global_context["system_request_summary"]
        }],
        callback=make_docx_callback(
            "Nghiên cứu khả thi",
            f"{output_base_dir}/0_initiation/Feasibility_Study.docx",
            shared_memory,
            "feasibility_study"
        )
    ))

    # Task 5: Value Proposition Template
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin tóm tắt yêu cầu hệ thống (system_request_summary):\n\n"
            f"{global_context['system_request_summary']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Mẫu giá trị đề xuất' (Value Proposition Template) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: sản phẩm/dịch vụ đề xuất, mô tả dự án, thị trường mục tiêu, nhu cầu và ngưỡng chịu đựng, tính năng cần thiết, lợi ích, quyết định tự phát triển hay mua ngoài. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=initiation_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'system_request_summary'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả yêu cầu hệ thống từ người dùng",
            "expected_output": "Tóm tắt thông tin hệ thống cần xây dựng (mục tiêu, người dùng, tính năng...)",
            "input": global_context["system_request_summary"]
        }],
        callback=make_docx_callback(
            "Mẫu giá trị đề xuất",
            f"{output_base_dir}/0_initiation/Value_Proposition_Template.docx",
            shared_memory,
            "value_proposition"
        )
    ))

    # Task 6: Project or Issue Submission Form
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin tóm tắt yêu cầu hệ thống (system_request_summary):\n\n"
            f"{global_context['system_request_summary']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Mẫu gửi dự án hoặc vấn đề' (Project or Issue Submission Form) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: mô tả vấn đề, mức độ ưu tiên, tác động, hành động đề xuất. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=initiation_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'system_request_summary'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả yêu cầu hệ thống từ người dùng",
            "expected_output": "Tóm tắt thông tin hệ thống cần xây dựng (mục tiêu, người dùng, tính năng...)",
            "input": global_context["system_request_summary"]
        }],
        callback=make_docx_callback(
            "Mẫu gửi dự án hoặc vấn đề",
            f"{output_base_dir}/0_initiation/Project_or_Issue_Submission_Form.docx",
            shared_memory,
            "submission_form"
        )
    ))

    # Task 7: Project Cost - Benefit Analysis
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin tóm tắt yêu cầu hệ thống (system_request_summary):\n\n"
            f"{global_context['system_request_summary']}\n\n"
            f"Dưới đây là thông tin business case (nếu có):\n\n"
            f"{global_context['business_case']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Phân tích chi phí - lợi ích' (Project Cost - Benefit Analysis) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: thông tin chung (tên dự án, nhà tài trợ, mục đích, lợi ích), khuyến nghị và lựa chọn thay thế, chi phí và nguồn lực, lịch trình, rủi ro, phân tích rủi ro. "
            "Yêu cầu trả về một chuỗi JSON chứa cả phần nội dung cho DOCX (dưới khóa 'docx_content') và dữ liệu cho XLSX (dưới khóa 'xlsx_data'). "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=initiation_agent,
        expected_output=(
            "Một chuỗi JSON hợp lệ chứa hai trường: "
            "'docx_content' là nội dung tài liệu phân tích chi phí - lợi ích (có cấu trúc, rõ ràng, đầy đủ các mục, không có phần trống hoặc placeholder), "
            "'xlsx_data' là dữ liệu bảng tính chi tiết các hạng mục chi phí/lợi ích. "
            "Nội dung docx_content có thể trình bày dạng Markdown hoặc plain text."
        ),
        context=[
            {
                "description": "Thông tin mô tả yêu cầu hệ thống từ người dùng",
                "expected_output": "Tóm tắt thông tin hệ thống cần xây dựng (mục tiêu, người dùng, tính năng...)",
                "input": global_context["system_request_summary"]
            },
            {
                "description": "Thông tin mô tả business case",
                "expected_output": "Thông tin người dùng đã cung cấp về business case",
                "input": global_context["business_case"]
            }
        ],
        callback=make_docx_xlsx_callback(
            "Phân tích chi phí - lợi ích",
            f"{output_base_dir}/0_initiation/Project_Cost_Benefit_Analysis.docx",
            f"{output_base_dir}/0_initiation/Project_Cost_Benefit_Analysis.xlsx",
            shared_memory,
            "cost_benefit_analysis"
        )
    ))

    # Task 8: Project Team Definition
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project charter (project_charter):\n\n"
            f"{global_context['project_charter']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Định nghĩa nhóm dự án' (Project Team Definition) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: tổng quan buổi họp, nhận diện các bên liên quan và thành viên dự án, lịch trình các cột mốc chính, trách nhiệm, cơ cấu tổ chức, danh sách thành viên, vai trò và trách nhiệm, yêu cầu kỹ năng. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=initiation_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_charter'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả project charter từ người dùng",
            "expected_output": "Tóm tắt thông tin về nhóm dự án, thành viên, vai trò, trách nhiệm, kỹ năng...",
            "input": global_context["project_charter"]
        }],
        callback=make_docx_callback(
            "Định nghĩa nhóm dự án",
            f"{output_base_dir}/0_initiation/Project_Team_Definition.docx",
            shared_memory,
            "project_team_definition"
        )
    ))

    # Task 9: Stakeholder Identification List
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project charter (project_charter):\n\n"
            f"{global_context['project_charter']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách nhận diện các bên liên quan' (Stakeholder Identification List) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: danh sách các bên liên quan, danh sách tài sản, danh sách rủi ro. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=initiation_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_charter'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả project charter từ người dùng",
            "expected_output": "Tóm tắt thông tin về các bên liên quan, tài sản, rủi ro của dự án",
            "input": global_context["project_charter"]
        }],
        callback=make_docx_callback(
            "Danh sách nhận diện các bên liên quan",
            f"{output_base_dir}/0_initiation/Stakeholder_Identification_List.docx",
            shared_memory,
            "identification_list"
        )
    ))

    # Task 10: Project Resource Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project charter (project_charter):\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Dưới đây là thông tin project team definition (project_team_definition):\n\n"
            f"{global_context['project_team_definition']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch tài nguyên dự án' (Project Resource Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: kích thước nhóm dự án, các nguồn lực/kỹ năng cần thiết, nguồn nhân sự, số lượng, nhu cầu cơ sở vật chất, hồ sơ nguồn lực, tổ chức nhóm, giả định, rủi ro và biện pháp giảm thiểu, phê duyệt từ các bên liên quan. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=initiation_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_charter' và 'project_team_definition'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project charter từ người dùng",
                "expected_output": "Tóm tắt thông tin về nguồn lực, tổ chức nhóm, giả định, rủi ro...",
                "input": global_context["project_charter"]
            },
            {
                "description": "Thông tin mô tả project team definition từ người dùng",
                "expected_output": "Tóm tắt thông tin về thành viên, kỹ năng, nhân sự, tổ chức nhóm...",
                "input": global_context["project_team_definition"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch tài nguyên dự án",
            f"{output_base_dir}/0_initiation/Project_Resource_Plan.docx",
            shared_memory,
            "project_resource_plan"
        )
    ))

    # Task 11: Concept Of Operations
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project charter (project_charter):\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Dưới đây là thông tin business case (business_case):\n\n"
            f"{global_context['business_case']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Khái niệm vận hành' (Concept Of Operations) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: nhu cầu năng lực, mô tả vận hành và hỗ trợ, cơ sở thay đổi, tác động tiềm năng, kịch bản vận hành, tính năng chức năng, tóm tắt và phân tích hệ thống đề xuất, quy trình vận hành, vai trò và trách nhiệm, rủi ro vận hành. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=initiation_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_charter' và 'business_case'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project charter từ người dùng",
                "expected_output": "Tóm tắt thông tin về vận hành, vai trò, quy trình, rủi ro...",
                "input": global_context["project_charter"]
            },
            {
                "description": "Thông tin mô tả business case từ người dùng",
                "expected_output": "Tóm tắt thông tin về mục tiêu, lợi ích, tác động, rủi ro...",
                "input": global_context["business_case"]
            }
        ],
        callback=make_docx_callback(
            "Khái niệm vận hành",
            f"{output_base_dir}/0_initiation/Concept_Of_Operations.docx",
            shared_memory,
            "concept_of_operations"
        )
    ))

    # Task 12: Initiate Project Checklist
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project charter (project_charter):\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Dưới đây là thông tin business case (business_case):\n\n"
            f"{global_context['business_case']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách kiểm tra khởi tạo dự án' (Initiate Project Checklist) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: mục tiêu dự án, vòng đời phát triển hệ thống, kiểm tra từng hạng mục, danh sách công việc, trạng thái hoàn thành, người chịu trách nhiệm, ghi chú. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_charter' và 'business_case'. "
            "Tài liệu không phải là template mẫu, không có hướng dẫn placeholder hay dấu ngoặc (), mà là nội dung cụ thể rõ ràng. "
            "Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project charter từ người dùng",
                "expected_output": "Tóm tắt thông tin về mục tiêu, vòng đời, trách nhiệm, công việc...",
                "input": global_context["project_charter"]
            },
            {
                "description": "Thông tin mô tả business case từ người dùng",
                "expected_output": "Tóm tắt thông tin về mục tiêu, lợi ích, rủi ro, tiến độ...",
                "input": global_context["business_case"]
            }
        ],
        callback=make_docx_callback(
            "Danh sách kiểm tra khởi tạo dự án",
            f"{output_base_dir}/0_initiation/Initiate_Project_Checklist.docx",
            shared_memory,
            "initiate_project_checklist"
        )
    ))

    return tasks

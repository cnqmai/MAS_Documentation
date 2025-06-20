import os
import json
from crewai import Task
from utils.output_formats import create_docx, create_xlsx
from memory.shared_memory import SharedMemory

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

def create_planning_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, planning_agent):
    tasks = []
    os.makedirs(f"{output_base_dir}/1_planning", exist_ok=True)

    global_context = {
        "project_charter": shared_memory.load("project_charter"),
        "business_case": shared_memory.load("business_case"),
        "cost_benefit_analysis": shared_memory.load("cost_benefit_analysis"),
        "project_team_definition": shared_memory.load("project_team_definition"),
        "project_resource_plan": shared_memory.load("project_resource_plan"),
        "statement_of_work": shared_memory.load("statement_of_work"),
        "project_approval": shared_memory.load("project_approval"),
        "risk_data_collection": shared_memory.load("risk_data_collection"),
        "activity_worksheet": shared_memory.load("activity_worksheet"),
        "wbs": shared_memory.load("wbs"),
        "opportunities_summary": shared_memory.load("opportunities_summary")
    }

    # PMO Checklist
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_charter:\n\n"
            f"{global_context['project_charter']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách kiểm tra PMO' (Project Management Office Checklist) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: mục tiêu, đối tượng, trách nhiệm tổ chức, bộ công cụ PMO, dữ liệu cần thiết, giao diện hỗ trợ. "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_charter'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả project_charter từ người dùng",
            "expected_output": "Tóm tắt thông tin về mục tiêu, vai trò, công cụ, dữ liệu PMO...",
            "input": global_context["project_charter"]
        }],
        callback=make_docx_callback(
            "Danh sách kiểm tra PMO",
            f"{output_base_dir}/1_planning/PMO_Checklist.docx",
            shared_memory,
            "pmo_checklist"
        )
    ))

    # Statement of Work
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_charter:\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Dưới đây là thông tin business_case:\n\n"
            f"{global_context['business_case']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Tuyên bố công việc' (Statement of Work) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: mục tiêu kinh doanh, mô tả dự án, ước lượng tiến độ, chi phí, nguồn lực, kiểm soát dự án (rủi ro, vấn đề, thay đổi). "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_charter' và 'business_case'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project_charter từ người dùng",
                "expected_output": "Tóm tắt thông tin về phạm vi, sản phẩm đầu ra, tiến độ...",
                "input": global_context["project_charter"]
            },
            {
                "description": "Thông tin mô tả business_case từ người dùng",
                "expected_output": "Tóm tắt mục tiêu kinh doanh, lợi ích, chi phí...",
                "input": global_context["business_case"]
            }
        ],
        callback=make_docx_callback(
            "Tuyên bố công việc",
            f"{output_base_dir}/1_planning/Statement_of_Work.docx",
            shared_memory,
            "statement_of_work"
        )
    ))

    # Project Approval Document
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_charter:\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Dưới đây là thông tin business_case:\n\n"
            f"{global_context['business_case']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Phê duyệt dự án' (Project Approval Document) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: tổng quan, mô tả dự án, thông tin phê duyệt (người phụ trách, chữ ký, ngày tháng). "
            "Nếu thiếu dữ liệu, hãy suy luận hoặc đưa ra giả định hợp lý thay vì để trống."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_charter' và 'business_case'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project_charter từ người dùng",
                "expected_output": "Tóm tắt tổng quan dự án, phạm vi, mục tiêu...",
                "input": global_context["project_charter"]
            },
            {
                "description": "Thông tin mô tả business_case từ người dùng",
                "expected_output": "Tóm tắt mục tiêu, lợi ích, phê duyệt...",
                "input": global_context["business_case"]
            }
        ],
        callback=make_docx_callback(
            "Phê duyệt dự án",
            f"{output_base_dir}/1_planning/Project_Approval_Document.docx",
            shared_memory,
            "project_approval"
        )
    ))

    # Cost Estimating Worksheet
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin cost_benefit_analysis:\n\n"
            f"{global_context['cost_benefit_analysis']}\n\n"
            "Hãy sử dụng dữ liệu trên để tạo bảng tính 'Ước lượng chi phí' (Cost Estimating Worksheet) với nội dung cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: nhân lực CNTT, dịch vụ chuyên nghiệp, phần cứng, phần mềm, chi phí khác, tổng chi phí, dự phòng rủi ro."
        ),
        agent=planning_agent,
        expected_output=(
            "Một bảng tính hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'cost_benefit_analysis'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file XLSX."
        ),
        context=[{
            "description": "Thông tin mô tả cost_benefit_analysis từ người dùng",
            "expected_output": "Tóm tắt các hạng mục chi phí, dự phòng rủi ro...",
            "input": global_context["cost_benefit_analysis"]
        }],
        callback=make_docx_xlsx_callback(
            "Ước lượng chi phí",
            f"{output_base_dir}/1_planning/Cost_Estimating_Worksheet.docx",
            f"{output_base_dir}/1_planning/Cost_Estimating_Worksheet.xlsx",
            shared_memory,
            "cost_estimating_worksheet"
        )
    ))

    # Development Estimating Worksheet
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin cost_benefit_analysis:\n\n"
            f"{global_context['cost_benefit_analysis']}\n\n"
            "Hãy sử dụng dữ liệu trên để tạo bảng tính 'Ước lượng phát triển' (Development Estimating Worksheet) với nội dung cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: nguyên mẫu, giao diện người dùng, báo cáo, cơ sở dữ liệu, tích hợp, máy chủ, tổng hợp chi phí phát triển, phần mềm, hỗ trợ dài hạn."
        ),
        agent=planning_agent,
        expected_output=(
            "Một bảng tính hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'cost_benefit_analysis'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file XLSX."
        ),
        context=[{
            "description": "Thông tin mô tả cost_benefit_analysis từ người dùng",
            "expected_output": "Tóm tắt các hạng mục chi phí phát triển...",
            "input": global_context["cost_benefit_analysis"]
        }],
        callback=make_docx_xlsx_callback(
            "Ước lượng phát triển",
            f"{output_base_dir}/1_planning/Development_Estimating_Worksheet.docx",
            f"{output_base_dir}/1_planning/Development_Estimating_Worksheet.xlsx",
            shared_memory,
            "development_estimating_worksheet"
        )
    ))

    # Capital vs. Expense Costs
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin cost_benefit_analysis:\n\n"
            f"{global_context['cost_benefit_analysis']}\n\n"
            "Hãy sử dụng dữ liệu trên để tạo bảng tính 'Chi phí vốn so với chi phí vận hành' (Project Capital vs. Expense Costs) với nội dung cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: phần cứng, phần mềm, dịch vụ, di chuyển, tổng hợp chi phí vốn và vận hành."
        ),
        agent=planning_agent,
        expected_output=(
            "Một bảng tính hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'cost_benefit_analysis'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file XLSX."
        ),
        context=[{
            "description": "Thông tin mô tả cost_benefit_analysis từ người dùng",
            "expected_output": "Tóm tắt các hạng mục chi phí vốn và vận hành...",
            "input": global_context["cost_benefit_analysis"]
        }],
        callback=make_docx_xlsx_callback(
            "Chi phí vốn vs vận hành",
            f"{output_base_dir}/1_planning/Project_Capital_vs_Expense_Costs.docx",
            f"{output_base_dir}/1_planning/Project_Capital_vs_Expense_Costs.xlsx",
            shared_memory,
            "capital_vs_expense"
        )
    ))

    # Configuration Management Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_charter:\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Dưới đây là thông tin statement_of_work:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch quản lý cấu hình' (Configuration Management Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: đối tượng người dùng, tổ chức quản lý cấu hình, hoạt động & trách nhiệm, hội đồng kiểm soát cấu hình (CCB), kiểm toán cấu hình, phê duyệt kế hoạch."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_charter' và 'statement_of_work'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project_charter từ người dùng",
                "expected_output": "Tóm tắt thông tin về tổ chức, vai trò, trách nhiệm...",
                "input": global_context["project_charter"]
            },
            {
                "description": "Thông tin mô tả statement_of_work từ người dùng",
                "expected_output": "Tóm tắt thông tin về phạm vi, hoạt động, kiểm soát...",
                "input": global_context["statement_of_work"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch quản lý cấu hình",
            f"{output_base_dir}/1_planning/Configuration_Management_Plan.docx",
            shared_memory,
            "config_management_plan"
        )
    ))

    # Risk Information Data Collection Form
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_charter:\n\n"
            f"{global_context['project_charter']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Mẫu thu thập thông tin rủi ro' (Risk Information Data Collection Form) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: nhận dạng rủi ro, phân tích nguyên nhân gốc, đánh giá rủi ro, xem xét và phản hồi."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_charter'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả project_charter từ người dùng",
            "expected_output": "Tóm tắt thông tin về rủi ro, nguyên nhân, đánh giá...",
            "input": global_context["project_charter"]
        }],
        callback=make_docx_callback(
            "Mẫu thu thập thông tin rủi ro",
            f"{output_base_dir}/1_planning/Risk_Information_Data_Collection_Form.docx",
            shared_memory,
            "risk_data_collection"
        )
    ))

    # Risk Analysis Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin risk_data_collection:\n\n"
            f"{global_context['risk_data_collection']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch phân tích rủi ro' (Risk Analysis Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: mục đích dự án, thông tin dự án, bảng phân tích rủi ro (điểm ưu tiên, chiến lược giảm thiểu, kế hoạch dự phòng)."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'risk_data_collection'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả risk_data_collection từ người dùng",
            "expected_output": "Tóm tắt thông tin về rủi ro, phân tích, chiến lược...",
            "input": global_context["risk_data_collection"]
        }],
        callback=make_docx_callback(
            "Kế hoạch phân tích rủi ro",
            f"{output_base_dir}/1_planning/Risk_Analysis_Plan.docx",
            shared_memory,
            "risk_analysis_plan"
        )
    ))

    # Procurement Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_resource_plan:\n\n"
            f"{global_context['project_resource_plan']}\n\n"
            f"Dưới đây là thông tin statement_of_work:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch mua sắm' (Procurement Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: giới thiệu, mục tiêu, thông tin mua sắm (người phụ trách, vật phẩm, rủi ro, thời gian), chiến lược mua sắm (chiến lược giá, phương pháp cạnh tranh, giới hạn ngân sách)."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_resource_plan' và 'statement_of_work'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project_resource_plan từ người dùng",
                "expected_output": "Tóm tắt thông tin về nguồn lực, vật tư, nhân sự...",
                "input": global_context["project_resource_plan"]
            },
            {
                "description": "Thông tin mô tả statement_of_work từ người dùng",
                "expected_output": "Tóm tắt thông tin về phạm vi, mục tiêu, tiến độ...",
                "input": global_context["statement_of_work"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch mua sắm",
            f"{output_base_dir}/1_planning/Procurement_Plan.docx",
            shared_memory,
            "procurement_plan"
        )
    ))

    # Project Organization Chart
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_team_definition:\n\n"
            f"{global_context['project_team_definition']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Sơ đồ tổ chức dự án' (Project Organization Chart) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: sơ đồ tổ chức, người ra quyết định, tổ chức hỗ trợ."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_team_definition'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả project_team_definition từ người dùng",
            "expected_output": "Tóm tắt thông tin về vai trò, tổ chức, hỗ trợ...",
            "input": global_context["project_team_definition"]
        }],
        callback=make_docx_callback(
            "Sơ đồ tổ chức dự án",
            f"{output_base_dir}/1_planning/Project_Organization_Chart.docx",
            shared_memory,
            "project_org_chart"
        )
    ))

    # Roles and Responsibilities Matrix
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_team_definition:\n\n"
            f"{global_context['project_team_definition']}\n\n"
            f"Dưới đây là thông tin statement_of_work:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Ma trận vai trò và trách nhiệm' (Roles and Responsibilities Matrix) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: thiết lập ma trận trách nhiệm, mô tả mẫu vai trò và trách nhiệm, ma trận chuẩn và ma trận theo mô hình RACI."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_team_definition' và 'statement_of_work'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project_team_definition từ người dùng",
                "expected_output": "Tóm tắt thông tin về vai trò, trách nhiệm...",
                "input": global_context["project_team_definition"]
            },
            {
                "description": "Thông tin mô tả statement_of_work từ người dùng",
                "expected_output": "Tóm tắt thông tin về hoạt động, trách nhiệm...",
                "input": global_context["statement_of_work"]
            }
        ],
        callback=make_docx_callback(
            "Ma trận vai trò và trách nhiệm",
            f"{output_base_dir}/1_planning/Roles_and_Responsibilities_Matrix.docx",
            shared_memory,
            "roles_responsibilities_matrix"
        )
    ))

    # Required Approvals Matrix
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_approval:\n\n"
            f"{global_context['project_approval']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Ma trận phê duyệt bắt buộc' (Required Approvals Matrix) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: mục đích của dự án, mô tả mẫu vai trò và trách nhiệm, ma trận phê duyệt."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_approval'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả project_approval từ người dùng",
            "expected_output": "Tóm tắt thông tin về phê duyệt, vai trò, trách nhiệm...",
            "input": global_context["project_approval"]
        }],
        callback=make_docx_callback(
            "Ma trận phê duyệt bắt buộc",
            f"{output_base_dir}/1_planning/Required_Approvals_Matrix.docx",
            shared_memory,
            "required_approvals_matrix"
        )
    ))

    # Activity Worksheet in WBS Dictionary Form
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin statement_of_work:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Bảng công việc theo dạng từ điển WBS' (Activity Worksheet in Work Breakdown Structure Dictionary Form) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: số nhiệm vụ, mô tả, hoạt động cụ thể, mục tiêu, tiêu chí chấp nhận, giả định, kỹ năng, tài nguyên, vật tư, ước lượng thời gian, chi phí, quan hệ phụ thuộc trước/sau, phê duyệt."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'statement_of_work'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả statement_of_work từ người dùng",
            "expected_output": "Tóm tắt thông tin về nhiệm vụ, mục tiêu, kỹ năng...",
            "input": global_context["statement_of_work"]
        }],
        callback=make_docx_callback(
            "Bảng công việc theo dạng từ điển WBS",
            f"{output_base_dir}/1_planning/Activity_Worksheet_WBS_Dictionary.docx",
            shared_memory,
            "activity_worksheet"
        )
    ))

    # WBS Resource Planning Template
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_resource_plan:\n\n"
            f"{global_context['project_resource_plan']}\n\n"
            f"Dưới đây là thông tin activity_worksheet:\n\n"
            f"{global_context['activity_worksheet']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Mẫu lập kế hoạch nguồn lực WBS' (Work Breakdown Structure Resource Planning Template) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: kỹ năng cần thiết, ước lượng thời gian, phân bổ tài nguyên."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_resource_plan' và 'activity_worksheet'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project_resource_plan từ người dùng",
                "expected_output": "Tóm tắt thông tin về nguồn lực, kỹ năng...",
                "input": global_context["project_resource_plan"]
            },
            {
                "description": "Thông tin mô tả activity_worksheet từ người dùng",
                "expected_output": "Tóm tắt thông tin về nhiệm vụ, thời gian...",
                "input": global_context["activity_worksheet"]
            }
        ],
        callback=make_docx_callback(
            "Mẫu lập kế hoạch nguồn lực WBS",
            f"{output_base_dir}/1_planning/WBS_Resource_Planning_Template.docx",
            shared_memory,
            "wbs_resource_planning"
        )
    ))

    # Work Breakdown Structure (WBS)
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin activity_worksheet:\n\n"
            f"{global_context['activity_worksheet']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Cấu trúc phân chia công việc' (Work Breakdown Structure - WBS) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: tên dự án, bộ phận, mã công việc, mô tả, người/nhóm phụ trách, thời hạn hoàn thành."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'activity_worksheet'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả activity_worksheet từ người dùng",
            "expected_output": "Tóm tắt thông tin về công việc, mã, người phụ trách...",
            "input": global_context["activity_worksheet"]
        }],
        callback=make_docx_callback(
            "Cấu trúc phân chia công việc",
            f"{output_base_dir}/1_planning/Work_Breakdown_Structure.docx",
            shared_memory,
            "wbs"
        )
    ))

    # COBIT Checklist and Review
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_charter:\n\n"
            f"{global_context['project_charter']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Danh sách kiểm tra và đánh giá COBIT' (COBIT Checklist and Review) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: mục tiêu kiểm soát COBIT, tóm tắt thành phần và quy trình COBIT, các nhóm chính (Lập kế hoạch, Triển khai, Hỗ trợ, Giám sát)."
        ),
        agent=researcher_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_charter'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả project_charter từ người dùng",
            "expected_output": "Tóm tắt thông tin về kiểm soát, quy trình, nhóm COBIT...",
            "input": global_context["project_charter"]
        }],
        callback=make_docx_callback(
            "Danh sách kiểm tra và đánh giá COBIT",
            f"{output_base_dir}/1_planning/COBIT_Checklist_and_Review.docx",
            shared_memory,
            "cobit_checklist"
        )
    ))

    # Request For Information
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin statement_of_work:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Yêu cầu thông tin' (Request For Information - RFI) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: mục đích, quy trình RFI, hồ sơ doanh nghiệp, tính năng kỹ thuật sản phẩm, thông tin định giá và chi phí vòng đời."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'statement_of_work'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả statement_of_work từ người dùng",
            "expected_output": "Tóm tắt thông tin về mục tiêu, quy trình, tính năng...",
            "input": global_context["statement_of_work"]
        }],
        callback=make_docx_callback(
            "Yêu cầu thông tin",
            f"{output_base_dir}/1_planning/Request_For_Information.docx",
            shared_memory,
            "rfi"
        )
    ))

    # Root Cause Analysis
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin risk_data_collection:\n\n"
            f"{global_context['risk_data_collection']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Phân tích nguyên nhân gốc rễ' (Root Cause Analysis) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: tóm tắt, thời gian xảy ra, phòng ban, ứng dụng bị ảnh hưởng, chuỗi sự kiện, hành động đề xuất."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'risk_data_collection'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả risk_data_collection từ người dùng",
            "expected_output": "Tóm tắt thông tin về sự cố, nguyên nhân, giải pháp...",
            "input": global_context["risk_data_collection"]
        }],
        callback=make_docx_callback(
            "Phân tích nguyên nhân gốc rễ",
            f"{output_base_dir}/1_planning/Root_Cause_Analysis.docx",
            shared_memory,
            "root_cause_analysis"
        )
    ))

    # Project Plan
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin project_charter:\n\n"
            f"{global_context['project_charter']}\n\n"
            f"Dưới đây là thông tin statement_of_work:\n\n"
            f"{global_context['statement_of_work']}\n\n"
            f"Dưới đây là thông tin wbs:\n\n"
            f"{global_context['wbs']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Kế hoạch dự án' (Project Plan) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: sản phẩm chính, mốc thời gian, hoạt động, nguồn lực, áp dụng theo các giai đoạn SDLC."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'project_charter', 'statement_of_work', và 'wbs'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[
            {
                "description": "Thông tin mô tả project_charter từ người dùng",
                "expected_output": "Tóm tắt thông tin về mục tiêu, nguồn lực...",
                "input": global_context["project_charter"]
            },
            {
                "description": "Thông tin mô tả statement_of_work từ người dùng",
                "expected_output": "Tóm tắt thông tin về sản phẩm, hoạt động...",
                "input": global_context["statement_of_work"]
            },
            {
                "description": "Thông tin mô tả wbs từ người dùng",
                "expected_output": "Tóm tắt thông tin về công việc, lịch trình...",
                "input": global_context["wbs"]
            }
        ],
        callback=make_docx_callback(
            "Kế hoạch dự án",
            f"{output_base_dir}/1_planning/Project_Plan.docx",
            shared_memory,
            "project_plan"
        )
    ))

    # List of Opportunities Summary
    tasks.append(Task(
        description=(
            f"Dưới đây là thông tin business_case:\n\n"
            f"{global_context['business_case']}\n\n"
            "Hãy sử dụng dữ liệu trên để viết tài liệu 'Tổng hợp danh sách cơ hội' (List of Opportunities Summary) với nội dung hoàn chỉnh, cụ thể, không để trống bất kỳ phần nào. "
            "Không được tạo template hoặc hướng dẫn, mà phải điền nội dung thực tế cho từng mục: mô tả, mức độ ưu tiên, ngày giao, người phụ trách, ghi chú."
        ),
        agent=planning_agent,
        expected_output=(
            "Một văn bản hoàn chỉnh, nội dung đã được điền đầy đủ dựa trên dữ liệu thực tế trong 'business_case'. "
            "Không phải template mẫu, không có placeholder hay dấu ngoặc (). Sẵn sàng để chuyển sang file DOCX."
        ),
        context=[{
            "description": "Thông tin mô tả business_case từ người dùng",
            "expected_output": "Tóm tắt thông tin về cơ hội, mức độ ưu tiên, người phụ trách...",
            "input": global_context["business_case"]
        }],
        callback=make_docx_callback(
            "Tổng hợp danh sách cơ hội",
            f"{output_base_dir}/1_planning/List_of_Opportunities_Summary.docx",
            shared_memory,
            "opportunities_summary"
        )
    ))

    return tasks
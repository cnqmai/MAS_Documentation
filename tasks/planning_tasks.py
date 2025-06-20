from crewai import Task
from utils.output_formats import create_docx, create_xlsx
from memory.shared_memory import SharedMemory
import os

def create_planning_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, planning_agent):
    """
    Tạo các tác vụ cho giai đoạn Lập kế hoạch (Planning Phase).
    """
    tasks = []

    # Tác vụ tạo Project Management Office (PMO) Checklist
    pmo_checklist_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Danh sách kiểm tra PMO (Project Management Office Checklist) dựa trên dữ liệu từ `project_charter` trong SharedMemory. "
            "Tài liệu này kiểm tra xem PMO có cung cấp đầy đủ chức năng và công cụ cần thiết để hỗ trợ ban điều hành và các quản lý dự án không. "
            "Nội dung phải bao gồm: mục tiêu, đối tượng, trách nhiệm tổ chức, bộ công cụ PMO, dữ liệu cần thiết, giao diện hỗ trợ. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `PMO_Checklist.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `pmo_checklist`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `PMO_Checklist.docx` chứa danh sách kiểm tra PMO, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `pmo_checklist`."
        ),
        callback=lambda output: create_docx(
            "Danh sách kiểm tra PMO",
            [
                "1. Mục tiêu: Mục đích và vai trò của PMO trong dự án (lấy từ project_charter).",
                "2. Đối tượng: Các bên liên quan sử dụng PMO.",
                "3. Trách nhiệm tổ chức: Vai trò và trách nhiệm của PMO.",
                "4. Bộ công cụ PMO: Các công cụ và dữ liệu cần thiết để hỗ trợ dự án.",
                shared_memory.load("project_charter") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/PMO_Checklist.docx"
        ) and shared_memory.save("pmo_checklist", output)
    )

    # Tác vụ tạo Statement of Work
    statement_of_work_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Tuyên bố công việc (Statement of Work) dựa trên dữ liệu từ `project_charter` và `business_case` trong SharedMemory. "
            "Tài liệu này mô tả phạm vi công việc chi tiết, thời lượng và sản phẩm đầu ra để tất cả bên liên quan cùng hiểu rõ. "
            "Nội dung phải bao gồm: mục tiêu kinh doanh, mô tả dự án, ước lượng tiến độ, chi phí, nguồn lực, kiểm soát dự án (rủi ro, vấn đề, thay đổi). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Statement_of_Work.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `statement_of_work`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `Statement_of_Work.docx` chứa tuyên bố công việc, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `statement_of_work`."
        ),
        callback=lambda output: create_docx(
            "Tuyên bố công việc",
            [
                "1. Mục tiêu kinh doanh: Mục tiêu chính của dự án (lấy từ business_case).",
                "2. Mô tả dự án: Phạm vi và sản phẩm đầu ra (lấy từ project_charter).",
                "3. Ước lượng: Tiến độ, chi phí, và nguồn lực cần thiết.",
                "4. Kiểm soát dự án: Quản lý rủi ro, vấn đề, và thay đổi.",
                shared_memory.load("project_charter") or "Không có dữ liệu",
                shared_memory.load("business_case") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Statement_of_Work.docx"
        ) and shared_memory.save("statement_of_work", output)
    )

    # Tác vụ tạo Project Approval Document
    project_approval_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Phê duyệt dự án (Project Approval Document) dựa trên dữ liệu từ `project_charter` và `business_case` trong SharedMemory. "
            "Tài liệu này là văn bản phê duyệt chính thức dự án bởi nhà tài trợ và các bên liên quan. "
            "Nội dung phải bao gồm: tổng quan, mô tả dự án, thông tin phê duyệt (người phụ trách, chữ ký, ngày tháng). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Project_Approval_Document.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `project_approval`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `Project_Approval_Document.docx` chứa thông tin phê duyệt dự án, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `project_approval`."
        ),
        callback=lambda output: create_docx(
            "Phê duyệt dự án",
            [
                "1. Tổng quan: Mô tả ngắn gọn về dự án (lấy từ project_charter).",
                "2. Mô tả dự án: Mục tiêu và phạm vi (lấy từ business_case).",
                "3. Thông tin phê duyệt: Người phụ trách, chữ ký, và ngày tháng.",
                shared_memory.load("project_charter") or "Không có dữ liệu",
                shared_memory.load("business_case") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Project_Approval_Document.docx"
        ) and shared_memory.save("project_approval", output)
    )

    # Tác vụ tạo Cost Estimating Worksheet
    cost_estimating_worksheet_task = Task(
        description=(
            "Sử dụng công cụ `create_xlsx` để tạo bảng tính Ước lượng chi phí (Cost Estimating Worksheet) dựa trên dữ liệu từ `cost_benefit_analysis` trong SharedMemory. "
            "Bảng tính này giúp ước lượng và lập ngân sách các chi phí CNTT, bao gồm nhân lực CNTT, dịch vụ chuyên nghiệp, phần cứng, phần mềm, chi phí khác, công thức tự động tính tổng, dự phòng rủi ro và tổng chi phí. "
            "Lưu bảng tính dưới dạng `.xlsx` trong thư mục `output/1_planning` với tên `Cost_Estimating_Worksheet.xlsx`. "
            "Lưu kết quả vào SharedMemory với khóa `cost_estimating_worksheet`."
        ),
        agent=planning_agent,
        expected_output=(
            "Bảng tính `Cost_Estimating_Worksheet.xlsx` chứa ước lượng chi phí, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `cost_estimating_worksheet`."
        ),
        callback=lambda output: create_xlsx(
            [
                ["Category", "Description", "Estimated Cost", "Risk Contingency"],
                ["Personnel", "IT labor costs", "TBD", "TBD"],
                ["Services", "Professional services", "TBD", "TBD"],
                ["Hardware", "Hardware costs", "TBD", "TBD"],
                ["Software", "Software licenses", "TBD", "TBD"],
                ["Other", "Miscellaneous costs", "TBD", "TBD"],
                ["Total", "", "=SUM(C2:C5)", "=SUM(D2:D5)"]
            ],
            f"{output_base_dir}/1_planning/Cost_Estimating_Worksheet.xlsx"
        ) and shared_memory.save("cost_estimating_worksheet", output)
    )

    # Tác vụ tạo Development Estimating Worksheet
    development_estimating_worksheet_task = Task(
        description=(
            "Sử dụng công cụ `create_xlsx` để tạo bảng tính Ước lượng phát triển (Development Estimating Worksheet) dựa trên dữ liệu từ `cost_benefit_analysis` trong SharedMemory. "
            "Bảng tính này ước lượng chi phí phát triển, bao gồm nguyên mẫu, giao diện người dùng, báo cáo, cơ sở dữ liệu, tích hợp, máy tính chi phí máy chủ, tổng hợp chi phí phát triển, phần mềm, hỗ trợ dài hạn. "
            "Lưu bảng tính dưới dạng `.xlsx` trong thư mục `output/1_planning` với tên `Development_Estimating_Worksheet.xlsx`. "
            "Lưu kết quả vào SharedMemory với khóa `development_estimating_worksheet`."
        ),
        agent=planning_agent,
        expected_output=(
            "Bảng tính `Development_Estimating_Worksheet.xlsx` chứa ước lượng chi phí phát triển, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `development_estimating_worksheet`."
        ),
        callback=lambda output: create_xlsx(
            [
                ["Category", "Description", "Estimated Cost"],
                ["Prototype", "Development of prototypes", "TBD"],
                ["UI", "User interface development", "TBD"],
                ["Database", "Database design and implementation", "TBD"],
                ["Integration", "System integration", "TBD"],
                ["Servers", "Server costs (Windows, SQL, etc.)", "TBD"],
                ["Total", "", "=SUM(C2:C6)"]
            ],
            f"{output_base_dir}/1_planning/Development_Estimating_Worksheet.xlsx"
        ) and shared_memory.save("development_estimating_worksheet", output)
    )

    # Tác vụ tạo Project Capital vs. Expense Costs
    capital_vs_expense_task = Task(
        description=(
            "Sử dụng công cụ `create_xlsx` để tạo bảng tính Chi phí vốn so với chi phí vận hành (Project Capital vs. Expense Costs) dựa trên dữ liệu từ `cost_benefit_analysis` trong SharedMemory. "
            "Bảng tính này ước lượng chi phí vốn và chi phí vận hành (bao gồm phần cứng, phần mềm, dịch vụ, di chuyển) và theo dõi so với ngân sách. "
            "Lưu bảng tính dưới dạng `.xlsx` trong thư mục `output/1_planning` với tên `Project_Capital_vs_Expense_Costs.xlsx`. "
            "Lưu kết quả vào SharedMemory với khóa `capital_vs_expense`."
        ),
        agent=planning_agent,
        expected_output=(
            "Bảng tính `Project_Capital_vs_Expense_Costs.xlsx` chứa ước lượng chi phí vốn và vận hành, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `capital_vs_expense`."
        ),
        callback=lambda output: create_xlsx(
            [
                ["Category", "Capital Cost", "Expense Cost", "Total"],
                ["Hardware", "TBD", "TBD", "=B2+C2"],
                ["Software", "TBD", "TBD", "=B3+C3"],
                ["Services", "TBD", "TBD", "=B4+C4"],
                ["Migration", "TBD", "TBD", "=B5+C5"],
                ["Total", "=SUM(B2:B5)", "=SUM(C2:C5)", "=SUM(D2:D5)"]
            ],
            f"{output_base_dir}/1_planning/Project_Capital_vs_Expense_Costs.xlsx"
        ) and shared_memory.save("capital_vs_expense", output)
    )

    # Tác vụ tạo Configuration Management Plan
    config_management_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Kế hoạch quản lý cấu hình (Configuration Management Plan) dựa trên dữ liệu từ `project_charter` và `statement_of_work` trong SharedMemory. "
            "Tài liệu này trình bày cách quản lý cấu hình (CM) trong dự án, công cụ sử dụng, quy trình áp dụng và cách đạt được thành công. "
            "Nội dung phải bao gồm: đối tượng người dùng, tổ chức quản lý cấu hình, hoạt động & trách nhiệm, hội đồng kiểm soát cấu hình (CCB), kiểm toán cấu hình, phê duyệt kế hoạch. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Configuration_Management_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `config_management_plan`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `Configuration_Management_Plan.docx` chứa kế hoạch quản lý cấu hình, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `config_management_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch quản lý cấu hình",
            [
                "1. Đối tượng người dùng: Các bên sử dụng kế hoạch (lấy từ project_charter).",
                "2. Tổ chức quản lý: Cơ cấu tổ chức quản lý cấu hình.",
                "3. Hoạt động & trách nhiệm: Các hoạt động và vai trò liên quan.",
                "4. Hội đồng kiểm soát cấu hình: Vai trò và quy trình của CCB.",
                "5. Kiểm toán cấu hình: Quy trình kiểm tra cấu hình.",
                shared_memory.load("project_charter") or "Không có dữ liệu",
                shared_memory.load("statement_of_work") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Configuration_Management_Plan.docx"
        ) and shared_memory.save("config_management_plan", output)
    )

    # Tác vụ tạo Risk Information Data Collection Form
    risk_data_collection_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Mẫu thu thập thông tin rủi ro (Risk Information Data Collection Form) dựa trên dữ liệu từ `project_charter` trong SharedMemory. "
            "Tài liệu này thu thập thông tin chi tiết về rủi ro từ nhiều nguồn trong quá trình dự án để phân tích và đưa vào Kế hoạch phân tích rủi ro. "
            "Nội dung phải bao gồm: nhận dạng rủi ro, phân tích nguyên nhân gốc, đánh giá rủi ro, xem xét và phản hồi. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Risk_Information_Data_Collection_Form.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `risk_data_collection`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `Risk_Information_Data_Collection_Form.docx` chứa mẫu thu thập thông tin rủi ro, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `risk_data_collection`."
        ),
        callback=lambda output: create_docx(
            "Mẫu thu thập thông tin rủi ro",
            [
                "1. Nhận dạng rủi ro: Danh sách các rủi ro tiềm năng (lấy từ project_charter).",
                "2. Phân tích nguyên nhân gốc: Nguyên nhân của từng rủi ro.",
                "3. Đánh giá rủi ro: Mức độ nghiêm trọng và xác suất xảy ra.",
                "4. Xem xét và phản hồi: Các biện pháp giảm thiểu và phản hồi.",
                shared_memory.load("project_charter") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Risk_Information_Data_Collection_Form.docx"
        ) and shared_memory.save("risk_data_collection", output)
    )

    # Tác vụ tạo Risk Analysis Plan
    risk_analysis_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Kế hoạch phân tích rủi ro (Risk Analysis Plan) dựa trên dữ liệu từ `risk_data_collection` trong SharedMemory. "
            "Tài liệu này cung cấp phương tiện để ghi lại phân tích rủi ro dự án và theo dõi những rủi ro có thể ảnh hưởng đến thành công hoặc tiến độ. "
            "Nội dung phải bao gồm: mục đích dự án, thông tin dự án, bảng phân tích rủi ro (điểm ưu tiên, chiến lược giảm thiểu, kế hoạch dự phòng). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Risk_Analysis_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `risk_analysis_plan`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `Risk_Analysis_Plan.docx` chứa kế hoạch phân tích rủi ro, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `risk_analysis_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch phân tích rủi ro",
            [
                "1. Mục đích dự án: Tổng quan về dự án và rủi ro (lấy từ risk_data_collection).",
                "2. Thông tin dự án: Bối cảnh và phạm vi rủi ro.",
                "3. Bảng phân tích rủi ro: Điểm ưu tiên, chiến lược giảm thiểu, kế hoạch dự phòng.",
                shared_memory.load("risk_data_collection") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Risk_Analysis_Plan.docx"
        ) and shared_memory.save("risk_analysis_plan", output)
    )

    # Tác vụ tạo Procurement Plan
    procurement_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Kế hoạch mua sắm (Procurement Plan) dựa trên dữ liệu từ `project_resource_plan` và `statement_of_work` trong SharedMemory. "
            "Tài liệu này xác định quy trình và thông tin để mua sắm phần cứng, phần mềm, nhà cung cấp hoặc các mục cần thiết khác. "
            "Nội dung phải bao gồm: giới thiệu, mục tiêu, thông tin mua sắm (người phụ trách, vật phẩm, rủi ro, thời gian), chiến lược mua sắm (chiến lược giá, phương pháp cạnh tranh, giới hạn ngân sách). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Procurement_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `procurement_plan`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `Procurement_Plan.docx` chứa kế hoạch mua sắm, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `procurement_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch mua sắm",
            [
                "1. Giới thiệu: Mục đích và phạm vi mua sắm (lấy từ statement_of_work).",
                "2. Thông tin mua sắm: Người phụ trách, vật phẩm, rủi ro, thời gian (lấy từ project_resource_plan).",
                "3. Chiến lược mua sắm: Chiến lược giá, phương pháp cạnh tranh, giới hạn ngân sách.",
                shared_memory.load("project_resource_plan") or "Không có dữ liệu",
                shared_memory.load("statement_of_work") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Procurement_Plan.docx"
        ) and shared_memory.save("procurement_plan", output)
    )

    # Tác vụ tạo Project Organization Chart
    project_org_chart_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Sơ đồ tổ chức dự án (Project Organization Chart) dựa trên dữ liệu từ `project_team_definition` trong SharedMemory. "
            "Sơ đồ tổ chức thể hiện các 'người ra quyết định' chính trong dự án, bao gồm PMO, nhà tài trợ, các bên liên quan, phân tích nghiệp vụ, tổ chức hỗ trợ như hạ tầng, thiết kế, QA. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Project_Organization_Chart.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `project_org_chart`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `Project_Organization_Chart.docx` chứa sơ đồ tổ chức dự án, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `project_org_chart`."
        ),
        callback=lambda output: create_docx(
            "Sơ đồ tổ chức dự án",
            [
                "1. Sơ đồ tổ chức: Hiển thị các vai trò và mối quan hệ trong dự án (lấy từ project_team_definition).",
                "2. Người ra quyết định: PMO, nhà tài trợ, các bên liên quan chính.",
                "3. Tổ chức hỗ trợ: Hạ tầng, thiết kế, QA, v.v.",
                shared_memory.load("project_team_definition") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Project_Organization_Chart.docx"
        ) and shared_memory.save("project_org_chart", output)
    )

    # Tác vụ tạo Roles and Responsibilities Matrix
    roles_responsibilities_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Ma trận vai trò và trách nhiệm (Roles and Responsibilities Matrix) dựa trên dữ liệu từ `project_team_definition` và `statement_of_work` trong SharedMemory. "
            "Tài liệu hiển thị các hoạt động chính của dự án và chi tiết trách nhiệm của từng cá nhân hoặc vai trò trong từng phòng ban chức năng, sử dụng mô hình RACI. "
            "Nội dung phải bao gồm: thiết lập ma trận trách nhiệm, mô tả mẫu vai trò và trách nhiệm, ma trận chuẩn và ma trận theo mô hình RACI. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Roles_and_Responsibilities_Matrix.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `roles_responsibilities_matrix`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `Roles_and_Responsibilities_Matrix.docx` chứa ma trận vai trò và trách nhiệm, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `roles_responsibilities_matrix`."
        ),
        callback=lambda output: create_docx(
            "Ma trận vai trò và trách nhiệm",
            [
                "1. Thiết lập ma trận: Tổng quan về các hoạt động và vai trò (lấy từ project_team_definition).",
                "2. Mô tả vai trò: Chi tiết trách nhiệm của từng vai trò (lấy từ statement_of_work).",
                "3. Ma trận RACI: Phân bổ Responsible, Accountable, Consulted, Informed.",
                shared_memory.load("project_team_definition") or "Không có dữ liệu",
                shared_memory.load("statement_of_work") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Roles_and_Responsibilities_Matrix.docx"
        ) and shared_memory.save("roles_responsibilities_matrix", output)
    )

    # Tác vụ tạo Required Approvals Matrix
    required_approvals_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Ma trận phê duyệt bắt buộc (Required Approvals Matrix) dựa trên dữ liệu từ `project_approval` trong SharedMemory. "
            "Ma trận này thể hiện các hoạt động chính của dự án (chức năng, nhiệm vụ, tài liệu hoặc giai đoạn) và người chịu trách nhiệm phê duyệt chúng, bao gồm các tài liệu như Business Case, Feasibility Study, Cost/Benefit Analysis, Project Charter, Project Approval Document, Functional & Technical Requirements, Requirements Traceability Matrix, Project Plan, Training Plan, thiết kế, hướng dẫn sử dụng, kế hoạch kiểm thử, tài liệu chuyển giao sản phẩm, phân tích phản hồi, yêu cầu thay đổi. "
            "Nội dung phải bao gồm: mục đích của dự án, mô tả mẫu vai trò và trách nhiệm, ma trận phê duyệt. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Required_Approvals_Matrix.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `required_approvals_matrix`."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Tài liệu `Required_Approvals_Matrix.docx` chứa ma trận phê duyệt bắt buộc, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `required_approvals_matrix`."
        ),
        callback=lambda output: create_docx(
            "Ma trận phê duyệt bắt buộc",
            [
                "1. Mục đích dự án: Tổng quan về các hoạt động cần phê duyệt (lấy từ project_approval).",
                "2. Mô tả vai trò: Người chịu trách nhiệm phê duyệt cho từng tài liệu hoặc giai đoạn.",
                "3. Ma trận phê duyệt: Danh sách các tài liệu và người phê duyệt (Business Case, Feasibility Study, Project Charter, v.v.).",
                shared_memory.load("project_approval") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Required_Approvals_Matrix.docx"
        ) and shared_memory.save("required_approvals_matrix", output)
    )

    # Tác vụ tạo Activity Worksheet in Work Breakdown Structure Dictionary Form
    activity_worksheet_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Bảng công việc theo dạng từ điển WBS (Activity Worksheet in Work Breakdown Structure Dictionary Form) dựa trên dữ liệu từ `statement_of_work` trong SharedMemory. "
            "Tài liệu này cho phép chuyên gia (SME) định nghĩa chi tiết công việc và nhiệm vụ trong WBS, bao gồm: số nhiệm vụ, mô tả, hoạt động cụ thể, mục tiêu, tiêu chí chấp nhận, giả định, kỹ năng, tài nguyên, vật tư, ước lượng thời gian, chi phí, quan hệ phụ thuộc trước/sau, phê duyệt. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Activity_Worksheet_WBS_Dictionary.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `activity_worksheet`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `Activity_Worksheet_WBS_Dictionary.docx` chứa bảng công việc WBS, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `activity_worksheet`."
        ),
        callback=lambda output: create_docx(
            "Bảng công việc theo dạng từ điển WBS",
            [
                "1. Số nhiệm vụ: Danh sách các nhiệm vụ trong WBS (lấy từ statement_of_work).",
                "2. Mô tả: Chi tiết công việc và mục tiêu.",
                "3. Tiêu chí chấp nhận: Điều kiện để hoàn thành nhiệm vụ.",
                "4. Tài nguyên và kỹ năng: Yêu cầu về nhân sự, vật tư, thời gian, chi phí.",
                "5. Quan hệ phụ thuộc: Các nhiệm vụ trước/sau.",
                shared_memory.load("statement_of_work") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Activity_Worksheet_WBS_Dictionary.docx"
        ) and shared_memory.save("activity_worksheet", output)
    )

    # Tác vụ tạo Work Breakdown Structure Resource Planning Template
    wbs_resource_planning_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Mẫu lập kế hoạch nguồn lực WBS (Work Breakdown Structure Resource Planning Template) dựa trên dữ liệu từ `project_resource_plan` và `activity_worksheet` trong SharedMemory. "
            "Mẫu này ước lượng thời gian công việc và kỹ năng cần thiết, bao gồm quản lý dự án, BA, kiến trúc sư, phát triển phần mềm/giao diện/cơ sở dữ liệu, kiểm thử. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `WBS_Resource_Planning_Template.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `wbs_resource_planning`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `WBS_Resource_Planning_Template.docx` chứa mẫu lập kế hoạch nguồn lực WBS, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `wbs_resource_planning`."
        ),
        callback=lambda output: create_docx(
            "Mẫu lập kế hoạch nguồn lực WBS",
            [
                "1. Kỹ năng cần thiết: Quản lý dự án, BA, phát triển, kiểm thử, v.v. (lấy từ project_resource_plan).",
                "2. Ước lượng thời gian: Thời gian cần thiết cho từng nhiệm vụ (lấy từ activity_worksheet).",
                "3. Phân bổ tài nguyên: Cách phân bổ nhân sự và vật tư.",
                shared_memory.load("project_resource_plan") or "Không có dữ liệu",
                shared_memory.load("activity_worksheet") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/WBS_Resource_Planning_Template.docx"
        ) and shared_memory.save("wbs_resource_planning", output)
    )

    # Tác vụ tạo Work Breakdown Structure (WBS)
    wbs_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Cấu trúc phân chia công việc (Work Breakdown Structure - WBS) dựa trên dữ liệu từ `activity_worksheet` trong SharedMemory. "
            "WBS chia nhỏ dự án thành các giai đoạn, sản phẩm và công việc để hỗ trợ lập chi phí, lịch trình và kiểm soát. "
            "Nội dung phải bao gồm: tên dự án, bộ phận, mã công việc, mô tả, người/nhóm phụ trách, thời hạn hoàn thành. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Work_Breakdown_Structure.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `wbs`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `Work_Breakdown_Structure.docx` chứa cấu trúc phân chia công việc, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `wbs`."
        ),
        callback=lambda output: create_docx(
            "Cấu trúc phân chia công việc",
            [
                "1. Tên dự án: Tên và bối cảnh dự án (lấy từ activity_worksheet).",
                "2. Mã công việc: Danh sách mã và mô tả công việc.",
                "3. Người phụ trách: Nhóm hoặc cá nhân chịu trách nhiệm.",
                "4. Thời hạn: Thời gian hoàn thành từng công việc.",
                shared_memory.load("activity_worksheet") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Work_Breakdown_Structure.docx"
        ) and shared_memory.save("wbs", output)
    )

    # Tác vụ tạo COBIT Checklist and Review
    cobit_checklist_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Danh sách kiểm tra và đánh giá COBIT (COBIT Checklist and Review) dựa trên dữ liệu từ `project_charter` trong SharedMemory. "
            "COBIT là bộ tiêu chuẩn kiểm soát CNTT theo Luật Sarbanes-Oxley, cung cấp mô hình quản trị CNTT chuẩn hóa. "
            "Nội dung phải bao gồm: mục tiêu kiểm soát COBIT, tóm tắt thành phần và quy trình COBIT, các nhóm chính (Lập kế hoạch, Triển khai, Hỗ trợ, Giám sát). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `COBIT_Checklist_and_Review.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `cobit_checklist`."
        ),
        agent=researcher_agent,
        expected_output=(
            "Tài liệu `COBIT_Checklist_and_Review.docx` chứa danh sách kiểm tra COBIT, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `cobit_checklist`."
        ),
        callback=lambda output: create_docx(
            "Danh sách kiểm tra và đánh giá COBIT",
            [
                "1. Mục tiêu kiểm soát: Các mục tiêu COBIT liên quan đến dự án (lấy từ project_charter).",
                "2. Thành phần COBIT: Tóm tắt các quy trình COBIT.",
                "3. Nhóm chính: Lập kế hoạch, Triển khai, Hỗ trợ, Giám sát.",
                shared_memory.load("project_charter") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/COBIT_Checklist_and_Review.docx"
        ) and shared_memory.save("cobit_checklist", output)
    )

    # Tác vụ tạo Request For Information
    rfi_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Yêu cầu thông tin (Request For Information - RFI) dựa trên dữ liệu từ `statement_of_work` trong SharedMemory. "
            "Tài liệu này yêu cầu thông tin từ nhà cung cấp về sản phẩm/dịch vụ nhằm giúp đưa ra quyết định tiếp theo. "
            "Nội dung phải bao gồm: mục đích, quy trình RFI, hồ sơ doanh nghiệp, tính năng kỹ thuật sản phẩm, thông tin định giá và chi phí vòng đời. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Request_For_Information.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `rfi`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `Request_For_Information.docx` chứa yêu cầu thông tin, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `rfi`."
        ),
        callback=lambda output: create_docx(
            "Yêu cầu thông tin",
            [
                "1. Mục đích: Mục tiêu của RFI (lấy từ statement_of_work).",
                "2. Quy trình RFI: Các bước để thu thập thông tin từ nhà cung cấp.",
                "3. Hồ sơ doanh nghiệp: Yêu cầu thông tin về nhà cung cấp.",
                "4. Tính năng kỹ thuật: Yêu cầu chi tiết về sản phẩm/dịch vụ.",
                "5. Định giá: Thông tin chi phí và chi phí vòng đời.",
                shared_memory.load("statement_of_work") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Request_For_Information.docx"
        ) and shared_memory.save("rfi", output)
    )

    # Tác vụ tạo Root Cause Analysis
    root_cause_analysis_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Phân tích nguyên nhân gốc rễ (Root Cause Analysis) dựa trên dữ liệu từ `risk_data_collection` trong SharedMemory. "
            "Tài liệu này xác định nguyên nhân gốc rễ của sự cố và khuyến nghị cách giải quyết. "
            "Nội dung phải bao gồm: tóm tắt, thời gian xảy ra, phòng ban, ứng dụng bị ảnh hưởng, chuỗi sự kiện, hành động đề xuất. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Root_Cause_Analysis.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `root_cause_analysis`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `Root_Cause_Analysis.docx` chứa phân tích nguyên nhân gốc rễ, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `root_cause_analysis`."
        ),
        callback=lambda output: create_docx(
            "Phân tích nguyên nhân gốc rễ",
            [
                "1. Tóm tắt: Tổng quan về sự cố (lấy từ risk_data_collection).",
                "2. Thời gian xảy ra: Thời điểm xảy ra sự cố.",
                "3. Phòng ban và ứng dụng: Các phòng ban và hệ thống bị ảnh hưởng.",
                "4. Chuỗi sự kiện: Diễn biến dẫn đến sự cố.",
                "5. Hành động đề xuất: Giải pháp để giải quyết và ngăn chặn.",
                shared_memory.load("risk_data_collection") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Root_Cause_Analysis.docx"
        ) and shared_memory.save("root_cause_analysis", output)
    )

    # Tác vụ tạo Project Plan
    project_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Kế hoạch dự án (Project Plan) dựa trên dữ liệu từ `project_charter`, `statement_of_work`, và `wbs` trong SharedMemory. "
            "Tài liệu này lập kế hoạch thực thi và kiểm soát dự án, gồm sản phẩm chính, mốc thời gian, hoạt động, nguồn lực, áp dụng theo các giai đoạn SDLC (Khởi tạo, Lập kế hoạch, Xác định yêu cầu, Thiết kế hệ thống, Phát triển, Kiểm thử, Triển khai, Kết thúc). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `Project_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `project_plan`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `Project_Plan.docx` chứa kế hoạch dự án, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `project_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch dự án",
            [
                "1. Sản phẩm chính: Các sản phẩm đầu ra của dự án (lấy từ statement_of_work).",
                "2. Mốc thời gian: Lịch trình theo giai đoạn SDLC (lấy từ wbs).",
                "3. Hoạt động: Danh sách các hoạt động chính (lấy từ wbs).",
                "4. Nguồn lực: Phân bổ tài nguyên (lấy từ project_charter).",
                shared_memory.load("project_charter") or "Không có dữ liệu",
                shared_memory.load("statement_of_work") or "Không có dữ liệu",
                shared_memory.load("wbs") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/Project_Plan.docx"
        ) and shared_memory.save("project_plan", output)
    )

    # Tác vụ tạo List of Opportunities Summary
    opportunities_summary_task = Task(
        description=(
            "Sử dụng công cụ `create_project_plan_document` để tạo tài liệu Tổng hợp danh sách cơ hội (List of Opportunities Summary) dựa trên dữ liệu từ `business_case` trong SharedMemory. "
            "Tài liệu này tổng hợp các cơ hội dự án, bao gồm: mô tả, mức độ ưu tiên, ngày giao, người phụ trách, ghi chú. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/1_planning` với tên `List_of_Opportunities_Summary.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `opportunities_summary`."
        ),
        agent=planning_agent,
        expected_output=(
            "Tài liệu `List_of_Opportunities_Summary.docx` chứa tổng hợp danh sách cơ hội, "
            "được lưu trong `output/1_planning` và SharedMemory với khóa `opportunities_summary`."
        ),
        callback=lambda output: create_docx(
            "Tổng hợp danh sách cơ hội",
            [
                "1. Mô tả cơ hội: Danh sách các cơ hội dự án (lấy từ business_case).",
                "2. Mức độ ưu tiên: Cao, trung bình, thấp.",
                "3. Ngày giao: Thời hạn thực hiện cơ hội.",
                "4. Người phụ trách: Cá nhân hoặc nhóm chịu trách nhiệm.",
                "5. Ghi chú: Thông tin bổ sung hoặc lưu ý.",
                shared_memory.load("business_case") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/1_planning/List_of_Opportunities_Summary.docx"
        ) and shared_memory.save("opportunities_summary", output)
    )

    tasks.extend([
        pmo_checklist_task,
        statement_of_work_task,
        project_approval_task,
        cost_estimating_worksheet_task,
        development_estimating_worksheet_task,
        capital_vs_expense_task,
        config_management_plan_task,
        risk_data_collection_task,
        risk_analysis_plan_task,
        procurement_plan_task,
        project_org_chart_task,
        roles_responsibilities_task,
        required_approvals_task,
        activity_worksheet_task,
        wbs_resource_planning_task,
        wbs_task,
        cobit_checklist_task,
        rfi_task,
        root_cause_analysis_task,
        project_plan_task,
        opportunities_summary_task
    ])

    return tasks
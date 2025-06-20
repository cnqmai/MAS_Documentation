from crewai import Task
from utils.output_formats import create_docx, create_xlsx
from memory.shared_memory import SharedMemory
import os

def create_requirements_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, requirement_agent):
    """
    Tạo các tác vụ cho giai đoạn Yêu cầu (Requirements Phase).
    """
    tasks = []

    # Tác vụ tạo Managing Scope and Requirements Checklist
    scope_requirements_checklist_task = Task(
        description=(
            "Sử dụng công cụ `create_requirements_document` để tạo tài liệu Danh sách kiểm tra quản lý phạm vi và yêu cầu (Managing Scope and Requirements Checklist) dựa trên dữ liệu từ `project_plan` và `project_charter` trong SharedMemory. "
            "Tài liệu này kiểm soát phạm vi và yêu cầu dự án để đạt được sự đồng thuận từ khách hàng và tránh tình trạng 'scope creep'. "
            "Nó giúp xác định các bên liên quan, đảm bảo yêu cầu được ghi chép đầy đủ, cam kết về sản phẩm, lịch trình, tài nguyên, quản lý thay đổi phạm vi, đồng thuận sớm về phạm vi, dự báo và kiểm soát rủi ro, nâng cao sự hài lòng của khách hàng. "
            "Nội dung phải bao gồm: mục đích, tổng quan sản phẩm/hệ thống, lý do triển khai dự án, giả định, phụ thuộc, ràng buộc, danh sách các bên liên quan, rủi ro, bảng kiểm phạm vi/yêu cầu. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/2_requirements` với tên `Managing_Scope_and_Requirements_Checklist.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `scope_requirements_checklist`."
        ),
        agent=requirement_agent,
        expected_output=(
            "Tài liệu `Managing_Scope_and_Requirements_Checklist.docx` chứa danh sách kiểm tra quản lý phạm vi và yêu cầu, "
            "được lưu trong `output/2_requirements` và SharedMemory với khóa `scope_requirements_checklist`."
        ),
        callback=lambda output: create_docx(
            "Danh sách kiểm tra quản lý phạm vi và yêu cầu",
            [
                "1. Mục đích: Mục tiêu của việc quản lý phạm vi và yêu cầu (lấy từ project_plan).",
                "2. Tổng quan sản phẩm: Mô tả hệ thống hoặc sản phẩm (lấy từ project_charter).",
                "3. Lý do triển khai: Bối cảnh và mục tiêu kinh doanh.",
                "4. Giả định và ràng buộc: Các giả định, phụ thuộc, và hạn chế.",
                "5. Danh sách các bên liên quan: Vai trò và trách nhiệm.",
                "6. Rủi ro: Các rủi ro liên quan đến phạm vi và yêu cầu.",
                "7. Bảng kiểm: Các hạng mục kiểm tra phạm vi và yêu cầu.",
                shared_memory.load("project_plan") or "Không có dữ liệu",
                shared_memory.load("project_charter") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/2_requirements/Managing_Scope_and_Requirements_Checklist.docx"
        ) and shared_memory.save("scope_requirements_checklist", output)
    )

    # Tác vụ tạo Business Requirements Document (BRD)
    brd_task = Task(
        description=(
            "Sử dụng công cụ `create_requirements_document` để tạo tài liệu Yêu cầu kinh doanh (Business Requirements Document - BRD) dựa trên dữ liệu từ `project_plan`, `statement_of_work`, và `business_case` trong SharedMemory. "
            "Tài liệu này xác định các yêu cầu kinh doanh và kỹ thuật, từ tổng thể đến chi tiết, đảm bảo sự chấp thuận của các bên liên quan, giao tiếp rõ ràng nhu cầu kinh doanh, và là đầu vào cho các pha kế tiếp. "
            "Nội dung phải bao gồm: thông tin dự án (mục tiêu, cách tiếp cận, chi phí, rủi ro, ngày giao hàng), quy trình hiện tại và cải tiến, yêu cầu hệ thống và người dùng cuối, yêu cầu khác (tính năng, hiệu suất, nội dung, màn hình, đào tạo, tài liệu). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/2_requirements` với tên `Business_Requirements_Document.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `brd`."
        ),
        agent=requirement_agent,
        expected_output=(
            "Tài liệu `Business_Requirements_Document.docx` chứa yêu cầu kinh doanh, "
            "được lưu trong `output/2_requirements` và SharedMemory với khóa `brd`."
        ),
        callback=lambda output: create_docx(
            "Yêu cầu kinh doanh",
            [
                "1. Thông tin dự án: Mục tiêu, cách tiếp cận, chi phí, rủi ro (lấy từ project_plan, business_case).",
                "2. Quy trình hiện tại: Mô tả quy trình kinh doanh hiện tại.",
                "3. Quy trình cải tiến: Các cải tiến được đề xuất (lấy từ statement_of_work).",
                "4. Yêu cầu hệ thống: Yêu cầu của người dùng cuối và hệ thống.",
                "5. Yêu cầu khác: Tính năng, hiệu suất, nội dung, đào tạo, tài liệu.",
                shared_memory.load("project_plan") or "Không có dữ liệu",
                shared_memory.load("statement_of_work") or "Không có dữ liệu",
                shared_memory.load("business_case") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/2_requirements/Business_Requirements_Document.docx"
        ) and shared_memory.save("brd", output)
    )

    # Tác vụ tạo Business Requirements Presentation To Stakeholders
    brd_presentation_task = Task(
        description=(
            "Sử dụng công cụ `create_requirements_document` để tạo tài liệu Thuyết trình yêu cầu kinh doanh cho các bên liên quan (Business Requirements Presentation To Stakeholders) dựa trên dữ liệu từ `brd` trong SharedMemory. "
            "Tài liệu này là slide thuyết trình để chia sẻ và xác nhận yêu cầu dự án với các bên liên quan và đơn vị tài trợ. "
            "Nội dung phải bao gồm: lý do yêu cầu kinh doanh quan trọng, thông tin và mô tả dự án, mục tiêu và phạm vi, các bên liên quan, chi phí, bảo trì hàng năm, mốc thời gian, luồng xử lý hiện tại/tương lai, yêu cầu kinh doanh cấp cao, giao diện hệ thống, hạ tầng, các yêu cầu khác. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/2_requirements` với tên `Business_Requirements_Presentation.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `brd_presentation`."
        ),
        agent=requirement_agent,
        expected_output=(
            "Tài liệu `Business_Requirements_Presentation.docx` chứa thuyết trình yêu cầu kinh doanh, "
            "được lưu trong `output/2_requirements` và SharedMemory với khóa `brd_presentation`."
        ),
        callback=lambda output: create_docx(
            "Thuyết trình yêu cầu kinh doanh",
            [
                "1. Lý do quan trọng: Tầm quan trọng của yêu cầu kinh doanh (lấy từ brd).",
                "2. Mô tả dự án: Tổng quan và mục tiêu dự án.",
                "3. Phạm vi: Phạm vi dự án và các hạng mục loại trừ.",
                "4. Các bên liên quan: Danh sách các bên liên quan chính.",
                "5. Chi phí và bảo trì: Chi phí dự kiến và bảo trì hàng năm.",
                "6. Mốc thời gian: Lịch trình chính của dự án.",
                "7. Luồng xử lý: Quy trình hiện tại và tương lai.",
                "8. Yêu cầu cấp cao: Yêu cầu kinh doanh, giao diện, hạ tầng.",
                shared_memory.load("brd") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/2_requirements/Business_Requirements_Presentation.docx"
        ) and shared_memory.save("brd_presentation", output)
    )

    # Tác vụ tạo Functional Requirements Document
    functional_requirements_task = Task(
        description=(
            "Sử dụng công cụ `create_requirements_document` để tạo tài liệu Yêu cầu chức năng (Functional Requirements Document) dựa trên dữ liệu từ `brd` và `project_plan` trong SharedMemory. "
            "Tài liệu này xác định các yêu cầu chức năng, bao gồm các chi tiết kỹ thuật, xử lý dữ liệu, tính toán. "
            "Nội dung phải bao gồm: mục tiêu, thông tin quy trình, yêu cầu chức năng và phi chức năng, giao diện hệ thống, phần mềm, phần cứng, giao tiếp. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/2_requirements` với tên `Functional_Requirements_Document.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `functional_requirements`."
        ),
        agent=requirement_agent,
        expected_output=(
            "Tài liệu `Functional_Requirements_Document.docx` chứa yêu cầu chức năng, "
            "được lưu trong `output/2_requirements` và SharedMemory với khóa `functional_requirements`."
        ),
        callback=lambda output: create_docx(
            "Yêu cầu chức năng",
            [
                "1. Mục tiêu: Mục đích của yêu cầu chức năng (lấy từ brd).",
                "2. Thông tin quy trình: Quy trình kinh doanh liên quan (lấy từ project_plan).",
                "3. Yêu cầu chức năng: Chi tiết các chức năng hệ thống.",
                "4. Yêu cầu phi chức năng: Hiệu suất, bảo mật, v.v.",
                "5. Giao diện hệ thống: Phần mềm, phần cứng, giao tiếp.",
                shared_memory.load("brd") or "Không có dữ liệu",
                shared_memory.load("project_plan") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/2_requirements/Functional_Requirements_Document.docx"
        ) and shared_memory.save("functional_requirements", output)
    )

    # Tác vụ tạo Software Architecture Plan
    software_architecture_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_requirements_document` để tạo tài liệu Kế hoạch kiến trúc phần mềm (Software Architecture Plan) dựa trên dữ liệu từ `brd` và `functional_requirements` trong SharedMemory. "
            "Tài liệu này mô tả tổng quan kiến trúc phần mềm của hệ thống từ nhiều góc độ, bao gồm: phạm vi, ký hiệu, thuật ngữ, mục tiêu kiến trúc, các góc nhìn (Use-case, Logic, Quy trình, Triển khai, Triển khai dữ liệu, Hiệu năng, Kích thước, Chất lượng). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/2_requirements` với tên `Software_Architecture_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `software_architecture_plan`."
        ),
        agent=requirement_agent,
        expected_output=(
            "Tài liệu `Software_Architecture_Plan.docx` chứa kế hoạch kiến trúc phần mềm, "
            "được lưu trong `output/2_requirements` và SharedMemory với khóa `software_architecture_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch kiến trúc phần mềm",
            [
                "1. Phạm vi: Phạm vi kiến trúc phần mềm (lấy từ brd).",
                "2. Ký hiệu và thuật ngữ: Các định nghĩa và ký hiệu kỹ thuật.",
                "3. Mục tiêu kiến trúc: Mục tiêu của kiến trúc hệ thống.",
                "4. Các góc nhìn: Use-case, Logic, Quy trình, Triển khai, Hiệu năng, Kích thước, Chất lượng (lấy từ functional_requirements).",
                shared_memory.load("brd") or "Không có dữ liệu",
                shared_memory.load("functional_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/2_requirements/Software_Architecture_Plan.docx"
        ) and shared_memory.save("software_architecture_plan", output)
    )

    # Tác vụ tạo Use Case Template
    use_case_template_task = Task(
        description=(
            "Sử dụng công cụ `create_requirements_document` để tạo tài liệu Mẫu Use Case (Use Case Template) dựa trên dữ liệu từ `functional_requirements` trong SharedMemory. "
            "Tài liệu này mô tả yêu cầu dự án dưới dạng kịch bản người dùng sử dụng hệ thống để đạt mục tiêu. "
            "Nội dung phải bao gồm: mục tiêu, thông tin dự án, yêu cầu kinh doanh cấp cao, giao diện, hạ tầng, mô tả Use Case (đơn giản, truyền thống, ví dụ), các yêu cầu liên quan (màn hình, nội dung, đào tạo). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/2_requirements` với tên `Use_Case_Template.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `use_case_template`."
        ),
        agent=requirement_agent,
        expected_output=(
            "Tài liệu `Use_Case_Template.docx` chứa mẫu Use Case, "
            "được lưu trong `output/2_requirements` và SharedMemory với khóa `use_case_template`."
        ),
        callback=lambda output: create_docx(
            "Mẫu Use Case",
            [
                "1. Mục tiêu: Mục đích của Use Case (lấy từ functional_requirements).",
                "2. Thông tin dự án: Tổng quan về dự án.",
                "3. Yêu cầu kinh doanh: Yêu cầu cấp cao liên quan.",
                "4. Mô tả Use Case: Kịch bản sử dụng hệ thống (đơn giản, truyền thống, ví dụ).",
                "5. Yêu cầu liên quan: Màn hình, nội dung, đào tạo.",
                shared_memory.load("functional_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/2_requirements/Use_Case_Template.docx"
        ) and shared_memory.save("use_case_template", output)
    )

    # Tác vụ tạo Requirements Inspection Checklist
    requirements_inspection_checklist_task = Task(
        description=(
            "Sử dụng công cụ `create_requirements_document` để tạo tài liệu Danh sách kiểm tra kiểm tra yêu cầu (Requirements Inspection Checklist) dựa trên dữ liệu từ `brd` và `functional_requirements` trong SharedMemory. "
            "Tài liệu này đảm bảo yêu cầu dự án được xác định rõ ràng và chất lượng cao, bao gồm tính đúng đắn, truy vết, giao diện, yêu cầu hành vi, phi hành vi. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/2_requirements` với tên `Requirements_Inspection_Checklist.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `requirements_inspection_checklist`."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Tài liệu `Requirements_Inspection_Checklist.docx` chứa danh sách kiểm tra yêu cầu, "
            "được lưu trong `output/2_requirements` và SharedMemory với khóa `requirements_inspection_checklist`."
        ),
        callback=lambda output: create_docx(
            "Danh sách kiểm tra kiểm tra yêu cầu",
            [
                "1. Mục đích: Mục tiêu của việc kiểm tra yêu cầu (lấy từ brd).",
                "2. Checklist: Tính đúng đắn, truy vết, giao diện, yêu cầu hành vi, phi hành vi (lấy từ functional_requirements).",
                shared_memory.load("brd") or "Không có dữ liệu",
                shared_memory.load("functional_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/2_requirements/Requirements_Inspection_Checklist.docx"
        ) and shared_memory.save("requirements_inspection_checklist", output)
    )

    # Tác vụ tạo Requirements Traceability Matrix (RTM)
    rtm_task = Task(
        description=(
            "Sử dụng công cụ `create_xlsx` để tạo tài liệu Ma trận truy vết yêu cầu (Requirements Traceability Matrix - RTM) dựa trên dữ liệu từ `brd`, `functional_requirements`, và `wbs` trong SharedMemory. "
            "Ma trận này truy vết yêu cầu từ yêu cầu ban đầu đến thiết kế và kiểm thử, đảm bảo sự đầy đủ và nhất quán. "
            "Nội dung phải bao gồm: mục đích, ma trận yêu cầu (thông tin chung, giao diện, hành vi, phi hành vi, độ chính xác, truy vết). "
            "Lưu tài liệu dưới dạng `.xlsx` trong thư mục `output/2_requirements` với tên `Requirements_Traceability_Matrix.xlsx`. "
            "Lưu kết quả vào SharedMemory với khóa `rtm`."
        ),
        agent=requirement_agent,
        expected_output=(
            "Tài liệu `Requirements_Traceability_Matrix.xlsx` chứa ma trận truy vết yêu cầu, "
            "được lưu trong `output/2_requirements` và SharedMemory với khóa `rtm`."
        ),
        callback=lambda output: create_xlsx(
            [
                ["Requirement ID", "Description", "Source", "Design", "Test Case"],
                ["REQ-001", "TBD", "BRD", "TBD", "TBD"],
                ["REQ-002", "TBD", "Functional Requirements", "TBD", "TBD"],
                ["REQ-003", "TBD", "WBS", "TBD", "TBD"]
            ],
            f"{output_base_dir}/2_requirements/Requirements_Traceability_Matrix.xlsx"
        ) and shared_memory.save("rtm", output)
    )

    # Tác vụ tạo Requirements Changes Impact Analysis
    requirements_changes_impact_task = Task(
        description=(
            "Sử dụng công cụ `create_requirements_document` để tạo tài liệu Phân tích tác động thay đổi yêu cầu (Requirements Changes Impact Analysis) dựa trên dữ liệu từ `rtm` và `brd` trong SharedMemory. "
            "Tài liệu này phân tích tác động khi thay đổi yêu cầu, bao gồm ảnh hưởng đến hệ thống, lịch trình, chi phí. "
            "Nội dung phải bao gồm: mục đích, mô tả thay đổi, rủi ro, giả định, các thành phần bị ảnh hưởng, ước lượng thời gian/chi phí. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/2_requirements` với tên `Requirements_Changes_Impact_Analysis.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `requirements_changes_impact`."
        ),
        agent=requirement_agent,
        expected_output=(
            "Tài liệu `Requirements_Changes_Impact_Analysis.docx` chứa phân tích tác động thay đổi yêu cầu, "
            "được lưu trong `output/2_requirements` và SharedMemory với khóa `requirements_changes_impact`."
        ),
        callback=lambda output: create_docx(
            "Phân tích tác động thay đổi yêu cầu",
            [
                "1. Mục đích: Mục tiêu của phân tích thay đổi (lấy từ rtm).",
                "2. Mô tả thay đổi: Chi tiết các thay đổi yêu cầu (lấy từ brd).",
                "3. Rủi ro và giả định: Các rủi ro và giả định liên quan.",
                "4. Thành phần bị ảnh hưởng: Hệ thống, lịch trình, chi phí.",
                "5. Ước lượng: Thời gian và chi phí để thực hiện thay đổi.",
                shared_memory.load("rtm") or "Không có dữ liệu",
                shared_memory.load("brd") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/2_requirements/Requirements_Changes_Impact_Analysis.docx"
        ) and shared_memory.save("requirements_changes_impact", output)
    )

    # Tác vụ tạo Training Plan
    training_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_requirements_document` để tạo tài liệu Kế hoạch đào tạo (Training Plan) dựa trên dữ liệu từ `functional_requirements` và `brd` trong SharedMemory. "
            "Tài liệu này hỗ trợ sử dụng và duy trì hệ thống hoặc ứng dụng, bao gồm: giới thiệu, phạm vi, phương pháp đào tạo, khóa học đào tạo người dùng/kỹ thuật, yêu cầu môi trường, lịch đào tạo, phê duyệt và ký nhận. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/2_requirements` với tên `Training_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `training_plan`."
        ),
        agent=requirement_agent,
        expected_output=(
            "Tài liệu `Training_Plan.docx` chứa kế hoạch đào tạo, "
            "được lưu trong `output/2_requirements` và SharedMemory với khóa `training_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch đào tạo",
            [
                "1. Giới thiệu: Mục đích và phạm vi đào tạo (lấy từ brd).",
                "2. Phương pháp đào tạo: Cách thức triển khai đào tạo.",
                "3. Khóa học: Đào tạo người dùng và kỹ thuật (lấy từ functional_requirements).",
                "4. Yêu cầu môi trường: Cơ sở vật chất và công cụ cần thiết.",
                "5. Lịch đào tạo: Thời gian và lịch trình đào tạo.",
                "6. Phê duyệt: Quy trình phê duyệt và ký nhận.",
                shared_memory.load("functional_requirements") or "Không có dữ liệu",
                shared_memory.load("brd") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/2_requirements/Training_Plan.docx"
        ) and shared_memory.save("training_plan", output)
    )

    # Tác vụ tạo Service Level Agreement Template
    sla_template_task = Task(
        description=(
            "Sử dụng công cụ `create_requirements_document` để tạo tài liệu Mẫu thỏa thuận mức dịch vụ (Service Level Agreement Template) dựa trên dữ liệu từ `non_functional_requirements` và `brd` trong SharedMemory. "
            "Tài liệu này là thỏa thuận chính thức giữa tổ chức và khách hàng về dịch vụ được cung cấp, mức độ hỗ trợ và chi phí. "
            "Nội dung phải bao gồm: điều khoản, thời hạn, tổ chức liên quan, danh sách ứng dụng được hỗ trợ (khôi phục thảm họa, mức độ ưu tiên), trách nhiệm, hỗ trợ, báo cáo hiệu suất, điều kiện chấm dứt/hủy bỏ, sửa đổi SLA. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/2_requirements` với tên `Service_Level_Agreement_Template.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `sla_template`."
        ),
        agent=requirement_agent,
        expected_output=(
            "Tài liệu `Service_Level_Agreement_Template.docx` chứa mẫu thỏa thuận mức dịch vụ, "
            "được lưu trong `output/2_requirements` và SharedMemory với khóa `sla_template`."
        ),
        callback=lambda output: create_docx(
            "Mẫu thỏa thuận mức dịch vụ",
            [
                "1. Điều khoản: Các điều khoản chính của SLA (lấy từ non_functional_requirements).",
                "2. Thời hạn: Thời gian hiệu lực của SLA.",
                "3. Tổ chức liên quan: Các bên tham gia SLA (lấy từ brd).",
                "4. Ứng dụng hỗ trợ: Danh sách ứng dụng và mức độ ưu tiên.",
                "5. Trách nhiệm: Trách nhiệm của các bên.",
                "6. Báo cáo hiệu suất: Quy trình báo cáo và đo lường.",
                "7. Điều kiện chấm dứt: Điều kiện hủy bỏ hoặc sửa đổi SLA.",
                shared_memory.load("non_functional_requirements") or "Không có dữ liệu",
                shared_memory.load("brd") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/2_requirements/Service_Level_Agreement_Template.docx"
        ) and shared_memory.save("sla_template", output)
    )

    # Tác vụ tạo Non-functional Requirements
    non_functional_requirements_task = Task(
        description=(
            "Sử dụng công cụ `create_requirements_document` để tạo tài liệu Yêu cầu phi chức năng (Non-functional Requirements) dựa trên dữ liệu từ `brd` và `project_plan` trong SharedMemory. "
            "Tài liệu này xác định các yêu cầu phi chức năng như hiệu suất, bảo mật, khả năng mở rộng, và khả năng sử dụng. "
            "Nội dung phải bao gồm: yêu cầu hiệu suất, bảo mật, khả năng mở rộng, khả năng sử dụng, các ràng buộc kỹ thuật và nghiệp vụ. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/2_requirements` với tên `Non_functional_Requirements.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `non_functional_requirements`."
        ),
        agent=requirement_agent,
        expected_output=(
            "Tài liệu `Non_functional_Requirements.docx` chứa yêu cầu phi chức năng, "
            "được lưu trong `output/2_requirements` và SharedMemory với khóa `non_functional_requirements`."
        ),
        callback=lambda output: create_docx(
            "Yêu cầu phi chức năng",
            [
                "1. Yêu cầu hiệu suất: Hiệu suất hệ thống (lấy từ brd).",
                "2. Yêu cầu bảo mật: Các yêu cầu bảo mật hệ thống.",
                "3. Khả năng mở rộng: Khả năng mở rộng của hệ thống.",
                "4. Khả năng sử dụng: Yêu cầu về trải nghiệm người dùng.",
                "5. Ràng buộc: Các ràng buộc kỹ thuật và nghiệp vụ (lấy từ project_plan).",
                shared_memory.load("brd") or "Không có dữ liệu",
                shared_memory.load("project_plan") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/2_requirements/Non_functional_Requirements.docx"
        ) and shared_memory.save("non_functional_requirements", output)
    )

    # Tác vụ tạo Privacy & Security Requirements
    privacy_security_requirements_task = Task(
        description=(
            "Sử dụng công cụ `create_requirements_document` để tạo tài liệu Yêu cầu bảo mật và quyền riêng tư (Privacy & Security Requirements) dựa trên dữ liệu từ `non_functional_requirements` và `brd` trong SharedMemory. "
            "Tài liệu này xác định các yêu cầu liên quan đến bảo mật và quyền riêng tư của hệ thống. "
            "Nội dung phải bao gồm: yêu cầu bảo mật dữ liệu, quyền riêng tư của người dùng, tuân thủ quy định pháp lý, biện pháp kiểm soát truy cập. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/2_requirements` với tên `Privacy_and_Security_Requirements.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `privacy_security_requirements`."
        ),
        agent=requirement_agent,
        expected_output=(
            "Tài liệu `Privacy_and_Security_Requirements.docx` chứa yêu cầu bảo mật và quyền riêng tư, "
            "được lưu trong `output/2_requirements` và SharedMemory với khóa `privacy_security_requirements`."
        ),
        callback=lambda output: create_docx(
            "Yêu cầu bảo mật và quyền riêng tư",
            [
                "1. Bảo mật dữ liệu: Các yêu cầu bảo vệ dữ liệu (lấy từ non_functional_requirements).",
                "2. Quyền riêng tư: Bảo vệ thông tin người dùng (lấy từ brd).",
                "3. Tuân thủ quy định: Các yêu cầu pháp lý và quy định.",
                "4. Kiểm soát truy cập: Biện pháp kiểm soát truy cập hệ thống.",
                shared_memory.load("non_functional_requirements") or "Không có dữ liệu",
                shared_memory.load("brd") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/2_requirements/Privacy_and_Security_Requirements.docx"
        ) and shared_memory.save("privacy_security_requirements", output)
    )

    tasks.extend([
        scope_requirements_checklist_task,
        brd_task,
        brd_presentation_task,
        functional_requirements_task,
        software_architecture_plan_task,
        use_case_template_task,
        requirements_inspection_checklist_task,
        rtm_task,
        requirements_changes_impact_task,
        training_plan_task,
        sla_template_task,
        non_functional_requirements_task,
        privacy_security_requirements_task
    ])

    return tasks
from crewai import Task
from utils.output_formats import create_docx, create_xlsx
from memory.shared_memory import SharedMemory
import os

def create_initiation_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, initiation_agent):
    """
    Tạo các tác vụ cho giai đoạn Khởi tạo (Initiation Phase).
    """
    tasks = []

    # Tác vụ tạo tài liệu phương pháp tốt nhất
    best_practices_task = Task(
        description=(
            "Sử dụng công cụ `generate_best_practices` để tạo tài liệu phương pháp tốt nhất cho giai đoạn khởi tạo dự án. "
            "Tài liệu này cần đề xuất các thực tiễn hàng đầu, bao gồm chiến lược quản lý rủi ro, phương pháp thu thập yêu cầu, và cách tiếp cận lập kế hoạch sơ bộ. "
            "Đảm bảo rằng các khuyến nghị dựa trên các tiêu chuẩn quản lý dự án quốc tế như PMI hoặc PRINCE2. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/0_initiation` với tên `Best_Practices_Khởi_tạo.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `best_practices`."
        ),
        agent=researcher_agent,
        expected_output=(
            "Tài liệu `Best_Practices_Khởi_tạo.docx` chứa danh sách các phương pháp tốt nhất, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `best_practices`."
        ),
        callback=lambda output: shared_memory.save("best_practices", output)
    )

    # Tác vụ tạo Project Initiation Agenda
    project_initiation_agenda_task = Task(
        description=(
            "Sử dụng công cụ `create_project_document` để tạo tài liệu Chương trình nghị sự khởi tạo dự án (Project Initiation Agenda) dựa trên dữ liệu từ `system_request_summary` trong SharedMemory. "
            "Tài liệu này là lịch trình họp khởi động dự án, xác định các bên liên quan, nhà tài trợ và thành viên kỹ thuật/kinh doanh chủ chốt. "
            "Nó cung cấp cơ hội để quản lý dự án tạo động lực, xác lập mục tiêu chung và đánh giá nhóm. "
            "Nội dung phải bao gồm: chủ đề họp, người khởi xướng, thời gian họp, danh sách người tham dự, tài liệu cần đọc, chủ đề thảo luận (ví dụ: mục tiêu dự án, phạm vi sơ bộ, rủi ro ban đầu, kế hoạch truyền thông), người trình bày, và tài liệu đính kèm. "
            "Đảm bảo rằng tài liệu được trình bày rõ ràng, chuyên nghiệp, và phù hợp để sử dụng trong các cuộc họp với các bên liên quan cấp cao. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/0_initiation` với tên `Project_Initiation_Agenda.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `project_initiation_agenda`."
        ),
        agent=initiation_agent,
        expected_output=(
            "Tài liệu `Project_Initiation_Agenda.docx` chứa chương trình nghị sự, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `project_initiation_agenda`."
        ),
        callback=lambda output: create_docx(
            "Chương trình nghị sự khởi tạo dự án",
            [
                "1. Mục tiêu cuộc họp: Thống nhất mục tiêu và phạm vi dự án.",
                "2. Danh sách tham gia: Các bên liên quan chính (lấy từ system_request_summary).",
                "3. Thời gian biểu: Lịch trình chi tiết cho cuộc họp.",
                "4. Chủ đề thảo luận: Phạm vi, rủi ro, kế hoạch sơ bộ, và chiến lược truyền thông.",
                shared_memory.load("system_request_summary") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/0_initiation/Project_Initiation_Agenda.docx"
        ) and shared_memory.save("project_initiation_agenda", output)
    )

    # Tác vụ tạo Project Charter
    project_charter_task = Task(
        description=(
            "Sử dụng công cụ `create_project_document` để tạo tài liệu Bản điều lệ dự án (Project Charter) dựa trên dữ liệu từ `system_request_summary` trong SharedMemory. "
            "Tài liệu này là tài liệu khởi đầu chính thức dự án trong Giai đoạn Khởi tạo, xác định mục tiêu, phạm vi, các bên liên quan và quyền hạn của quản lý dự án. "
            "Nó là bản tổng quan cấp cao, một trang, được dùng để đảm bảo tất cả mọi người hiểu rõ mục tiêu và cách thức thực hiện. "
            "Nội dung phải bao gồm: tuyên bố cơ hội, mục tiêu, phạm vi dự án, quy trình trong và ngoài phạm vi, nhóm dự án, các bên liên quan, mốc thời gian, chi phí ước tính. "
            "Nội dung phải được trình bày theo cấu trúc chuẩn quản lý dự án (PMI hoặc PRINCE2), bao gồm các phần như Tóm tắt dự án, Mục tiêu, Phạm vi, Tổ chức dự án, Quản lý rủi ro sơ bộ, và Phê duyệt. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/0_initiation` với tên `Project_Charter.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `project_charter`."
        ),
        agent=initiation_agent,
        expected_output=(
            "Tài liệu `Project_Charter.docx` chứa bản điều lệ dự án, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `project_charter`."
        ),
        callback=lambda output: create_docx(
            "Bản điều lệ dự án",
            [
                "1. Tóm tắt dự án: Mô tả ngắn gọn về dự án và bối cảnh.",
                "2. Mục tiêu: Các mục tiêu cụ thể (lấy từ system_request_summary).",
                "3. Phạm vi: Phạm vi dự án và các hạng mục loại trừ.",
                "4. Các bên liên quan: Danh sách và vai trò của các bên liên quan chính.",
                "5. Giả định và ràng buộc: Các giả định và hạn chế (ngân sách, thời gian, tài nguyên).",
                "6. Cột mốc sơ bộ: Các mốc thời gian quan trọng.",
                "7. Quản lý rủi ro: Các rủi ro ban đầu và chiến lược giảm thiểu.",
                shared_memory.load("system_request_summary") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/0_initiation/Project_Charter.docx"
        ) and shared_memory.save("project_charter", output)
    )

    # Tác vụ tạo Business Case Document
    business_case_task = Task(
        description=(
            "Sử dụng công cụ `create_project_document` để tạo tài liệu Trường hợp kinh doanh (Business Case Document) dựa trên dữ liệu từ `system_request_summary` trong SharedMemory. "
            "Tài liệu này xác định giá trị kinh doanh tiềm năng của dự án, thường đi kèm với Project Charter để trình bày với lãnh đạo nhằm được phê duyệt. "
            "Nó cần đánh giá các lợi ích kinh doanh của dự án, bao gồm lợi ích tài chính (ROI, NPV, lợi nhuận, tiết kiệm chi phí, thị phần) và phi tài chính (cải thiện quy trình, nâng cao trải nghiệm khách hàng, yếu tố xã hội/môi trường). "
            "Nội dung phải bao gồm: mô tả nhu cầu, vấn đề, giải pháp; lợi ích định lượng và định tính; rủi ro; yêu cầu; chi phí; tiến độ; chất lượng; khuyến nghị và lựa chọn thay thế; phê duyệt từ các bên liên quan. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/0_initiation` với tên `Business_Case_Document.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `business_case`."
        ),
        agent=initiation_agent,
        expected_output=(
            "Tài liệu `Business_Case_Document.docx` chứa trường hợp kinh doanh, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `business_case`."
        ),
        callback=lambda output: create_docx(
            "Tài liệu trường hợp kinh doanh",
            [
                "1. Tóm tắt điều hành: Tổng quan về lợi ích và mục tiêu kinh doanh.",
                "2. Lợi ích kinh doanh: Lợi ích tài chính và phi tài chính (lấy từ system_request_summary).",
                "3. Phân tích chi phí: Chi phí ước tính ban đầu.",
                "4. Rủi ro kinh doanh: Các rủi ro tiềm ẩn và chiến lược giảm thiểu.",
                "5. Khuyến nghị: Lý do thực hiện dự án.",
                shared_memory.load("system_request_summary") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/0_initiation/Business_Case_Document.docx"
        ) and shared_memory.save("business_case", output)
    )

    # Tác vụ tạo Feasibility Study
    feasibility_study_task = Task(
        description=(
            "Sử dụng công cụ `create_project_document` để tạo tài liệu Nghiên cứu khả thi (Feasibility Study) dựa trên dữ liệu từ `system_request_summary` trong SharedMemory. "
            "Báo cáo này chứa thông tin kỹ thuật, kinh doanh và chi phí để đánh giá tính khả thi và tiềm năng của dự án, dựa trên mức độ khó khăn, kinh nghiệm cần thiết, thời gian, nguồn lực, ảnh hưởng đến hoạt động hiện tại, kế hoạch dự phòng nếu kéo dài, yếu tố môi trường, văn hóa công ty, nhân lực hiện có, quy trình hiện hành, và phân tích chi phí/lợi ích. "
            "Nội dung phải bao gồm: giới thiệu, mục tiêu, phạm vi; hệ thống hiện tại; môi trường vận hành; tổ chức người dùng; sản phẩm cuối cùng; giải pháp và lựa chọn thay thế; phê duyệt; phân tích khả thi kỹ thuật (công nghệ, cơ sở hạ tầng); khả thi tài chính (ngân sách, ROI); khả thi tổ chức (nhân sự, quy trình); khả thi pháp lý; rủi ro khả thi. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/0_initiation` với tên `Feasibility_Study.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `feasibility_study`."
        ),
        agent=initiation_agent,
        expected_output=(
            "Tài liệu `Feasibility_Study.docx` chứa nghiên cứu khả thi, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `feasibility_study`."
        ),
        callback=lambda output: create_docx(
            "Nghiên cứu khả thi",
            [
                "1. Mục tiêu nghiên cứu: Xác định tính khả thi của dự án.",
                "2. Khả thi kỹ thuật: Công nghệ, cơ sở hạ tầng cần thiết.",
                "3. Khả thi tài chính: Ngân sách, ROI, và nguồn tài trợ.",
                "4. Khả thi tổ chức: Nhân sự, quy trình, và năng lực hiện tại.",
                "5. Khả thi pháp lý: Các quy định và yêu cầu tuân thủ.",
                "6. Rủi ro khả thi: Các rủi ro tiềm ẩn và chiến lược giảm thiểu.",
                shared_memory.load("system_request_summary") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/0_initiation/Feasibility_Study.docx"
        ) and shared_memory.save("feasibility_study", output)
    )

    # Tác vụ tạo Value Proposition Template
    value_proposition_task = Task(
        description=(
            "Sử dụng công cụ `create_project_document` để tạo tài liệu Mẫu giá trị đề xuất (Value Proposition Template) dựa trên dữ liệu từ `system_request_summary` trong SharedMemory. "
            "Biểu mẫu này giúp đánh giá giá trị của một ứng dụng, hệ thống hoặc sản phẩm đề xuất (thường từ bên ngoài) nhằm hỗ trợ ra quyết định, sử dụng kèm với Business Case Document. "
            "Nội dung phải bao gồm: sản phẩm/dịch vụ đề xuất, mô tả dự án, thị trường mục tiêu, nhu cầu và ngưỡng chịu đựng, tính năng cần thiết, lợi ích, quyết định tự phát triển hay mua ngoài. "
            "Tài liệu cần xác định giá trị cốt lõi mà dự án mang lại cho các bên liên quan, bao gồm lợi ích cụ thể cho khách hàng, tổ chức, và các đối tác. "
            "Đảm bảo tài liệu được trình bày rõ ràng và ngắn gọn để sử dụng trong các buổi thuyết trình với các bên liên quan. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/0_initiation` với tên `Value_Proposition_Template.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `value_proposition`."
        ),
        agent=initiation_agent,
        expected_output=(
            "Tài liệu `Value_Proposition_Template.docx` chứa mẫu giá trị đề xuất, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `value_proposition`."
        ),
        callback=lambda output: create_docx(
            "Mẫu giá trị đề xuất",
            [
                "1. Mô tả giá trị: Giá trị cốt lõi của dự án (lấy từ system_request_summary).",
                "2. Đối tượng hưởng lợi: Khách hàng, tổ chức, và các đối tác.",
                "3. Lợi ích chính: Các lợi ích cụ thể mà dự án mang lại.",
                "4. Điểm khác biệt: Những yếu tố làm dự án nổi bật so với các giải pháp khác.",
                shared_memory.load("system_request_summary") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/0_initiation/Value_Proposition_Template.docx"
        ) and shared_memory.save("value_proposition", output)
    )

    # Tác vụ tạo Project or Issue Submission Form
    submission_form_task = Task(
        description=(
            "Sử dụng công cụ `create_project_document` để tạo tài liệu Mẫu gửi dự án hoặc vấn đề (Project or Issue Submission Form) dựa trên dữ liệu từ `system_request_summary` trong SharedMemory. "
            "Mẫu đơn tóm tắt 1 trang giúp nhận diện dự án đề xuất, cơ hội, mục tiêu kinh doanh (giảm chi phí, tăng hiệu suất, tuân thủ quy định), phạm vi, các vấn đề và khuyến nghị. "
            "Biểu mẫu này giúp xác định cơ hội tiềm năng về kinh doanh/CNTT, những hệ thống liên quan, các phòng ban bị ảnh hưởng, các yếu tố trong và ngoài phạm vi dự án, chi phí dự kiến, các vấn đề trọng yếu và khuyến nghị. "
            "Nội dung phải bao gồm: mô tả vấn đề, mức độ ưu tiên, tác động, hành động đề xuất. "
            "Đảm bảo mẫu được thiết kế dễ sử dụng và phù hợp với quy trình quản lý dự án. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/0_initiation` với tên `Project_or_Issue_Submission_Form.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `submission_form`."
        ),
        agent=initiation_agent,
        expected_output=(
            "Tài liệu `Project_or_Issue_Submission_Form.docx` chứa mẫu gửi dự án hoặc vấn đề, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `submission_form`."
        ),
        callback=lambda output: create_docx(
            "Mẫu gửi dự án hoặc vấn đề",
            [
                "1. Mô tả vấn đề: Thông tin chi tiết về dự án hoặc vấn đề (lấy từ system_request_summary).",
                "2. Mức độ ưu tiên: Cao, trung bình, thấp.",
                "3. Tác động: Ảnh hưởng đến dự án hoặc tổ chức.",
                "4. Hành động đề xuất: Các bước giải quyết được đề xuất.",
                shared_memory.load("system_request_summary") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/0_initiation/Project_or_Issue_Submission_Form.docx"
        ) and shared_memory.save("submission_form", output)
    )

    # Tác vụ tạo Project Cost - Benefit Analysis
    cost_benefit_analysis_task = Task(
        description=(
            "Sử dụng công cụ `create_project_document` và `create_analysis_table` để tạo tài liệu Phân tích chi phí - lợi ích (Project Cost - Benefit Analysis) dựa trên dữ liệu từ `system_request_summary` và `business_case` trong SharedMemory. "
            "Tài liệu này xác định dự án đề xuất, cơ hội, mục tiêu kinh doanh, phạm vi, các vấn đề, lựa chọn thay thế hoặc khuyến nghị, và phê duyệt bởi các bên liên quan chủ chốt. "
            "Phân tích này cho thấy có nên đầu tư thời gian, nguồn lực, chi phí cho dự án hay không dựa trên giá trị lợi ích và chi phí. "
            "Nội dung phải bao gồm: thông tin chung (tên dự án, nhà tài trợ, mục đích, lợi ích), khuyến nghị và lựa chọn thay thế, chi phí và nguồn lực, lịch trình, rủi ro, phân tích rủi ro. "
            "Lưu tài liệu dưới dạng `.docx` và bảng phân tích dưới dạng `.xlsx` trong thư mục `output/0_initiation` với tên `Project_Cost_Benefit_Analysis.docx` và `Project_Cost_Benefit_Analysis.xlsx`. "
            "Lưu kết quả vào SharedMemory với khóa `cost_benefit_analysis`."
        ),
        agent=initiation_agent,
        expected_output=(
            "Tài liệu `Project_Cost_Benefit_Analysis.docx` và `Project_Cost_Benefit_Analysis.xlsx` chứa phân tích chi phí - lợi ích, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `cost_benefit_analysis`."
        ),
        callback=lambda output: (
            create_docx(
                "Phân tích chi phí - lợi ích",
                [
                    "1. Tóm tắt chi phí: Tổng quan về chi phí dự án.",
                    "2. Lợi ích dự kiến: Lợi ích tài chính và phi tài chính (lấy từ business_case).",
                    "3. Phân tích định lượng: ROI, NPV, và các chỉ số tài chính khác.",
                    "4. Kết luận: Đánh giá tổng thể về tính khả thi tài chính.",
                    shared_memory.load("system_request_summary") or "Không có dữ liệu",
                    shared_memory.load("business_case") or "Không có dữ liệu"
                ],
                f"{output_base_dir}/0_initiation/Project_Cost_Benefit_Analysis.docx"
            ) and
            create_xlsx(
                [
                    ["Category", "Description", "Cost", "Benefit"],
                    ["Personnel", "Labor costs", "TBD", "TBD"],
                    ["Technology", "Software and hardware", "TBD", "TBD"],
                    ["Infrastructure", "Facilities and equipment", "TBD", "TBD"]
                ],
                f"{output_base_dir}/0_initiation/Project_Cost_Benefit_Analysis.xlsx"
            ) and
            shared_memory.save("cost_benefit_analysis", output)
        )
    )

    # Tác vụ tạo Project Team Definition
    project_team_definition_task = Task(
        description=(
            "Sử dụng công cụ `create_project_document` để tạo tài liệu Định nghĩa nhóm dự án (Project Team Definition) dựa trên dữ liệu từ `project_charter` trong SharedMemory. "
            "Tài liệu xác định các nhóm kinh doanh và kỹ thuật chịu trách nhiệm khởi tạo, phân tích, phát triển, kiểm thử, triển khai và phê duyệt dự án. "
            "Nhóm dự án bao gồm các nguồn lực được phân công để hoàn thành mục tiêu và sản phẩm của dự án, có thể là nhóm chức năng đơn lẻ hoặc đa chức năng. "
            "Nội dung phải bao gồm: tổng quan buổi họp, nhận diện các bên liên quan và thành viên dự án, lịch trình các cột mốc chính, trách nhiệm (hoàn thành công việc đúng thời hạn, ngân sách, và báo cáo tiến độ), cơ cấu tổ chức, danh sách thành viên, vai trò và trách nhiệm, yêu cầu kỹ năng. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/0_initiation` với tên `Project_Team_Definition.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `project_team_definition`."
        ),
        agent=initiation_agent,
        expected_output=(
            "Tài liệu `Project_Team_Definition.docx` chứa định nghĩa nhóm dự án, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `project_team_definition`."
        ),
        callback=lambda output: create_docx(
            "Định nghĩa nhóm dự án",
            [
                "1. Cơ cấu tổ chức: Sơ đồ tổ chức của nhóm dự án (lấy từ project_charter).",
                "2. Danh sách thành viên: Các thành viên và vai trò chính.",
                "3. Vai trò và trách nhiệm: Mô tả chi tiết trách nhiệm của từng vai trò.",
                "4. Yêu cầu kỹ năng: Kỹ năng và kinh nghiệm cần thiết.",
                shared_memory.load("project_charter") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/0_initiation/Project_Team_Definition.docx"
        ) and shared_memory.save("project_team_definition", output)
    )

    # Tác vụ tạo Identification List
    identification_list_task = Task(
        description=(
            "Sử dụng công cụ `create_project_document` để tạo tài liệu Danh sách nhận diện các bên liên quan (Stakeholder Identification List) dựa trên dữ liệu từ `project_charter` trong SharedMemory. "
            "Danh sách xác định các bên liên quan cung cấp khả năng nhận diện những cá nhân, nhóm, hoặc tổ chức có thể ảnh hưởng hoặc bị ảnh hưởng bởi dự án, phân tích kỳ vọng của họ và mức độ ảnh hưởng tới dự án, đồng thời phát triển chiến lược và cách tiếp cận phù hợp để thu hút sự tham gia của họ. "
            "Việc xác định bao gồm các quy trình để nhận diện cá nhân, nhóm, hoặc tổ chức có liên quan, phân tích kỳ vọng và tác động, xây dựng chiến lược quản lý hiệu quả sự tham gia, nhận diện tên, chức danh, vai trò tiềm năng, mức độ hiểu biết và cam kết, xác định mức độ quyền lực, quan tâm và ảnh hưởng, quản lý và kiểm soát liên tục các bên liên quan. "
            "Nội dung phải bao gồm: danh sách các bên liên quan, danh sách tài sản, danh sách rủi ro. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/0_initiation` với tên `Stakeholder_Identification_List.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `identification_list`."
        ),
        agent=initiation_agent,
        expected_output=(
            "Tài liệu `Stakeholder_Identification_List.docx` chứa danh sách nhận diện, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `identification_list`."
        ),
        callback=lambda output: create_docx(
            "Danh sách nhận diện các bên liên quan",
            [
                "1. Danh sách các bên liên quan: Tên, chức danh, vai trò, mức độ quyền lực, quan tâm, ảnh hưởng (lấy từ project_charter).",
                "2. Phân tích kỳ vọng: Kỳ vọng và mức độ cam kết của các bên liên quan.",
                "3. Chiến lược thu hút: Cách tiếp cận để quản lý và thu hút sự tham gia.",
                "4. Danh sách tài sản: Các tài sản liên quan đến dự án.",
                "5. Danh sách rủi ro: Các rủi ro chính được nhận diện ban đầu.",
                shared_memory.load("project_charter") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/0_initiation/Stakeholder_Identification_List.docx"
        ) and shared_memory.save("identification_list", output)
    )

    # Tác vụ tạo Project Resource Plan
    project_resource_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_project_document` để tạo tài liệu Kế hoạch tài nguyên dự án (Project Resource Plan) dựa trên dữ liệu từ `project_charter` và `project_team_definition` trong SharedMemory. "
            "Tài liệu này là nguồn tổng hợp trung tâm để xác định tất cả nguồn lực cần thiết cho dự án: kích thước nhóm, loại nguồn lực, nhu cầu về cơ sở vật chất, tổ chức nhóm, các giả định, rủi ro và biện pháp giảm thiểu. "
            "Nội dung phải bao gồm: kích thước nhóm dự án, các nguồn lực/kỹ năng cần thiết, nguồn nhân sự, số lượng, nhu cầu cơ sở vật chất (loại, thời gian, số lượng), hồ sơ nguồn lực (loại, nguồn, chi phí theo giờ, giờ theo tháng, tổng giờ, tổng chi phí), tổ chức nhóm, giả định, rủi ro và biện pháp giảm thiểu, phê duyệt từ các bên liên quan. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/0_initiation` với tên `Project_Resource_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `project_resource_plan`."
        ),
        agent=initiation_agent,
        expected_output=(
            "Tài liệu `Project_Resource_Plan.docx` chứa kế hoạch tài nguyên, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `project_resource_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch tài nguyên dự án",
            [
                "1. Danh sách tài nguyên: Nhân sự, thiết bị, và công nghệ cần thiết (lấy từ project_charter và project_team_definition).",
                "2. Kế hoạch phân bổ: Cách thức và thời điểm phân bổ tài nguyên.",
                "3. Lịch trình sử dụng tài nguyên: Thời gian sử dụng từng loại tài nguyên.",
                "4. Rủi ro tài nguyên: Các rủi ro liên quan đến tài nguyên và chiến lược giảm thiểu.",
                shared_memory.load("project_charter") or "Không có dữ liệu",
                shared_memory.load("project_team_definition") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/0_initiation/Project_Resource_Plan.docx"
        ) and shared_memory.save("project_resource_plan", output)
    )

    # Tác vụ tạo Concept Of Operations
    concept_of_operations_task = Task(
        description=(
            "Sử dụng công cụ `create_project_document` để tạo tài liệu Khái niệm vận hành (Concept Of Operations) dựa trên dữ liệu từ `project_charter` và `business_case` trong SharedMemory. "
            "CONOPS là tài liệu phân tích nhu cầu về năng lực và mô tả ở mức cao về các yêu cầu nhằm đạt được mục tiêu của tổ chức CNTT và các đơn vị trực thuộc, làm công cụ giao tiếp giữa khách hàng nội bộ và nhóm phát triển để mô tả rõ nhu cầu kinh doanh. "
            "Nó được dùng để đánh giá nhu cầu, đề xuất hệ thống mới, hỗ trợ lập Business Case và tài liệu yêu cầu kinh doanh (BRD). "
            "Nội dung phải bao gồm: nhu cầu năng lực, mô tả vận hành và hỗ trợ, cơ sở thay đổi, tác động tiềm năng, kịch bản vận hành, tính năng chức năng, tóm tắt và phân tích hệ thống đề xuất, quy trình vận hành, vai trò và trách nhiệm, rủi ro vận hành. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/0_initiation` với tên `Concept_Of_Operations.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `concept_of_operations`."
        ),
        agent=initiation_agent,
        expected_output=(
            "Tài liệu `Concept_Of_Operations.docx` chứa khái niệm vận hành, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `concept_of_operations`."
        ),
        callback=lambda output: create_docx(
            "Khái niệm vận hành",
            [
                "1. Mô tả hệ thống: Tổng quan về hệ thống hoặc sản phẩm của dự án (lấy từ project_charter).",
                "2. Quy trình vận hành: Các quy trình chính để vận hành dự án (lấy từ business_case).",
                "3. Vai trò và trách nhiệm: Các vai trò vận hành chính.",
                "4. Rủi ro vận hành: Các rủi ro tiềm ẩn và chiến lược giảm thiểu.",
                shared_memory.load("project_charter") or "Không có dữ liệu",
                shared_memory.load("business_case") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/0_initiation/Concept_Of_Operations.docx"
        ) and shared_memory.save("concept_of_operations", output)
    )

    # Tác vụ tạo Initiate Project Checklist
    initiate_project_checklist_task = Task(
        description=(
            "Sử dụng công cụ `create_project_document` để tạo tài liệu Danh sách kiểm tra khởi tạo dự án (Initiate Project Checklist) dựa trên dữ liệu từ `project_charter` và `business_case` trong SharedMemory. "
            "Danh sách kiểm tra các mục tiêu và nhiệm vụ chính trong Giai đoạn Khởi tạo Dự án (Project Concept / Initiation Phase), xác minh rằng các chức năng bắt buộc đã được hoàn thành. "
            "Nội dung phải bao gồm: mục tiêu dự án, vòng đời phát triển hệ thống, kiểm tra từng hạng mục (tuyên bố sứ mệnh, đánh giá cơ hội, trường hợp kinh doanh, tính khả thi, Project Charter, phê duyệt), danh sách công việc, trạng thái hoàn thành, người chịu trách nhiệm, ghi chú. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/0_initiation` với tên `Initiate_Project_Checklist.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `initiate_project_checklist`."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Tài liệu `Initiate_Project_Checklist.docx` chứa danh sách kiểm tra khởi tạo, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `initiate_project_checklist`."
        ),
        callback=lambda output: create_docx(
            "Danh sách kiểm tra khởi tạo dự án",
            [
                "1. Danh sách công việc: Các bước cần hoàn thành để khởi tạo dự án (lấy từ project_charter và business_case).",
                "2. Trạng thái hoàn thành: Hoàn thành, đang thực hiện, hoặc chưa bắt đầu.",
                "3. Người chịu trách nhiệm: Danh sách người phụ trách từng công việc.",
                "4. Ghi chú: Các thông tin bổ sung hoặc vấn đề cần lưu ý.",
                shared_memory.load("project_charter") or "Không có dữ liệu",
                shared_memory.load("business_case") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/0_initiation/Initiate_Project_Checklist.docx"
        ) and shared_memory.save("initiate_project_checklist", output)
    )

    # Tác vụ xác thực tài liệu
    validate_documents_task = Task(
        description=(
            "Sử dụng công cụ `validate_documents` để kiểm tra và xác thực tất cả các tài liệu khởi tạo (Best Practices, Project Initiation Agenda, Project Charter, Business Case, Feasibility Study, "
            "Value Proposition Template, Project or Issue Submission Form, Project Cost - Benefit Analysis, Project Team Definition, Stakeholder Identification List, Project Resource Plan, Concept Of Operations, Initiate Project Checklist). "
            "Đánh giá tính đầy đủ, chính xác, và phù hợp với các tiêu chuẩn quản lý dự án như PMI hoặc PRINCE2. "
            "Tạo báo cáo xác thực chi tiết, nêu rõ trạng thái của từng tài liệu (đạt, cần chỉnh sửa, không đạt) và đưa ra các khuyến nghị cải thiện nếu cần. "
            "Lưu báo cáo dưới dạng `.docx` và `.xlsx` trong thư mục `output/0_initiation` với tên `Validation_Report.docx` và `Validation_Report.xlsx`. "
            "Lưu kết quả vào SharedMemory với khóa `validation_report`."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Báo cáo xác thực `Validation_Report.docx` và `Validation_Report.xlsx` chứa trạng thái và khuyến nghị cho các tài liệu, "
            "được lưu trong `output/0_initiation` và SharedMemory với khóa `validation_report`."
        ),
        callback=lambda output: (
            create_docx(
                "Báo cáo xác thực tài liệu",
                [
                    "1. Tóm tắt: Tổng quan về trạng thái xác thực của các tài liệu.",
                    "2. Trạng thái từng tài liệu: Best Practices, Project Initiation Agenda, Project Charter, Business Case, Feasibility Study, Value Proposition Template, Project or Issue Submission Form, Project Cost - Benefit Analysis, Project Team Definition, Stakeholder Identification List, Project Resource Plan, Concept Of Operations, Initiate Project Checklist.",
                    "3. Khuyến nghị: Các cải tiến cần thiết cho từng tài liệu (nếu có).",
                    "4. Kết luận: Đánh giá tổng thể về chất lượng tài liệu."
                ],
                f"{output_base_dir}/0_initiation/Validation_Report.docx"
            ) and
            create_xlsx(
                [
                    ["Document", "Status", "Recommendations"],
                    ["Best Practices", "TBD", "TBD"],
                    ["Project Initiation Agenda", "TBD", "TBD"],
                    ["Project Charter", "TBD", "TBD"],
                    ["Business Case", "TBD", "TBD"],
                    ["Feasibility Study", "TBD", "TBD"],
                    ["Value Proposition Template", "TBD", "TBD"],
                    ["Project or Issue Submission Form", "TBD", "TBD"],
                    ["Project Cost - Benefit Analysis", "TBD", "TBD"],
                    ["Project Team Definition", "TBD", "TBD"],
                    ["Stakeholder Identification List", "TBD", "TBD"],
                    ["Project Resource Plan", "TBD", "TBD"],
                    ["Concept Of Operations", "TBD", "TBD"],
                    ["Initiate Project Checklist", "TBD", "TBD"]
                ],
                f"{output_base_dir}/0_initiation/Validation_Report.xlsx"
            ) and
            shared_memory.save("validation_report", output)
        )
    )

    tasks.extend([
        best_practices_task,
        project_initiation_agenda_task,
        project_charter_task,
        business_case_task,
        feasibility_study_task,
        value_proposition_task,
        submission_form_task,
        cost_benefit_analysis_task,
        project_team_definition_task,
        identification_list_task,
        project_resource_plan_task,
        concept_of_operations_task,
        initiate_project_checklist_task,
        validate_documents_task
    ])

    return tasks
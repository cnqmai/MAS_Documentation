from crewai import Task
from utils.output_formats import create_docx, create_xlsx
from memory.shared_memory import SharedMemory
import os

def create_maintenance_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, maintenance_agent):
    """
    Tạo các tác vụ cho giai đoạn Bảo trì (Maintenance Phase).
    """
    tasks = []

    # Tác vụ tạo Lessons Learned
    lessons_learned_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Đúc kết kinh nghiệm (Lessons Learned) dựa trên dữ liệu từ `test_summary_report` và `project_status_report` trong SharedMemory. "
            "Tài liệu này tổng kết những điều làm tốt và những điểm cần cải thiện sau khi dự án kết thúc. "
            "Nội dung phải bao gồm: thảo luận đóng dự án, thành phần tham dự, thành công lớn nhất, các bài học kinh nghiệm, các lĩnh vực (khởi động dự án, lập kế hoạch, quản lý dự án, nhân sự, giao tiếp, kinh phí, chi phí, tiến độ, vai trò và trách nhiệm, quản lý rủi ro, mua sắm, yêu cầu, phạm vi, phát triển, kiểm thử, đào tạo, tài liệu, phê duyệt). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Lessons_Learned.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `lessons_learned`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Lessons_Learned.docx` chứa đúc kết kinh nghiệm, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `lessons_learned`."
        ),
        callback=lambda output: create_docx(
            "Đúc kết kinh nghiệm",
            [
                "1. Thảo luận đóng dự án: Tóm tắt cuộc họp đóng dự án (lấy từ project_status_report).",
                "2. Thành phần tham dự: Danh sách các bên liên quan tham gia.",
                "3. Thành công lớn nhất: Các thành tựu nổi bật của dự án (lấy từ test_summary_report).",
                "4. Bài học kinh nghiệm: Các lĩnh vực cần cải thiện.",
                "5. Các lĩnh vực: Khởi động, lập kế hoạch, quản lý dự án, nhân sự, giao tiếp, kinh phí, tiến độ, rủi ro, yêu cầu, phát triển, kiểm thử, đào tạo, tài liệu, phê duyệt.",
                shared_memory.load("test_summary_report") or "Không có dữ liệu",
                shared_memory.load("project_status_report") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Lessons_Learned.docx"
        ) and shared_memory.save("lessons_learned", output)
    )

    # Tác vụ tạo Transition Out Plan
    transition_out_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Kế hoạch chuyển giao (Transition Out Plan) dựa trên dữ liệu từ `operations_guide` và `system_admin_guide` trong SharedMemory. "
            "Tài liệu này mô tả cách các sản phẩm bàn giao được tích hợp vào vận hành và duy trì sau dự án. "
            "Nội dung phải bao gồm: cách tiếp cận chuyển giao, mục tiêu chuyển giao, tổ chức nhóm chuyển giao, các nhiệm vụ chuyển giao, quy trình chuyển giao kiến thức, triển khai sản phẩm (rollout, di chuyển dữ liệu), kế hoạch truyền thông, lịch trình và bàn giao. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Transition_Out_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `transition_out_plan`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Transition_Out_Plan.docx` chứa kế hoạch chuyển giao, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `transition_out_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch chuyển giao",
            [
                "1. Cách tiếp cận chuyển giao: Phương pháp chuyển giao (lấy từ operations_guide).",
                "2. Mục tiêu chuyển giao: Mục tiêu của quá trình chuyển giao.",
                "3. Tổ chức nhóm chuyển giao: Danh sách thành viên nhóm (lấy từ system_admin_guide).",
                "4. Nhiệm vụ chuyển giao: Các nhiệm vụ cần thực hiện.",
                "5. Quy trình chuyển giao kiến thức: Quy trình đào tạo và chuyển giao kiến thức.",
                "6. Triển khai sản phẩm: Rollout và di chuyển dữ liệu.",
                "7. Kế hoạch truyền thông: Kế hoạch giao tiếp với các bên liên quan.",
                "8. Lịch trình và bàn giao: Lịch trình chi tiết và các mốc bàn giao.",
                shared_memory.load("operations_guide") or "Không có dữ liệu",
                shared_memory.load("system_admin_guide") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Transition_Out_Plan.docx"
        ) and shared_memory.save("transition_out_plan", output)
    )

    # Tác vụ tạo Post Project Survey Questionnaire
    post_project_survey_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Bảng khảo sát đánh giá dự án (Post Project Survey Questionnaire) dựa trên dữ liệu từ `lessons_learned` trong SharedMemory. "
            "Tài liệu này thu thập phản hồi để cải tiến cho các dự án sau. "
            "Nội dung phải bao gồm: vấn đề chung, giao tiếp dự án, lập kế hoạch và tiến độ, thiết kế và triển khai, quy trình kiểm thử, đào tạo và tài liệu, câu hỏi quy trình tổng quát. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Post_Project_Survey_Questionnaire.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `post_project_survey`."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Tài liệu `Post_Project_Survey_Questionnaire.docx` chứa bảng khảo sát đánh giá dự án, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `post_project_survey`."
        ),
        callback=lambda output: create_docx(
            "Bảng khảo sát đánh giá dự án",
            [
                "1. Vấn đề chung: Các vấn đề tổng quát của dự án (lấy từ lessons_learned).",
                "2. Giao tiếp dự án: Đánh giá hiệu quả giao tiếp.",
                "3. Lập kế hoạch và tiến độ: Đánh giá kế hoạch và tiến độ dự án.",
                "4. Thiết kế và triển khai: Đánh giá quá trình thiết kế và triển khai.",
                "5. Quy trình kiểm thử: Đánh giá hiệu quả kiểm thử.",
                "6. Đào tạo và tài liệu: Đánh giá chất lượng đào tạo và tài liệu.",
                "7. Câu hỏi tổng quát: Các câu hỏi mở về quy trình dự án.",
                shared_memory.load("lessons_learned") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Post_Project_Survey_Questionnaire.docx"
        ) and shared_memory.save("post_project_survey", output)
    )

    # Tác vụ tạo Post Project Review
    post_project_review_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Đánh giá sau dự án (Post Project Review) dựa trên dữ liệu từ `lessons_learned` và `project_status_report` trong SharedMemory. "
            "Tài liệu này đánh giá tổng thể hiệu quả triển khai, chi phí, chất lượng, và tiến độ. "
            "Nội dung phải bao gồm: các vấn đề tổng quát, giao tiếp trong dự án, tiến độ và thời gian thực hiện, thiết kế và triển khai, kiểm thử, đào tạo, tài liệu, chi phí (ngân sách và thực tế), phê duyệt. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Post_Project_Review.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `post_project_review`."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Tài liệu `Post_Project_Review.docx` chứa đánh giá sau dự án, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `post_project_review`."
        ),
        callback=lambda output: create_docx(
            "Đánh giá sau dự án",
            [
                "1. Vấn đề tổng quát: Tóm tắt các vấn đề chính (lấy từ lessons_learned).",
                "2. Giao tiếp: Đánh giá giao tiếp trong dự án (lấy từ project_status_report).",
                "3. Tiến độ: Đánh giá tiến độ và thời gian thực hiện.",
                "4. Thiết kế và triển khai: Đánh giá thiết kế và triển khai.",
                "5. Kiểm thử: Đánh giá quy trình kiểm thử.",
                "6. Đào tạo và tài liệu: Đánh giá chất lượng đào tạo và tài liệu.",
                "7. Chi phí: So sánh ngân sách và chi phí thực tế.",
                "8. Phê duyệt: Tình trạng phê duyệt dự án.",
                shared_memory.load("lessons_learned") or "Không có dữ liệu",
                shared_memory.load("project_status_report") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Post_Project_Review.docx"
        ) and shared_memory.save("post_project_review", output)
    )

    # Tác vụ tạo Change Request Document (CCR)
    change_request_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Yêu cầu thay đổi (Change Request Document - CCR) dựa trên dữ liệu từ `requirements_changes_impact_analysis` và `bug_report` trong SharedMemory. "
            "Tài liệu này dùng để đánh giá và phê duyệt các thay đổi đối với hệ thống. "
            "Nội dung phải bao gồm: lý do thay đổi, mô tả, giả định, tác động tới dự án, tác động tiến độ, ước lượng công và chi phí, bảng phân bổ vốn/chi phí, phê duyệt. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Change_Request_Document.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `change_request`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Change_Request_Document.docx` chứa yêu cầu thay đổi, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `change_request`."
        ),
        callback=lambda output: create_docx(
            "Yêu cầu thay đổi",
            [
                "1. Lý do thay đổi: Lý do cần thay đổi (lấy từ requirements_changes_impact_analysis).",
                "2. Mô tả: Mô tả chi tiết thay đổi (lấy từ bug_report).",
                "3. Giả định: Các giả định liên quan đến thay đổi.",
                "4. Tác động tới dự án: Ảnh hưởng đến phạm vi, chất lượng, chi phí.",
                "5. Tác động tiến độ: Ảnh hưởng đến lịch trình dự án.",
                "6. Ước lượng công và chi phí: Công sức và chi phí cần thiết.",
                "7. Phân bổ vốn/chi phí: Bảng phân bổ nguồn lực.",
                "8. Phê duyệt: Quy trình phê duyệt thay đổi.",
                shared_memory.load("requirements_changes_impact_analysis") or "Không có dữ liệu",
                shared_memory.load("bug_report") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Change_Request_Document.docx"
        ) and shared_memory.save("change_request", output)
    )

    # Tác vụ tạo Disaster Recovery Plan
    disaster_recovery_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Kế hoạch khắc phục thảm họa (Disaster Recovery Plan) dựa trên dữ liệu từ `security_architecture` và `system_admin_guide` trong SharedMemory. "
            "Tài liệu này đảm bảo hệ thống có thể khôi phục trong tình huống khẩn cấp. "
            "Nội dung phải bao gồm: định nghĩa, mục tiêu, phạm vi, nhóm phục hồi, thời gian và địa điểm khôi phục, dịch vụ quan trọng, mức độ ưu tiên, quy trình phản hồi (thông báo, đánh giá, xử lý), tuyên bố thảm họa, quy trình phục hồi, kế hoạch phục hồi hệ thống mạng, email, server. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Disaster_Recovery_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `disaster_recovery_plan`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Disaster_Recovery_Plan.docx` chứa kế hoạch khắc phục thảm họa, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `disaster_recovery_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch khắc phục thảm họa",
            [
                "1. Định nghĩa và mục tiêu: Mục tiêu của kế hoạch (lấy từ security_architecture).",
                "2. Phạm vi: Phạm vi áp dụng kế hoạch phục hồi.",
                "3. Nhóm phục hồi: Danh sách nhóm phục hồi (lấy từ system_admin_guide).",
                "4. Thời gian và địa điểm: Thời gian và địa điểm khôi phục.",
                "5. Dịch vụ quan trọng: Các dịch vụ cần ưu tiên khôi phục.",
                "6. Quy trình phản hồi: Thông báo, đánh giá, xử lý sự cố.",
                "7. Tuyên bố thảm họa: Quy trình tuyên bố thảm họa.",
                "8. Kế hoạch phục hồi: Phục hồi mạng, email, server.",
                shared_memory.load("security_architecture") or "Không có dữ liệu",
                shared_memory.load("system_admin_guide") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Disaster_Recovery_Plan.docx"
        ) and shared_memory.save("disaster_recovery_plan", output)
    )

    # Tác vụ tạo Certificate Of Compliance
    certificate_of_compliance_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Giấy chứng nhận nghiệm thu (Certificate Of Compliance) dựa trên dữ liệu từ `test_summary_report` và `project_acceptance` trong SharedMemory. "
            "Tài liệu này xác nhận sản phẩm đã được bàn giao đúng yêu cầu. "
            "Nội dung phải bao gồm: phần nhà thầu (mã đơn hàng, tên sản phẩm bàn giao), phần quản lý dự án (thông tin bàn giao), phòng hợp đồng (xác nhận), chữ ký đại diện nhà thầu và quản lý dự án. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Certificate_Of_Compliance.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `certificate_of_compliance`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Certificate_Of_Compliance.docx` chứa giấy chứng nhận nghiệm thu, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `certificate_of_compliance`."
        ),
        callback=lambda output: create_docx(
            "Giấy chứng nhận nghiệm thu",
            [
                "1. Phần nhà thầu: Mã đơn hàng, tên sản phẩm (lấy từ project_acceptance).",
                "2. Phần quản lý dự án: Thông tin bàn giao (lấy từ test_summary_report).",
                "3. Phòng hợp đồng: Xác nhận bàn giao.",
                "4. Chữ ký: Chữ ký đại diện nhà thầu và quản lý dự án.",
                shared_memory.load("test_summary_report") or "Không có dữ liệu",
                shared_memory.load("project_acceptance") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Certificate_Of_Compliance.docx"
        ) and shared_memory.save("certificate_of_compliance", output)
    )

    # Tác vụ tạo Request For Enhancement
    request_for_enhancement_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Yêu cầu nâng cấp (Request For Enhancement) dựa trên dữ liệu từ `bug_report` và `non_functional_requirements` trong SharedMemory. "
            "Tài liệu này cho phép đề xuất ứng dụng mới hoặc nâng cấp hệ thống. "
            "Nội dung phải bao gồm: thông tin người yêu cầu, loại yêu cầu (mới, nâng cấp, chỉnh sửa nhỏ), mô tả chi tiết, mức độ ưu tiên, rủi ro tiềm ẩn, nguồn tài trợ, dự án liên quan, file đính kèm (nếu có). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Request_For_Enhancement.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `request_for_enhancement`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Request_For_Enhancement.docx` chứa yêu cầu nâng cấp, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `request_for_enhancement`."
        ),
        callback=lambda output: create_docx(
            "Yêu cầu nâng cấp",
            [
                "1. Thông tin người yêu cầu: Thông tin người đề xuất (lấy từ bug_report).",
                "2. Loại yêu cầu: Mới, nâng cấp, chỉnh sửa nhỏ.",
                "3. Mô tả chi tiết: Mô tả yêu cầu nâng cấp (lấy từ non_functional_requirements).",
                "4. Mức độ ưu tiên: Mức độ ưu tiên của yêu cầu.",
                "5. Rủi ro tiềm ẩn: Các rủi ro liên quan.",
                "6. Nguồn tài trợ: Nguồn tài trợ cho yêu cầu.",
                "7. Dự án liên quan: Các dự án liên quan (nếu có).",
                "8. File đính kèm: Tài liệu bổ sung (nếu có).",
                shared_memory.load("bug_report") or "Không có dữ liệu",
                shared_memory.load("non_functional_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Request_For_Enhancement.docx"
        ) and shared_memory.save("request_for_enhancement", output)
    )

    # Tác vụ tạo Product Retirement Plan
    product_retirement_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Kế hoạch ngừng sử dụng sản phẩm (Product Retirement Plan) dựa trên dữ liệu từ `lessons_learned` và `transition_out_plan` trong SharedMemory. "
            "Tài liệu này mô tả chi tiết việc rút sản phẩm ra khỏi môi trường sản xuất. "
            "Nội dung phải bao gồm: thông tin hệ thống/sản phẩm, lý do ngừng sử dụng, chi phí và lợi ích, giả định, ràng buộc, danh sách bên liên quan, rủi ro, lịch trình. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Product_Retirement_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `product_retirement_plan`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Product_Retirement_Plan.docx` chứa kế hoạch ngừng sử dụng sản phẩm, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `product_retirement_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch ngừng sử dụng sản phẩm",
            [
                "1. Thông tin hệ thống: Mô tả hệ thống/sản phẩm (lấy từ lessons_learned).",
                "2. Lý do ngừng sử dụng: Lý do rút sản phẩm (lấy từ transition_out_plan).",
                "3. Chi phí và lợi ích: Phân tích chi phí và lợi ích.",
                "4. Giả định và ràng buộc: Các giả định và ràng buộc liên quan.",
                "5. Bên liên quan: Danh sách các bên liên quan.",
                "6. Rủi ro: Các rủi ro khi ngừng sử dụng.",
                "7. Lịch trình: Lịch trình ngừng sử dụng sản phẩm.",
                shared_memory.load("lessons_learned") or "Không có dữ liệu",
                shared_memory.load("transition_out_plan") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Product_Retirement_Plan.docx"
        ) and shared_memory.save("product_retirement_plan", output)
    )

    # Tác vụ tạo Global Application Support Summary
    global_support_summary_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Tóm tắt hỗ trợ ứng dụng toàn cầu (Global Application Support Summary) dựa trên dữ liệu từ `operations_guide` và `sla_warranty_policies` trong SharedMemory. "
            "Tài liệu này tập hợp dữ liệu về thiết kế, phát triển, hỗ trợ, và bảo mật ứng dụng. "
            "Nội dung phải bao gồm: dữ liệu ứng dụng, thiết kế, phát triển và tích hợp, hỗ trợ sản xuất, hạ tầng, bảo mật, hướng dẫn điền thông tin. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Global_Application_Support_Summary.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `global_support_summary`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Global_Application_Support_Summary.docx` chứa tóm tắt hỗ trợ ứng dụng, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `global_support_summary`."
        ),
        callback=lambda output: create_docx(
            "Tóm tắt hỗ trợ ứng dụng toàn cầu",
            [
                "1. Dữ liệu ứng dụng: Thông tin tổng quan ứng dụng (lấy từ operations_guide).",
                "2. Thiết kế và phát triển: Mô tả thiết kế và tích hợp.",
                "3. Hỗ trợ sản xuất: Quy trình hỗ trợ sản xuất (lấy từ sla_warranty_policies).",
                "4. Hạ tầng: Mô tả hạ tầng hỗ trợ ứng dụng.",
                "5. Bảo mật: Các biện pháp bảo mật ứng dụng.",
                "6. Hướng dẫn điền thông tin: Hướng dẫn cung cấp thông tin hỗ trợ.",
                shared_memory.load("operations_guide") or "Không có dữ liệu",
                shared_memory.load("sla_warranty_policies") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Global_Application_Support_Summary.docx"
        ) and shared_memory.save("global_support_summary", output)
    )

    # Tác vụ tạo Developer Knowledge Transfer Report
    knowledge_transfer_report_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Báo cáo chuyển giao kiến thức (Developer Knowledge Transfer Report) dựa trên dữ liệu từ `source_code_documentation` và `middleware_documentation` trong SharedMemory. "
            "Tài liệu này chuyển giao kiến thức từ nhóm phát triển sang nhóm duy trì hệ thống. "
            "Nội dung phải bao gồm: tài liệu tham khảo, nhân sự chính (người dùng, chuyên gia, lập trình viên), kiến thức kỹ thuật (ngôn ngữ, công cụ, CSDL, hệ điều hành), kiến thức nghiệp vụ, kiến thức ứng dụng (chức năng, luồng xử lý, client/server, môi trường sử dụng). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Developer_Knowledge_Transfer_Report.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `knowledge_transfer_report`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Developer_Knowledge_Transfer_Report.docx` chứa báo cáo chuyển giao kiến thức, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `knowledge_transfer_report`."
        ),
        callback=lambda output: create_docx(
            "Báo cáo chuyển giao kiến thức",
            [
                "1. Tài liệu tham khảo: Các tài liệu liên quan (lấy từ source_code_documentation).",
                "2. Nhân sự chính: Người dùng, chuyên gia, lập trình viên (lấy từ middleware_documentation).",
                "3. Kiến thức kỹ thuật: Ngôn ngữ, công cụ, CSDL, hệ điều hành.",
                "4. Kiến thức nghiệp vụ: Thông tin nghiệp vụ của hệ thống.",
                "5. Kiến thức ứng dụng: Chức năng, luồng xử lý, client/server, môi trường.",
                shared_memory.load("source_code_documentation") or "Không có dữ liệu",
                shared_memory.load("middleware_documentation") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Developer_Knowledge_Transfer_Report.docx"
        ) and shared_memory.save("knowledge_transfer_report", output)
    )

    # Tác vụ tạo Maintenance Checklist
    maintenance_checklist_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Danh sách kiểm tra bảo trì (Maintenance Checklist) dựa trên dữ liệu từ `operations_guide` và `system_admin_guide` trong SharedMemory. "
            "Tài liệu này liệt kê các nhiệm vụ bảo trì để đảm bảo hệ thống hoạt động ổn định. "
            "Nội dung phải bao gồm: danh sách nhiệm vụ bảo trì, tần suất thực hiện, người phụ trách, công cụ sử dụng, kiểm tra hiệu suất, kiểm tra bảo mật, sao lưu và phục hồi. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Maintenance_Checklist.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `maintenance_checklist`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Maintenance_Checklist.docx` chứa danh sách kiểm tra bảo trì, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `maintenance_checklist`."
        ),
        callback=lambda output: create_docx(
            "Danh sách kiểm tra bảo trì",
            [
                "1. Nhiệm vụ bảo trì: Danh sách các nhiệm vụ bảo trì (lấy từ operations_guide).",
                "2. Tần suất thực hiện: Tần suất thực hiện các nhiệm vụ (lấy từ system_admin_guide).",
                "3. Người phụ trách: Danh sách người thực hiện bảo trì.",
                "4. Công cụ sử dụng: Các công cụ hỗ trợ bảo trì.",
                "5. Kiểm tra hiệu suất: Kiểm tra hiệu suất hệ thống.",
                "6. Kiểm tra bảo mật: Kiểm tra các biện pháp bảo mật.",
                "7. Sao lưu và phục hồi: Quy trình sao lưu và phục hồi.",
                shared_memory.load("operations_guide") or "Không có dữ liệu",
                shared_memory.load("system_admin_guide") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Maintenance_Checklist.docx"
        ) and shared_memory.save("maintenance_checklist", output)
    )

    # Tác vụ tạo Issue Reporting Template
    issue_reporting_template_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Mẫu báo cáo sự cố (Issue Reporting Template) dựa trên dữ liệu từ `bug_report` trong SharedMemory. "
            "Tài liệu này cung cấp mẫu để báo cáo các sự cố trong quá trình bảo trì. "
            "Nội dung phải bao gồm: mô tả sự cố, vị trí xuất hiện, mức độ nghiêm trọng, trạng thái, mức ưu tiên, môi trường xảy ra, phương pháp phát hiện, người phụ trách. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Issue_Reporting_Template.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `issue_reporting_template`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Issue_Reporting_Template.docx` chứa mẫu báo cáo sự cố, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `issue_reporting_template`."
        ),
        callback=lambda output: create_docx(
            "Mẫu báo cáo sự cố",
            [
                "1. Mô tả sự cố: Chi tiết về sự cố phát hiện (lấy từ bug_report).",
                "2. Vị trí xuất hiện: Vị trí sự cố trong hệ thống.",
                "3. Mức độ nghiêm trọng: Mức độ ảnh hưởng của sự cố.",
                "4. Trạng thái: Trạng thái hiện tại của sự cố (mới, đang xử lý, đã giải quyết).",
                "5. Mức ưu tiên: Mức độ ưu tiên xử lý.",
                "6. Môi trường xảy ra: Môi trường phát hiện sự cố.",
                "7. Phương pháp phát hiện: Cách thức phát hiện sự cố.",
                "8. Người phụ trách: Người xử lý sự cố.",
                shared_memory.load("bug_report") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Issue_Reporting_Template.docx"
        ) and shared_memory.save("issue_reporting_template", output)
    )

    # Tác vụ tạo SLA and Warranty Policies
    sla_warranty_policies_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Chính sách SLA và bảo hành (SLA and Warranty Policies) dựa trên dữ liệu từ `sla_template` và `non_functional_requirements` trong SharedMemory. "
            "Tài liệu này xác định các chính sách dịch vụ và bảo hành cho hệ thống. "
            "Nội dung phải bao gồm: mục đích, phạm vi, các điều khoản SLA, chính sách bảo hành, thời gian phản hồi, thời gian giải quyết, trách nhiệm các bên, quy trình yêu cầu dịch vụ. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `SLA_and_Warranty_Policies.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `sla_warranty_policies`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `SLA_and_Warranty_Policies.docx` chứa chính sách SLA và bảo hành, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `sla_warranty_policies`."
        ),
        callback=lambda output: create_docx(
            "Chính sách SLA và bảo hành",
            [
                "1. Mục đích: Mục tiêu của chính sách SLA và bảo hành (lấy từ sla_template).",
                "2. Phạm vi: Phạm vi áp dụng của chính sách.",
                "3. Điều khoản SLA: Các điều khoản về dịch vụ (lấy từ non_functional_requirements).",
                "4. Chính sách bảo hành: Chính sách bảo hành hệ thống.",
                "5. Thời gian phản hồi: Thời gian phản hồi yêu cầu dịch vụ.",
                "6. Thời gian giải quyết: Thời gian giải quyết sự cố.",
                "7. Trách nhiệm các bên: Trách nhiệm của nhà cung cấp và khách hàng.",
                "8. Quy trình yêu cầu dịch vụ: Quy trình gửi yêu cầu hỗ trợ.",
                shared_memory.load("sla_template") or "Không có dữ liệu",
                shared_memory.load("non_functional_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/SLA_and_Warranty_Policies.docx"
        ) and shared_memory.save("sla_warranty_policies", output)
    )

    # Tác vụ tạo Security Patch Management Guide
    security_patch_management_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Hướng dẫn quản lý bản vá bảo mật (Security Patch Management Guide) dựa trên dữ liệu từ `security_architecture` và `system_admin_guide` trong SharedMemory. "
            "Tài liệu này hướng dẫn quản lý và áp dụng các bản vá bảo mật cho hệ thống. "
            "Nội dung phải bao gồm: mục đích, quy trình quản lý bản vá, công cụ sử dụng, lịch trình áp dụng bản vá, kiểm thử bản vá, quy trình rollback, báo cáo quản lý bản vá. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Security_Patch_Management_Guide.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `security_patch_management`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Security_Patch_Management_Guide.docx` chứa hướng dẫn quản lý bản vá bảo mật, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `security_patch_management`."
        ),
        callback=lambda output: create_docx(
            "Hướng dẫn quản lý bản vá bảo mật",
            [
                "1. Mục đích: Mục tiêu quản lý bản vá bảo mật (lấy từ security_architecture).",
                "2. Quy trình quản lý: Quy trình áp dụng bản vá (lấy từ system_admin_guide).",
                "3. Công cụ sử dụng: Các công cụ hỗ trợ quản lý bản vá.",
                "4. Lịch trình áp dụng: Lịch trình triển khai bản vá.",
                "5. Kiểm thử bản vá: Quy trình kiểm thử trước khi áp dụng.",
                "6. Quy trình rollback: Kế hoạch khôi phục nếu bản vá thất bại.",
                "7. Báo cáo: Báo cáo quản lý bản vá.",
                shared_memory.load("security_architecture") or "Không có dữ liệu",
                shared_memory.load("system_admin_guide") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Security_Patch_Management_Guide.docx"
        ) and shared_memory.save("security_patch_management", output)
    )

    # Tác vụ tạo Usage Analytics Report
    usage_analytics_report_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Báo cáo phân tích sử dụng (Usage Analytics Report) dựa trên dữ liệu từ `monitoring_alerting_guide` trong SharedMemory. "
            "Tài liệu này phân tích dữ liệu sử dụng hệ thống để tối ưu hóa hiệu suất. "
            "Nội dung phải bao gồm: tổng quan sử dụng, các chỉ số hiệu suất, xu hướng sử dụng, vấn đề phát hiện, khuyến nghị cải tiến, báo cáo chi tiết. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Usage_Analytics_Report.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `usage_analytics_report`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Usage_Analytics_Report.docx` chứa báo cáo phân tích sử dụng, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `usage_analytics_report`."
        ),
        callback=lambda output: create_docx(
            "Báo cáo phân tích sử dụng",
            [
                "1. Tổng quan sử dụng: Tóm tắt dữ liệu sử dụng hệ thống (lấy từ monitoring_alerting_guide).",
                "2. Chỉ số hiệu suất: Các chỉ số hiệu suất chính.",
                "3. Xu hướng sử dụng: Phân tích xu hướng sử dụng hệ thống.",
                "4. Vấn đề phát hiện: Các vấn đề từ dữ liệu giám sát.",
                "5. Khuyến nghị cải tiến: Đề xuất tối ưu hóa hệ thống.",
                "6. Báo cáo chi tiết: Báo cáo chi tiết về dữ liệu sử dụng.",
                shared_memory.load("monitoring_alerting_guide") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Usage_Analytics_Report.docx"
        ) and shared_memory.save("usage_analytics_report", output)
    )

    # Tác vụ tạo Maintenance and Support Plan
    maintenance_support_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_maintenance_plan_document` để tạo tài liệu Kế hoạch bảo trì và hỗ trợ (Maintenance and Support Plan) dựa trên dữ liệu từ `operations_guide` và `sla_warranty_policies` trong SharedMemory. "
            "Tài liệu này mô tả kế hoạch bảo trì và hỗ trợ hệ thống để đảm bảo hoạt động ổn định. "
            "Nội dung phải bao gồm: mục đích, phạm vi, kế hoạch bảo trì, kế hoạch hỗ trợ, lịch trình bảo trì, trách nhiệm các bên, quy trình xử lý sự cố, báo cáo bảo trì. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/7_maintenance` với tên `Maintenance_and_Support_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `maintenance_support_plan`."
        ),
        agent=maintenance_agent,
        expected_output=(
            "Tài liệu `Maintenance_and_Support_Plan.docx` chứa kế hoạch bảo trì và hỗ trợ, "
            "được lưu trong `output/7_maintenance` và SharedMemory với khóa `maintenance_support_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch bảo trì và hỗ trợ",
            [
                "1. Mục đích: Mục tiêu của kế hoạch bảo trì (lấy từ operations_guide).",
                "2. Phạm vi: Phạm vi áp dụng kế hoạch (lấy từ sla_warranty_policies).",
                "3. Kế hoạch bảo trì: Các nhiệm vụ bảo trì định kỳ.",
                "4. Kế hoạch hỗ trợ: Quy trình hỗ trợ kỹ thuật.",
                "5. Lịch trình bảo trì: Lịch trình thực hiện bảo trì.",
                "6. Trách nhiệm các bên: Trách nhiệm của nhóm bảo trì và khách hàng.",
                "7. Quy trình xử lý sự cố: Quy trình xử lý sự cố hệ thống.",
                "8. Báo cáo bảo trì: Báo cáo định kỳ về hoạt động bảo trì.",
                shared_memory.load("operations_guide") or "Không có dữ liệu",
                shared_memory.load("sla_warranty_policies") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/7_maintenance/Maintenance_and_Support_Plan.docx"
        ) and shared_memory.save("maintenance_support_plan", output)
    )

    tasks.extend([
        lessons_learned_task,
        transition_out_plan_task,
        post_project_survey_task,
        post_project_review_task,
        change_request_task,
        disaster_recovery_plan_task,
        certificate_of_compliance_task,
        request_for_enhancement_task,
        product_retirement_plan_task,
        global_support_summary_task,
        knowledge_transfer_report_task,
        maintenance_checklist_task,
        issue_reporting_template_task,
        sla_warranty_policies_task,
        security_patch_management_task,
        usage_analytics_report_task,
        maintenance_support_plan_task
    ])

    return tasks
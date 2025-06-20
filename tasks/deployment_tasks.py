from crewai import Task
from utils.output_formats import create_docx
from memory.shared_memory import SharedMemory
import os

def create_deployment_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, deployment_agent):
    """
    Tạo các tác vụ cho giai đoạn Triển khai (Deployment Phase).
    """
    tasks = []

    # Tác vụ tạo Process Guide
    process_guide_task = Task(
        description=(
            "Sử dụng công cụ `create_deployment_plan_document` để tạo tài liệu Hướng dẫn quy trình (Process Guide) dựa trên dữ liệu từ `build_deployment_plan` trong SharedMemory. "
            "Tài liệu này cung cấp hướng dẫn thực hiện từng bước cho hệ thống hoặc quy trình. "
            "Nội dung phải bao gồm: giới thiệu, mục đích và phạm vi, bối cảnh, đối tượng sử dụng, tài liệu tham chiếu, thông tin quy trình, các thủ tục chính, các nhiệm vụ, chức năng, thông tin bổ sung về quy trình. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/6_deployment` với tên `Process_Guide.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `process_guide`."
        ),
        agent=deployment_agent,
        expected_output=(
            "Tài liệu `Process_Guide.docx` chứa hướng dẫn quy trình, "
            "được lưu trong `output/6_deployment` và SharedMemory với khóa `process_guide`."
        ),
        callback=lambda output: create_docx(
            "Hướng dẫn quy trình",
            [
                "1. Giới thiệu: Mục đích và phạm vi của quy trình (lấy từ build_deployment_plan).",
                "2. Bối cảnh: Ngữ cảnh sử dụng quy trình.",
                "3. Đối tượng sử dụng: Người sử dụng tài liệu.",
                "4. Tài liệu tham chiếu: Các tài liệu liên quan.",
                "5. Thông tin quy trình: Mô tả quy trình triển khai.",
                "6. Thủ tục chính: Các bước thực hiện quy trình.",
                "7. Nhiệm vụ và chức năng: Các nhiệm vụ và chức năng cụ thể.",
                "8. Thông tin bổ sung: Các chi tiết bổ sung về quy trình.",
                shared_memory.load("build_deployment_plan") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/6_deployment/Process_Guide.docx"
        ) and shared_memory.save("process_guide", output)
    )

    # Tác vụ tạo Installation Guide
    installation_guide_task = Task(
        description=(
            "Sử dụng công cụ `create_deployment_plan_document` để tạo tài liệu Hướng dẫn cài đặt (Installation Guide) dựa trên dữ liệu từ `build_deployment_plan` và `system_architecture` trong SharedMemory. "
            "Tài liệu này mô tả chiến lược cài đặt, rủi ro, và bảo mật khi cài đặt hệ thống. "
            "Nội dung phải bao gồm: giới thiệu, mục đích, mục tiêu, các bên liên quan, người liên hệ, thông tin cài đặt, tổng quan hệ thống, phạm vi, môi trường, rủi ro, bảo mật, kế hoạch và yêu cầu tiền cài đặt, lịch trình cài đặt, hướng dẫn cài đặt, các giai đoạn chính, nhiệm vụ, sao lưu và phục hồi, quy trình thay đổi và rollback, hỗ trợ cài đặt, danh sách phần cứng, phần mềm, mạng, cơ sở vật chất. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/6_deployment` với tên `Installation_Guide.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `installation_guide`."
        ),
        agent=deployment_agent,
        expected_output=(
            "Tài liệu `Installation_Guide.docx` chứa hướng dẫn cài đặt, "
            "được lưu trong `output/6_deployment` và SharedMemory với khóa `installation_guide`."
        ),
        callback=lambda output: create_docx(
            "Hướng dẫn cài đặt",
            [
                "1. Giới thiệu: Mục đích và mục tiêu cài đặt (lấy từ build_deployment_plan).",
                "2. Các bên liên quan: Người liên hệ và các bên liên quan (lấy từ system_architecture).",
                "3. Tổng quan hệ thống: Mô tả hệ thống và môi trường cài đặt.",
                "4. Rủi ro và bảo mật: Các rủi ro và biện pháp bảo mật.",
                "5. Yêu cầu tiền cài đặt: Các yêu cầu trước khi cài đặt.",
                "6. Lịch trình cài đặt: Thời gian và các bước cài đặt.",
                "7. Hướng dẫn cài đặt: Các giai đoạn và nhiệm vụ cài đặt.",
                "8. Sao lưu và phục hồi: Quy trình sao lưu và phục hồi.",
                "9. Quy trình rollback: Kế hoạch khôi phục nếu cài đặt thất bại.",
                "10. Hỗ trợ cài đặt: Danh sách phần cứng, phần mềm, mạng, cơ sở vật chất.",
                shared_memory.load("build_deployment_plan") or "Không có dữ liệu",
                shared_memory.load("system_architecture") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/6_deployment/Installation_Guide.docx"
        ) and shared_memory.save("installation_guide", output)
    )

    # Tác vụ tạo Software User Guide
    software_user_guide_task = Task(
        description=(
            "Sử dụng công cụ `create_deployment_plan_document` để tạo tài liệu Hướng dẫn sử dụng phần mềm (Software User Guide) dựa trên dữ liệu từ `functional_requirements` và `ui_design_template` trong SharedMemory. "
            "Tài liệu này hướng dẫn người dùng cuối cách sử dụng phần mềm với minh họa và thao tác cơ bản. "
            "Nội dung phải bao gồm: giới thiệu, mục đích và phạm vi, bối cảnh, đối tượng, tài liệu tham chiếu, tổng quan ứng dụng, thành phần chính, chức năng, lợi ích, phân quyền người dùng, thông tin truy cập, điều hướng, hướng dẫn menu, trang chính, các hành động, thủ tục và chức năng chính. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/6_deployment` với tên `Software_User_Guide.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `software_user_guide`."
        ),
        agent=deployment_agent,
        expected_output=(
            "Tài liệu `Software_User_Guide.docx` chứa hướng dẫn sử dụng phần mềm, "
            "được lưu trong `output/6_deployment` và SharedMemory với khóa `software_user_guide`."
        ),
        callback=lambda output: create_docx(
            "Hướng dẫn sử dụng phần mềm",
            [
                "1. Giới thiệu: Mục đích và phạm vi hướng dẫn (lấy từ functional_requirements).",
                "2. Bối cảnh và đối tượng: Ngữ cảnh và người dùng cuối.",
                "3. Tài liệu tham chiếu: Các tài liệu liên quan.",
                "4. Tổng quan ứng dụng: Thành phần, chức năng, lợi ích (lấy từ ui_design_template).",
                "5. Phân quyền người dùng: Các mức phân quyền.",
                "6. Thông tin truy cập: Hướng dẫn đăng nhập.",
                "7. Điều hướng: Hướng dẫn menu và trang chính.",
                "8. Thủ tục và chức năng: Các thao tác và chức năng chính.",
                shared_memory.load("functional_requirements") or "Không có dữ liệu",
                shared_memory.load("ui_design_template") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/6_deployment/Software_User_Guide.docx"
        ) and shared_memory.save("software_user_guide", output)
    )

    # Tác vụ tạo System Administration Guide
    system_admin_guide_task = Task(
        description=(
            "Sử dụng công cụ `create_deployment_plan_document` để tạo tài liệu Hướng dẫn quản trị hệ thống (System Administration Guide) dựa trên dữ liệu từ `system_architecture` và `security_architecture` trong SharedMemory. "
            "Tài liệu này hướng dẫn quản trị viên hệ thống thực hiện các nhiệm vụ quản trị và bảo trì. "
            "Nội dung phải bao gồm: giới thiệu, mục đích, mục tiêu, tài liệu tham chiếu, thông tin chung hệ thống, tổng quan, tài sản dữ liệu, quy trình xử lý, môi trường (cơ sở vật chất, phần cứng, phần mềm, mạng), quản trị và bảo trì, quản trị máy chủ, tài khoản người dùng, quản trị phần mềm/hệ thống, quản trị cơ sở dữ liệu, sao lưu phục hồi. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/6_deployment` với tên `System_Administration_Guide.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `system_admin_guide`."
        ),
        agent=deployment_agent,
        expected_output=(
            "Tài liệu `System_Administration_Guide.docx` chứa hướng dẫn quản trị hệ thống, "
            "được lưu trong `output/6_deployment` và SharedMemory với khóa `system_admin_guide`."
        ),
        callback=lambda output: create_docx(
            "Hướng dẫn quản trị hệ thống",
            [
                "1. Giới thiệu: Mục đích và mục tiêu quản trị (lấy từ system_architecture).",
                "2. Tài liệu tham chiếu: Các tài liệu liên quan.",
                "3. Tổng quan hệ thống: Mô tả hệ thống và tài sản dữ liệu (lấy từ security_architecture).",
                "4. Môi trường: Cơ sở vật chất, phần cứng, phần mềm, mạng.",
                "5. Quản trị máy chủ: Quản lý và bảo trì máy chủ.",
                "6. Tài khoản người dùng: Quản lý tài khoản người dùng.",
                "7. Quản trị phần mềm/hệ thống: Quản lý phần mềm và hệ thống.",
                "8. Quản trị cơ sở dữ liệu: Quản lý và bảo trì cơ sở dữ liệu.",
                "9. Sao lưu phục hồi: Quy trình sao lưu và phục hồi.",
                shared_memory.load("system_architecture") or "Không có dữ liệu",
                shared_memory.load("security_architecture") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/6_deployment/System_Administration_Guide.docx"
        ) and shared_memory.save("system_admin_guide", output)
    )

    # Tác vụ tạo Operations Guide
    operations_guide_task = Task(
        description=(
            "Sử dụng công cụ `create_deployment_plan_document` để tạo tài liệu Hướng dẫn vận hành (Operations Guide) dựa trên dữ liệu từ `system_architecture` và `build_deployment_plan` trong SharedMemory. "
            "Tài liệu này mô tả các thủ tục vận hành hệ thống và thực hành vận hành tốt. "
            "Nội dung phải bao gồm: giới thiệu, mục đích, đối tượng, thông tin hệ thống, tổng quan, người liên hệ, môi trường, tài sản, giao diện hệ thống, vận hành, quản trị và bảo trì, lịch trình vận hành, phân công trách nhiệm, quy trình vận hành chi tiết, bảo trì và xử lý sự cố, quản lý thay đổi, cấu hình, quản trị hệ thống, phần mềm, máy chủ, cơ sở dữ liệu. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/6_deployment` với tên `Operations_Guide.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `operations_guide`."
        ),
        agent=deployment_agent,
        expected_output=(
            "Tài liệu `Operations_Guide.docx` chứa hướng dẫn vận hành, "
            "được lưu trong `output/6_deployment` và SharedMemory với khóa `operations_guide`."
        ),
        callback=lambda output: create_docx(
            "Hướng dẫn vận hành",
            [
                "1. Giới thiệu: Mục đích và đối tượng hướng dẫn (lấy từ system_architecture).",
                "2. Thông tin hệ thống: Tổng quan, người liên hệ, môi trường (lấy từ build_deployment_plan).",
                "3. Giao diện hệ thống: Mô tả giao diện vận hành.",
                "4. Lịch trình vận hành: Thời gian và phân công trách nhiệm.",
                "5. Quy trình vận hành: Các bước vận hành chi tiết.",
                "6. Bảo trì và xử lý sự cố: Quy trình bảo trì và xử lý lỗi.",
                "7. Quản lý thay đổi: Quy trình quản lý thay đổi và cấu hình.",
                "8. Quản trị hệ thống: Quản lý hệ thống, phần mềm, máy chủ, cơ sở dữ liệu.",
                shared_memory.load("system_architecture") or "Không có dữ liệu",
                shared_memory.load("build_deployment_plan") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/6_deployment/Operations_Guide.docx"
        ) and shared_memory.save("operations_guide", output)
    )

    # Tác vụ tạo Production Implementation Plan
    production_implementation_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_deployment_plan_document` để tạo tài liệu Kế hoạch triển khai sản phẩm (Production Implementation Plan) dựa trên dữ liệu từ `build_deployment_plan` và `test_summary_report` trong SharedMemory. "
            "Tài liệu này hướng dẫn từng bước đưa ứng dụng vào môi trường sản xuất. "
            "Nội dung phải bao gồm: mô tả triển khai sản phẩm, mục tiêu, thiết bị bị ảnh hưởng, các bước bàn giao sản phẩm, thông tin hỗ trợ kỹ thuật, tác động tiềm tàng, thành phần phần mềm, phần cứng và bước triển khai tương ứng, kiểm thử và chấp nhận, kế hoạch rollback và dự phòng, đào tạo người dùng và tài liệu, liên hệ khẩn cấp khác. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/6_deployment` với tên `Production_Implementation_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `production_implementation_plan`."
        ),
        agent=deployment_agent,
        expected_output=(
            "Tài liệu `Production_Implementation_Plan.docx` chứa kế hoạch triển khai sản phẩm, "
            "được lưu trong `output/6_deployment` và SharedMemory với khóa `production_implementation_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch triển khai sản phẩm",
            [
                "1. Mô tả triển khai: Mô tả quy trình triển khai (lấy từ build_deployment_plan).",
                "2. Mục tiêu: Mục tiêu triển khai sản phẩm.",
                "3. Thiết bị bị ảnh hưởng: Các thiết bị liên quan (lấy từ test_summary_report).",
                "4. Bước bàn giao: Các bước bàn giao sản phẩm.",
                "5. Hỗ trợ kỹ thuật: Thông tin hỗ trợ kỹ thuật.",
                "6. Tác động tiềm tàng: Các tác động có thể xảy ra.",
                "7. Thành phần triển khai: Phần mềm, phần cứng và các bước triển khai.",
                "8. Kiểm thử và chấp nhận: Quy trình kiểm thử sau triển khai.",
                "9. Kế hoạch rollback: Kế hoạch dự phòng và rollback.",
                "10. Đào tạo và tài liệu: Đào tạo người dùng và tài liệu hỗ trợ.",
                "11. Liên hệ khẩn cấp: Danh sách liên hệ khẩn cấp.",
                shared_memory.load("build_deployment_plan") or "Không có dữ liệu",
                shared_memory.load("test_summary_report") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/6_deployment/Production_Implementation_Plan.docx"
        ) and shared_memory.save("production_implementation_plan", output)
    )

    # Tác vụ tạo Production Turnover Approval
    production_turnover_approval_task = Task(
        description=(
            "Sử dụng công cụ `create_deployment_plan_document` để tạo tài liệu Phê duyệt bàn giao sản xuất (Production Turnover Approval) dựa trên dữ liệu từ `project_acceptance` và `test_summary_report` trong SharedMemory. "
            "Tài liệu này đảm bảo các thay đổi được kiểm thử, phê duyệt và chuyển giao an toàn. "
            "Nội dung phải bao gồm: giới thiệu, mục đích, tổng quan hệ thống/dự án, phạm vi, yêu cầu phê duyệt bàn giao, phê duyệt và ký xác nhận. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/6_deployment` với tên `Production_Turnover_Approval.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `production_turnover_approval`."
        ),
        agent=deployment_agent,
        expected_output=(
            "Tài liệu `Production_Turnover_Approval.docx` chứa phê duyệt bàn giao sản xuất, "
            "được lưu trong `output/6_deployment` và SharedMemory với khóa `production_turnover_approval`."
        ),
        callback=lambda output: create_docx(
            "Phê duyệt bàn giao sản xuất",
            [
                "1. Giới thiệu: Mục đích của phê duyệt bàn giao (lấy từ project_acceptance).",
                "2. Tổng quan hệ thống: Mô tả hệ thống/dự án (lấy từ test_summary_report).",
                "3. Phạm vi: Phạm vi bàn giao sản xuất.",
                "4. Yêu cầu phê duyệt: Các yêu cầu để phê duyệt bàn giao.",
                "5. Phê duyệt và ký xác nhận: Chữ ký của các bên liên quan.",
                shared_memory.load("project_acceptance") or "Không có dữ liệu",
                shared_memory.load("test_summary_report") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/6_deployment/Production_Turnover_Approval.docx"
        ) and shared_memory.save("production_turnover_approval", output)
    )

    # Tác vụ tạo Deployment Plan
    deployment_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_deployment_plan_document` để tạo tài liệu Kế hoạch triển khai (Deployment Plan) dựa trên dữ liệu từ `build_deployment_plan` và `production_implementation_plan` trong SharedMemory. "
            "Tài liệu này chi tiết hóa các bước triển khai hệ thống vào môi trường sản xuất. "
            "Nội dung phải bao gồm: mục đích, phạm vi, chiến lược triển khai, lịch trình triển khai, các bước triển khai, môi trường triển khai, kiểm thử sau triển khai, kế hoạch rollback, hỗ trợ sau triển khai. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/6_deployment` với tên `Deployment_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `deployment_plan`."
        ),
        agent=deployment_agent,
        expected_output=(
            "Tài liệu `Deployment_Plan.docx` chứa kế hoạch triển khai, "
            "được lưu trong `output/6_deployment` và SharedMemory với khóa `deployment_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch triển khai",
            [
                "1. Mục đích: Mục tiêu của kế hoạch triển khai (lấy từ build_deployment_plan).",
                "2. Phạm vi: Phạm vi triển khai hệ thống (lấy từ production_implementation_plan).",
                "3. Chiến lược triển khai: Phương pháp triển khai (blue-green, canary,...).",
                "4. Lịch trình triển khai: Thời gian và các mốc triển khai.",
                "5. Các bước triển khai: Các bước chi tiết để triển khai.",
                "6. Môi trường triển khai: Môi trường sản xuất và staging.",
                "7. Kiểm thử sau triển khai: Quy trình kiểm thử sau triển khai.",
                "8. Kế hoạch rollback: Kế hoạch khôi phục nếu triển khai thất bại.",
                "9. Hỗ trợ sau triển khai: Hỗ trợ kỹ thuật sau triển khai.",
                shared_memory.load("build_deployment_plan") or "Không có dữ liệu",
                shared_memory.load("production_implementation_plan") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/6_deployment/Deployment_Plan.docx"
        ) and shared_memory.save("deployment_plan", output)
    )

    # Tác vụ tạo Monitoring and Alerting Setup Guide
    monitoring_alerting_guide_task = Task(
        description=(
            "Sử dụng công cụ `create_deployment_plan_document` để tạo tài liệu Hướng dẫn thiết lập giám sát và cảnh báo (Monitoring and Alerting Setup Guide) dựa trên dữ liệu từ `system_admin_guide` và `non_functional_requirements` trong SharedMemory. "
            "Tài liệu này hướng dẫn thiết lập hệ thống giám sát và cảnh báo để đảm bảo hệ thống hoạt động ổn định. "
            "Nội dung phải bao gồm: mục đích, công cụ giám sát, cấu hình giám sát, các chỉ số cần theo dõi, thiết lập cảnh báo, quy trình xử lý sự cố, báo cáo giám sát. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/6_deployment` với tên `Monitoring_and_Alerting_Setup_Guide.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `monitoring_alerting_guide`."
        ),
        agent=deployment_agent,
        expected_output=(
            "Tài liệu `Monitoring_and_Alerting_Setup_Guide.docx` chứa hướng dẫn thiết lập giám sát và cảnh báo, "
            "được lưu trong `output/6_deployment` và SharedMemory với khóa `monitoring_alerting_guide`."
        ),
        callback=lambda output: create_docx(
            "Hướng dẫn thiết lập giám sát và cảnh báo",
            [
                "1. Mục đích: Mục tiêu của giám sát và cảnh báo (lấy từ system_admin_guide).",
                "2. Công cụ giám sát: Các công cụ được sử dụng (Prometheus, Grafana,...).",
                "3. Cấu hình giám sát: Hướng dẫn cấu hình hệ thống giám sát.",
                "4. Chỉ số theo dõi: Các chỉ số hiệu suất và trạng thái (lấy từ non_functional_requirements).",
                "5. Thiết lập cảnh báo: Quy tắc và ngưỡng cảnh báo.",
                "6. Quy trình xử lý sự cố: Quy trình xử lý khi nhận cảnh báo.",
                "7. Báo cáo giám sát: Báo cáo định kỳ về trạng thái hệ thống.",
                shared_memory.load("system_admin_guide") or "Không có dữ liệu",
                shared_memory.load("non_functional_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/6_deployment/Monitoring_and_Alerting_Setup_Guide.docx"
        ) and shared_memory.save("monitoring_alerting_guide", output)
    )

    tasks.extend([
        process_guide_task,
        installation_guide_task,
        software_user_guide_task,
        system_admin_guide_task,
        operations_guide_task,
        production_implementation_plan_task,
        production_turnover_approval_task,
        deployment_plan_task,
        monitoring_alerting_guide_task
    ])

    return tasks
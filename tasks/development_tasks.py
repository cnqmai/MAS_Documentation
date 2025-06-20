from crewai import Task
from utils.output_formats import create_docx, create_xlsx
from memory.shared_memory import SharedMemory
import os

def create_development_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, development_agent):
    """
    Tạo các tác vụ cho giai đoạn Phát triển (Development Phase).
    """
    tasks = []

    # Tác vụ tạo Development Standards Document
    dev_standards_task = Task(
        description=(
            "Sử dụng công cụ `create_development_document` để tạo tài liệu Tiêu chuẩn phát triển (Development Standards Document) dựa trên dữ liệu từ `technical_requirements` và `project_plan` trong SharedMemory. "
            "Tài liệu này xác định các tiêu chuẩn phát triển phần mềm để đảm bảo chất lượng mã nguồn và tuân thủ yêu cầu kỹ thuật. "
            "Nội dung phải bao gồm: mục đích, phạm vi, tiêu chuẩn mã hóa, công cụ phát triển, quy trình kiểm soát chất lượng, yêu cầu tài liệu, tiêu chuẩn hiệu suất và bảo mật. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/4_development` với tên `Development_Standards_Document.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `dev_standards`."
        ),
        agent=development_agent,
        expected_output=(
            "Tài liệu `Development_Standards_Document.docx` chứa tiêu chuẩn phát triển, "
            "được lưu trong `output/4_development` và SharedMemory với khóa `dev_standards`."
        ),
        callback=lambda output: create_docx(
            "Tiêu chuẩn phát triển",
            [
                "1. Mục đích: Mục tiêu của tiêu chuẩn phát triển (lấy từ technical_requirements).",
                "2. Phạm vi: Phạm vi áp dụng của tiêu chuẩn.",
                "3. Tiêu chuẩn mã hóa: Quy tắc và chuẩn mã hóa (lấy từ project_plan).",
                "4. Công cụ phát triển: Các công cụ và môi trường phát triển.",
                "5. Kiểm soát chất lượng: Quy trình kiểm tra và đánh giá mã.",
                "6. Yêu cầu tài liệu: Tiêu chuẩn tài liệu mã nguồn.",
                "7. Hiệu suất và bảo mật: Yêu cầu về hiệu suất và bảo mật.",
                shared_memory.load("technical_requirements") or "Không có dữ liệu",
                shared_memory.load("project_plan") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/4_development/Development_Standards_Document.docx"
        ) and shared_memory.save("dev_standards", output)
    )

    # Tác vụ tạo Coding Guidelines
    coding_guidelines_task = Task(
        description=(
            "Sử dụng công cụ `create_development_document` để tạo tài liệu Hướng dẫn mã hóa (Coding Guidelines) dựa trên dữ liệu từ `dev_standards` trong SharedMemory. "
            "Tài liệu này cung cấp các quy tắc cụ thể để viết mã nguồn, đảm bảo tính nhất quán, dễ đọc, và dễ bảo trì. "
            "Nội dung phải bao gồm: phong cách mã hóa, quy ước đặt tên, cấu trúc mã, quản lý lỗi, bình luận mã, và các ví dụ minh họa. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/4_development` với tên `Coding_Guidelines.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `coding_guidelines`."
        ),
        agent=development_agent,
        expected_output=(
            "Tài liệu `Coding_Guidelines.docx` chứa hướng dẫn mã hóa, "
            "được lưu trong `output/4_development` và SharedMemory với khóa `coding_guidelines`."
        ),
        callback=lambda output: create_docx(
            "Hướng dẫn mã hóa",
            [
                "1. Phong cách mã hóa: Quy tắc về định dạng mã (lấy từ dev_standards).",
                "2. Quy ước đặt tên: Quy tắc đặt tên biến, hàm, và lớp.",
                "3. Cấu trúc mã: Tổ chức mã nguồn và cấu trúc thư mục.",
                "4. Quản lý lỗi: Xử lý ngoại lệ và lỗi.",
                "5. Bình luận mã: Quy tắc viết bình luận và tài liệu mã.",
                "6. Ví dụ minh họa: Các đoạn mã mẫu tuân thủ hướng dẫn.",
                shared_memory.load("dev_standards") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/4_development/Coding_Guidelines.docx"
        ) and shared_memory.save("coding_guidelines", output)
    )

    # Tác vụ tạo Version Control Plan
    version_control_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_development_document` để tạo tài liệu Kế hoạch kiểm soát phiên bản (Version Control Plan) dựa trên dữ liệu từ `dev_standards` trong SharedMemory. "
            "Tài liệu này mô tả quy trình quản lý phiên bản mã nguồn, đảm bảo tính nhất quán và khả năng truy vết. "
            "Nội dung phải bao gồm: mục đích, công cụ kiểm soát phiên bản, quy trình branch và merge, quy tắc commit, quản lý tag và release, quy trình sao lưu. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/4_development` với tên `Version_Control_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `version_control_plan`."
        ),
        agent=development_agent,
        expected_output=(
            "Tài liệu `Version_Control_Plan.docx` chứa kế hoạch kiểm soát phiên bản, "
            "được lưu trong `output/4_development` và SharedMemory với khóa `version_control_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch kiểm soát phiên bản",
            [
                "1. Mục đích: Mục tiêu của kiểm soát phiên bản (lấy từ dev_standards).",
                "2. Công cụ: Công cụ kiểm soát phiên bản (Git, SVN, v.v.).",
                "3. Quy trình branch và merge: Quy tắc tạo branch và merge mã.",
                "4. Quy tắc commit: Quy tắc viết thông điệp commit.",
                "5. Quản lý tag và release: Quy trình đánh tag và phát hành.",
                "6. Sao lưu: Quy trình sao lưu kho mã nguồn.",
                shared_memory.load("dev_standards") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/4_development/Version_Control_Plan.docx"
        ) and shared_memory.save("version_control_plan", output)
    )

    # Tác vụ tạo Integration Plan
    integration_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_development_document` để tạo tài liệu Kế hoạch tích hợp (Integration Plan) dựa trên dữ liệu từ `system_architecture` và `api_design` trong SharedMemory. "
            "Tài liệu này mô tả quy trình tích hợp các thành phần hệ thống, bao gồm API và các module khác. "
            "Nội dung phải bao gồm: mục đích, phạm vi, chiến lược tích hợp, lịch trình tích hợp, các thành phần tích hợp, yêu cầu môi trường, quy trình kiểm thử tích hợp. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/4_development` với tên `Integration_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `integration_plan`."
        ),
        agent=development_agent,
        expected_output=(
            "Tài liệu `Integration_Plan.docx` chứa kế hoạch tích hợp, "
            "được lưu trong `output/4_development` và SharedMemory với khóa `integration_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch tích hợp",
            [
                "1. Mục đích: Mục tiêu của kế hoạch tích hợp (lấy từ system_architecture).",
                "2. Phạm vi: Phạm vi tích hợp các thành phần hệ thống.",
                "3. Chiến lược tích hợp: Phương pháp tích hợp (top-down, bottom-up).",
                "4. Lịch trình: Lịch trình tích hợp các thành phần.",
                "5. Thành phần tích hợp: Các module và API (lấy từ api_design).",
                "6. Yêu cầu môi trường: Môi trường cần thiết để tích hợp.",
                "7. Kiểm thử tích hợp: Quy trình kiểm thử tích hợp.",
                shared_memory.load("system_architecture") or "Không có dữ liệu",
                shared_memory.load("api_design") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/4_development/Integration_Plan.docx"
        ) and shared_memory.save("integration_plan", output)
    )

    # Tác vụ tạo Code Review Checklist
    code_review_checklist_task = Task(
        description=(
            "Sử dụng công cụ `create_development_document` để tạo tài liệu Danh sách kiểm tra đánh giá mã nguồn (Code Review Checklist) dựa trên dữ liệu từ `coding_guidelines` và `technical_requirements` trong SharedMemory. "
            "Tài liệu này đảm bảo chất lượng mã nguồn bằng cách kiểm tra tính tuân thủ các tiêu chuẩn mã hóa và yêu cầu kỹ thuật. "
            "Nội dung phải bao gồm: cấu trúc mã, tài liệu, biến, kiểu dữ liệu, phong cách lập trình, cấu trúc điều khiển, vòng lặp, bảo trì, bảo mật, kiểm tra lỗi, xử lý ngoại lệ, thử nghiệm, xác thực. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/4_development` với tên `Code_Review_Checklist.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `code_review_checklist`."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Tài liệu `Code_Review_Checklist.docx` chứa danh sách kiểm tra đánh giá mã nguồn, "
            "được lưu trong `output/4_development` và SharedMemory với khóa `code_review_checklist`."
        ),
        callback=lambda output: create_docx(
            "Danh sách kiểm tra đánh giá mã nguồn",
            [
                "1. Cấu trúc mã: Cấu trúc và tổ chức mã nguồn (lấy từ coding_guidelines).",
                "2. Tài liệu: Bình luận và tài liệu mã (lấy từ technical_requirements).",
                "3. Biến và kiểu dữ liệu: Kiểm tra biến và kiểu dữ liệu.",
                "4. Phong cách lập trình: Tuân thủ chuẩn mã hóa.",
                "5. Điều khiển và vòng lặp: Cấu trúc điều khiển và vòng lặp.",
                "6. Bảo mật và bảo trì: Các biện pháp bảo mật và khả năng bảo trì.",
                "7. Kiểm tra lỗi: Xử lý ngoại lệ và kiểm tra lỗi.",
                shared_memory.load("coding_guidelines") or "Không có dữ liệu",
                shared_memory.load("technical_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/4_development/Code_Review_Checklist.docx"
        ) and shared_memory.save("code_review_checklist", output)
    )

    # Tác vụ tạo Source Code Repository Checklist
    source_code_repo_checklist_task = Task(
        description=(
            "Sử dụng công cụ `create_development_document` để tạo tài liệu Danh sách kiểm tra kho mã nguồn (Source Code Repository Checklist) dựa trên dữ liệu từ `version_control_plan` trong SharedMemory. "
            "Tài liệu này đảm bảo kho mã nguồn được thiết lập và quản lý đúng cách. "
            "Nội dung phải bao gồm: cấu hình kho mã, quyền truy cập, cấu trúc thư mục, quy tắc commit, kiểm tra bảo mật, sao lưu, và giám sát kho. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/4_development` với tên `Source_Code_Repository_Checklist.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `source_code_repo_checklist`."
        ),
        agent=development_agent,
        expected_output=(
            "Tài liệu `Source_Code_Repository_Checklist.docx` chứa danh sách kiểm tra kho mã nguồn, "
            "được lưu trong `output/4_development` và SharedMemory với khóa `source_code_repo_checklist`."
        ),
        callback=lambda output: create_docx(
            "Danh sách kiểm tra kho mã nguồn",
            [
                "1. Cấu hình kho mã: Thiết lập kho mã nguồn (lấy từ version_control_plan).",
                "2. Quyền truy cập: Phân quyền truy cập kho mã.",
                "3. Cấu trúc thư mục: Tổ chức thư mục trong kho.",
                "4. Quy tắc commit: Quy tắc commit mã nguồn.",
                "5. Bảo mật: Kiểm tra bảo mật kho mã.",
                "6. Sao lưu: Quy trình sao lưu kho mã.",
                "7. Giám sát: Giám sát hoạt động kho mã.",
                shared_memory.load("version_control_plan") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/4_development/Source_Code_Repository_Checklist.docx"
        ) and shared_memory.save("source_code_repo_checklist", output)
    )

    # Tác vụ tạo Development Progress Report
    dev_progress_report_task = Task(
        description=(
            "Sử dụng công cụ `create_development_document` để tạo tài liệu Báo cáo tiến độ phát triển (Development Progress Report) dựa trên dữ liệu từ `project_plan` và `wbs` trong SharedMemory. "
            "Tài liệu này theo dõi tiến độ phát triển, bao gồm các nhiệm vụ đã hoàn thành, đang thực hiện, và các vấn đề phát sinh. "
            "Nội dung phải bao gồm: tổng quan tiến độ, nhiệm vụ hoàn thành, nhiệm vụ đang thực hiện, rủi ro và vấn đề, kế hoạch tiếp theo. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/4_development` với tên `Development_Progress_Report.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `dev_progress_report`."
        ),
        agent=development_agent,
        expected_output=(
            "Tài liệu `Development_Progress_Report.docx` chứa báo cáo tiến độ phát triển, "
            "được lưu trong `output/4_development` và SharedMemory với khóa `dev_progress_report`."
        ),
        callback=lambda output: create_docx(
            "Báo cáo tiến độ phát triển",
            [
                "1. Tổng quan tiến độ: Tóm tắt tiến độ dự án (lấy từ project_plan).",
                "2. Nhiệm vụ hoàn thành: Các nhiệm vụ đã hoàn thành (lấy từ wbs).",
                "3. Nhiệm vụ đang thực hiện: Các nhiệm vụ đang tiến hành.",
                "4. Rủi ro và vấn đề: Các vấn đề phát sinh và rủi ro.",
                "5. Kế hoạch tiếp theo: Các bước tiếp theo trong phát triển.",
                shared_memory.load("project_plan") or "Không có dữ liệu",
                shared_memory.load("wbs") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/4_development/Development_Progress_Report.docx"
        ) and shared_memory.save("dev_progress_report", output)
    )

    # Tác vụ tạo Build and Deployment Plan
    build_deployment_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_development_document` để tạo tài liệu Kế hoạch xây dựng và triển khai (Build and Deployment Plan) dựa trên dữ liệu từ `integration_plan` và `system_architecture` trong SharedMemory. "
            "Tài liệu này mô tả quy trình xây dựng và triển khai hệ thống, đảm bảo hệ thống được triển khai chính xác và ổn định. "
            "Nội dung phải bao gồm: mục đích, chiến lược xây dựng, công cụ xây dựng, quy trình triển khai, môi trường triển khai, kiểm thử sau triển khai, kế hoạch rollback. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/4_development` với tên `Build_and_Deployment_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `build_deployment_plan`."
        ),
        agent=development_agent,
        expected_output=(
            "Tài liệu `Build_and_Deployment_Plan.docx` chứa kế hoạch xây dựng và triển khai, "
            "được lưu trong `output/4_development` và SharedMemory với khóa `build_deployment_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch xây dựng và triển khai",
            [
                "1. Mục đích: Mục tiêu của kế hoạch triển khai (lấy từ integration_plan).",
                "2. Chiến lược xây dựng: Quy trình xây dựng hệ thống.",
                "3. Công cụ xây dựng: Các công cụ CI/CD (lấy từ system_architecture).",
                "4. Quy trình triển khai: Các bước triển khai hệ thống.",
                "5. Môi trường triển khai: Môi trường staging và production.",
                "6. Kiểm thử sau triển khai: Quy trình kiểm thử sau triển khai.",
                "7. Kế hoạch rollback: Kế hoạch khôi phục nếu triển khai thất bại.",
                shared_memory.load("integration_plan") or "Không có dữ liệu",
                shared_memory.load("system_architecture") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/4_development/Build_and_Deployment_Plan.docx"
        ) and shared_memory.save("build_deployment_plan", output)
    )

    # Tác vụ tạo Middleware Documentation
    middleware_documentation_task = Task(
        description=(
            "Sử dụng công cụ `create_development_document` để tạo tài liệu Tài liệu middleware (Middleware Documentation) dựa trên dữ liệu từ `integration_plan` và `api_design` trong SharedMemory. "
            "Tài liệu này mô tả các thành phần middleware được sử dụng để tích hợp hệ thống. "
            "Nội dung phải bao gồm: tổng quan middleware, các thành phần middleware, cấu hình, tích hợp API, hiệu suất và bảo mật, quy trình bảo trì. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/4_development` với tên `Middleware_Documentation.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `middleware_documentation`."
        ),
        agent=development_agent,
        expected_output=(
            "Tài liệu `Middleware_Documentation.docx` chứa tài liệu middleware, "
            "được lưu trong `output/4_development` và SharedMemory với khóa `middleware_documentation`."
        ),
        callback=lambda output: create_docx(
            "Tài liệu middleware",
            [
                "1. Tổng quan middleware: Mô tả vai trò middleware (lấy từ integration_plan).",
                "2. Thành phần middleware: Các thành phần middleware được sử dụng.",
                "3. Cấu hình: Hướng dẫn cấu hình middleware.",
                "4. Tích hợp API: Tích hợp với các API (lấy từ api_design).",
                "5. Hiệu suất và bảo mật: Yêu cầu về hiệu suất và bảo mật.",
                "6. Quy trình bảo trì: Bảo trì và giám sát middleware.",
                shared_memory.load("integration_plan") or "Không có dữ liệu",
                shared_memory.load("api_design") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/4_development/Middleware_Documentation.docx"
        ) and shared_memory.save("middleware_documentation", output)
    )

    # Tác vụ tạo Source Code Documentation
    source_code_documentation_task = Task(
        description=(
            "Sử dụng công cụ `create_development_document` để tạo tài liệu Tài liệu mã nguồn (Source Code Documentation) dựa trên dữ liệu từ `lld` và `coding_guidelines` trong SharedMemory. "
            "Tài liệu này cung cấp tài liệu chi tiết về mã nguồn, hỗ trợ bảo trì và phát triển tiếp theo. "
            "Nội dung phải bao gồm: tổng quan mã nguồn, cấu trúc module, mô tả chức năng, bình luận mã, hướng dẫn sử dụng, các ví dụ mã. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/4_development` với tên `Source_Code_Documentation.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `source_code_documentation`."
        ),
        agent=development_agent,
        expected_output=(
            "Tài liệu `Source_Code_Documentation.docx` chứa tài liệu mã nguồn, "
            "được lưu trong `output/4_development` và SharedMemory với khóa `source_code_documentation`."
        ),
        callback=lambda output: create_docx(
            "Tài liệu mã nguồn",
            [
                "1. Tổng quan mã nguồn: Mô tả tổng thể mã nguồn (lấy từ lld).",
                "2. Cấu trúc module: Tổ chức các module mã nguồn.",
                "3. Mô tả chức năng: Chức năng của từng module.",
                "4. Bình luận mã: Bình luận tuân thủ chuẩn (lấy từ coding_guidelines).",
                "5. Hướng dẫn sử dụng: Cách sử dụng mã nguồn.",
                "6. Ví dụ mã: Các đoạn mã minh họa.",
                shared_memory.load("lld") or "Không có dữ liệu",
                shared_memory.load("coding_guidelines") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/4_development/Source_Code_Documentation.docx"
        ) and shared_memory.save("source_code_documentation", output)
    )

    tasks.extend([
        dev_standards_task,
        coding_guidelines_task,
        version_control_plan_task,
        integration_plan_task,
        code_review_checklist_task,
        source_code_repo_checklist_task,
        dev_progress_report_task,
        build_deployment_plan_task,
        middleware_documentation_task,
        source_code_documentation_task
    ])

    return tasks
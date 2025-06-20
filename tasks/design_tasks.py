from crewai import Task
from utils.output_formats import create_docx, create_xlsx
from memory.shared_memory import SharedMemory
import os

def create_design_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, design_agent):
    """
    Tạo các tác vụ cho giai đoạn Thiết kế (Design Phase).
    """
    tasks = []

    # Tác vụ tạo System Requirements Specifications
    srs_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Đặc tả yêu cầu hệ thống (System Requirements Specifications - SRS) dựa trên dữ liệu từ `brd`, `functional_requirements`, và `non_functional_requirements` trong SharedMemory. "
            "Tài liệu này cung cấp yêu cầu hệ thống chi tiết, đảm bảo hệ thống được xây dựng đúng yêu cầu và chất lượng. "
            "Nội dung phải bao gồm: giới thiệu, mục đích, phạm vi, vai trò và trách nhiệm, yêu cầu hệ thống, yêu cầu chức năng, yêu cầu phần mềm/phần cứng, đặc điểm người dùng, khả năng sử dụng, môi trường vận hành, bảo mật, tuân thủ quy định, khôi phục thảm họa, thông số dữ liệu, ảnh hưởng đến mạng. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `System_Requirements_Specifications.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `srs`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `System_Requirements_Specifications.docx` chứa đặc tả yêu cầu hệ thống, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `srs`."
        ),
        callback=lambda output: create_docx(
            "Đặc tả yêu cầu hệ thống",
            [
                "1. Giới thiệu: Mục đích và phạm vi của SRS (lấy từ brd).",
                "2. Vai trò và trách nhiệm: Các bên liên quan và trách nhiệm.",
                "3. Yêu cầu chức năng: Chi tiết chức năng hệ thống (lấy từ functional_requirements).",
                "4. Yêu cầu phi chức năng: Hiệu suất, bảo mật, khả năng sử dụng (lấy từ non_functional_requirements).",
                "5. Yêu cầu phần mềm/phần cứng: Yêu cầu kỹ thuật.",
                "6. Môi trường vận hành: Máy tính, mạng, và cơ sở hạ tầng.",
                "7. Bảo mật: Yêu cầu bảo mật và tuân thủ quy định.",
                "8. Khôi phục thảm họa: Kế hoạch dự phòng.",
                shared_memory.load("brd") or "Không có dữ liệu",
                shared_memory.load("functional_requirements") or "Không có dữ liệu",
                shared_memory.load("non_functional_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/System_Requirements_Specifications.docx"
        ) and shared_memory.save("srs", output)
    )

    # Tác vụ tạo Analysis and Design Document
    analysis_design_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Phân tích và thiết kế (Analysis and Design Document) dựa trên dữ liệu từ `srs` trong SharedMemory. "
            "Tài liệu này phân tích và thiết kế hệ thống, bao gồm luồng dữ liệu, kiến trúc phần mềm hiện tại và tương lai, tích hợp, bảo mật. "
            "Nội dung phải bao gồm: tổng quan hệ thống, hạ tầng, giả định thiết kế, tóm tắt thay đổi từ khởi tạo, tác động đến kinh doanh, ứng dụng, kiến trúc hiện tại và đề xuất, bảo mật và kiểm toán, thiết kế giao diện, tầng ứng dụng, thông tin triển khai, cải tiến trong tương lai, phê duyệt. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `Analysis_and_Design_Document.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `analysis_design`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `Analysis_and_Design_Document.docx` chứa phân tích và thiết kế hệ thống, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `analysis_design`."
        ),
        callback=lambda output: create_docx(
            "Phân tích và thiết kế",
            [
                "1. Tổng quan hệ thống: Mô tả hệ thống và hạ tầng (lấy từ srs).",
                "2. Giả định thiết kế: Các giả định và ràng buộc.",
                "3. Tác động kinh doanh: Ảnh hưởng đến quy trình kinh doanh.",
                "4. Kiến trúc hiện tại và đề xuất: So sánh kiến trúc hiện tại và tương lai.",
                "5. Bảo mật và kiểm toán: Các biện pháp bảo mật.",
                "6. Thiết kế giao diện: Giao diện người dùng và tầng ứng dụng.",
                "7. Thông tin triển khai: Kế hoạch triển khai hệ thống.",
                "8. Cải tiến tương lai: Các đề xuất cải tiến.",
                shared_memory.load("srs") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/Analysis_and_Design_Document.docx"
        ) and shared_memory.save("analysis_design", output)
    )

    # Tác vụ tạo Application Development Project List
    app_dev_project_list_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Danh sách dự án phát triển ứng dụng (Application Development Project List) dựa trên dữ liệu từ `project_plan` và `wbs` trong SharedMemory. "
            "Tài liệu này liệt kê các dự án phát triển ứng dụng theo quy trình tuần tự từ khái niệm đến kiểm thử, bao gồm: mô tả hệ thống, kiến trúc phần mềm hiện tại và đề xuất, thiết kế giao diện, các lớp ứng dụng, tác động hạ tầng, an ninh, tích hợp, triển khai, các cải tiến đề xuất, phê duyệt. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `Application_Development_Project_List.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `app_dev_project_list`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `Application_Development_Project_List.docx` chứa danh sách dự án phát triển ứng dụng, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `app_dev_project_list`."
        ),
        callback=lambda output: create_docx(
            "Danh sách dự án phát triển ứng dụng",
            [
                "1. Mô tả hệ thống: Tổng quan các ứng dụng (lấy từ project_plan).",
                "2. Kiến trúc phần mềm: Hiện tại và đề xuất (lấy từ wbs).",
                "3. Thiết kế giao diện: Giao diện người dùng.",
                "4. Các lớp ứng dụng: Các thành phần ứng dụng.",
                "5. Tác động hạ tầng: Ảnh hưởng đến cơ sở hạ tầng.",
                "6. An ninh: Các biện pháp bảo mật.",
                "7. Tích hợp: Tích hợp với các hệ thống khác.",
                "8. Triển khai: Kế hoạch triển khai.",
                "9. Cải tiến đề xuất: Các cải tiến trong tương lai.",
                shared_memory.load("project_plan") or "Không có dữ liệu",
                shared_memory.load("wbs") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/Application_Development_Project_List.docx"
        ) and shared_memory.save("app_dev_project_list", output)
    )

    # Tác vụ tạo Technical Requirements Document
    technical_requirements_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Yêu cầu kỹ thuật (Technical Requirements Document) dựa trên dữ liệu từ `srs` trong SharedMemory. "
            "Tài liệu này cung cấp các yêu cầu kỹ thuật cụ thể để hỗ trợ phát triển và kiểm thử hệ thống chính xác. "
            "Nội dung bao gồm: mục đích, phạm vi, tài liệu tham chiếu, giả định, yêu cầu kỹ thuật cụ thể (hệ thống, mạng, cơ sở dữ liệu, giao diện người dùng, giao diện hệ thống, bảo mật). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `Technical_Requirements_Document.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `technical_requirements`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `Technical_Requirements_Document.docx` chứa yêu cầu kỹ thuật, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `technical_requirements`."
        ),
        callback=lambda output: create_docx(
            "Yêu cầu kỹ thuật",
            [
                "1. Mục đích: Mục tiêu của tài liệu yêu cầu kỹ thuật (lấy từ srs).",
                "2. Phạm vi: Phạm vi áp dụng của các yêu cầu kỹ thuật.",
                "3. Giả định: Các giả định và ràng buộc kỹ thuật.",
                "4. Yêu cầu hệ thống: Yêu cầu về hệ thống và mạng.",
                "5. Cơ sở dữ liệu: Yêu cầu về cơ sở dữ liệu.",
                "6. Giao diện: Giao diện người dùng và hệ thống.",
                "7. Bảo mật: Các yêu cầu bảo mật kỹ thuật.",
                shared_memory.load("srs") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/Technical_Requirements_Document.docx"
        ) and shared_memory.save("technical_requirements", output)
    )

    # Tác vụ tạo Database Design Document
    database_design_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Thiết kế cơ sở dữ liệu (Database Design Document) dựa trên dữ liệu từ `srs` và `software_architecture_plan` trong SharedMemory. "
            "Tài liệu này mô tả thiết kế cơ sở dữ liệu từ mô hình logic đến mô hình vật lý, đảm bảo hiệu năng và khả năng mở rộng. "
            "Nội dung bao gồm: mục tiêu, đối tượng sử dụng, nhân sự và chủ sở hữu dữ liệu, giả định, ràng buộc, tổng quan hệ thống, kiến trúc phần cứng/phần mềm, quyết định thiết kế tổng thể, chức năng quản trị CSDL, thiết kế chi tiết (mapping dữ liệu, backup, phục hồi), yêu cầu báo cáo. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `Database_Design_Document.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `database_design`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `Database_Design_Document.docx` chứa thiết kế cơ sở dữ liệu, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `database_design`."
        ),
        callback=lambda output: create_docx(
            "Thiết kế cơ sở dữ liệu",
            [
                "1. Mục tiêu: Mục đích của thiết kế cơ sở dữ liệu (lấy từ srs).",
                "2. Đối tượng sử dụng: Người dùng và chủ sở hữu dữ liệu.",
                "3. Giả định và ràng buộc: Các giả định và hạn chế.",
                "4. Tổng quan hệ thống: Mô tả hệ thống và kiến trúc (lấy từ software_architecture_plan).",
                "5. Chức năng quản trị: Quản trị cơ sở dữ liệu.",
                "6. Thiết kế chi tiết: Mapping dữ liệu, backup, phục hồi.",
                "7. Yêu cầu báo cáo: Các yêu cầu về báo cáo dữ liệu.",
                shared_memory.load("srs") or "Không có dữ liệu",
                shared_memory.load("software_architecture_plan") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/Database_Design_Document.docx"
        ) and shared_memory.save("database_design", output)
    )

    # Tác vụ tạo Website Planning Checklist
    website_planning_checklist_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Danh sách kiểm tra lập kế hoạch website (Website Planning Checklist) dựa trên dữ liệu từ `functional_requirements` và `non_functional_requirements` trong SharedMemory. "
            "Tài liệu này cung cấp danh sách kiểm tra khi lập kế hoạch xây dựng website mới, bao gồm: phân tích đối tượng, phân tích đối thủ, chiến lược nội dung, quảng bá và bảo trì, cấu trúc trang, dẫn hướng, thiết kế hình ảnh và bố cục, thiết kế giao diện người dùng, kỹ thuật kiểm thử. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `Website_Planning_Checklist.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `website_planning_checklist`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `Website_Planning_Checklist.docx` chứa danh sách kiểm tra lập kế hoạch website, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `website_planning_checklist`."
        ),
        callback=lambda output: create_docx(
            "Danh sách kiểm tra lập kế hoạch website",
            [
                "1. Phân tích đối tượng: Đối tượng người dùng website (lấy từ functional_requirements).",
                "2. Phân tích đối thủ: Phân tích các website đối thủ.",
                "3. Chiến lược nội dung: Kế hoạch nội dung website.",
                "4. Quảng bá và bảo trì: Chiến lược quảng bá và bảo trì.",
                "5. Cấu trúc trang: Cấu trúc và dẫn hướng website.",
                "6. Thiết kế giao diện: Hình ảnh, bố cục, và giao diện người dùng (lấy từ non_functional_requirements).",
                "7. Kỹ thuật kiểm thử: Các phương pháp kiểm thử website.",
                shared_memory.load("functional_requirements") or "Không có dữ liệu",
                shared_memory.load("non_functional_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/Website_Planning_Checklist.docx"
        ) and shared_memory.save("website_planning_checklist", output)
    )

    # Tác vụ tạo User Interface Design Template
    ui_design_template_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Mẫu thiết kế giao diện người dùng (User Interface Design Template) dựa trên dữ liệu từ `functional_requirements` trong SharedMemory. "
            "Tài liệu này định nghĩa tất cả thông số liên quan đến màn hình, hành động, hiển thị, bao gồm: tên sản phẩm/hệ thống, lý do thiết kế lại, chi tiết màn hình (tên, chức năng, tab, điều hướng), các thành phần (trường dữ liệu, kiểu dữ liệu, độ dài, tính toán, dropdown, font chữ, màu, kích thước, nút hành động, popup, định dạng, sự kiện), ràng buộc, rủi ro, các bên liên quan. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `User_Interface_Design_Template.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `ui_design_template`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `User_Interface_Design_Template.docx` chứa mẫu thiết kế giao diện người dùng, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `ui_design_template`."
        ),
        callback=lambda output: create_docx(
            "Mẫu thiết kế giao diện người dùng",
            [
                "1. Tên sản phẩm: Tên hệ thống hoặc sản phẩm (lấy từ functional_requirements).",
                "2. Lý do thiết kế: Mục đích thiết kế giao diện.",
                "3. Chi tiết màn hình: Tên, chức năng, tab, và điều hướng.",
                "4. Thành phần giao diện: Trường dữ liệu, dropdown, nút hành động, popup.",
                "5. Định dạng: Font chữ, màu, kích thước.",
                "6. Ràng buộc và rủi ro: Các hạn chế và rủi ro thiết kế.",
                "7. Các bên liên quan: Những người liên quan đến thiết kế.",
                shared_memory.load("functional_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/User_Interface_Design_Template.docx"
        ) and shared_memory.save("ui_design_template", output)
    )

    # Tác vụ tạo Report Design Template
    report_design_template_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Mẫu thiết kế báo cáo (Report Design Template) dựa trên dữ liệu từ `functional_requirements` trong SharedMemory. "
            "Tài liệu này thiết kế báo cáo chi tiết, bao gồm: tên hệ thống, mục đích báo cáo, tần suất, quyền truy cập, giả định, ràng buộc, rủi ro, các bên liên quan, các thành phần (tham số đầu vào, tính toán, công thức, trường báo cáo, nguồn dữ liệu, nhóm dữ liệu, tiêu đề/trang, mẫu báo cáo). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `Report_Design_Template.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `report_design_template`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `Report_Design_Template.docx` chứa mẫu thiết kế báo cáo, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `report_design_template`."
        ),
        callback=lambda output: create_docx(
            "Mẫu thiết kế báo cáo",
            [
                "1. Tên hệ thống: Tên hệ thống hoặc sản phẩm (lấy từ functional_requirements).",
                "2. Mục đích báo cáo: Mục tiêu và tần suất báo cáo.",
                "3. Quyền truy cập: Đối tượng sử dụng báo cáo.",
                "4. Giả định và ràng buộc: Các giả định và hạn chế.",
                "5. Thành phần báo cáo: Tham số đầu vào, tính toán, trường báo cáo.",
                "6. Nguồn dữ liệu: Nguồn dữ liệu và nhóm dữ liệu.",
                "7. Mẫu báo cáo: Tiêu đề, trang, và định dạng báo cáo.",
                shared_memory.load("functional_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/Report_Design_Template.docx"
        ) and shared_memory.save("report_design_template", output)
    )

    # Tác vụ tạo Code Review Checklist
    code_review_checklist_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Danh sách kiểm tra đánh giá mã nguồn (Code Review Checklist) dựa trên dữ liệu từ `technical_requirements` trong SharedMemory. "
            "Tài liệu này đảm bảo chất lượng và chuẩn lập trình, bao gồm: cấu trúc, tài liệu, biến, kiểu dữ liệu, phong cách lập trình, cấu trúc điều khiển, vòng lặp, bảo trì, bảo mật, tính khả dụng, kiểm tra lỗi, xử lý ngoại lệ, rò rỉ tài nguyên, thời gian, thử nghiệm, xác thực. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `Code_Review_Checklist.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `code_review_checklist`."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Tài liệu `Code_Review_Checklist.docx` chứa danh sách kiểm tra đánh giá mã nguồn, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `code_review_checklist`."
        ),
        callback=lambda output: create_docx(
            "Danh sách kiểm tra đánh giá mã nguồn",
            [
                "1. Cấu trúc: Cấu trúc mã nguồn và tài liệu (lấy từ technical_requirements).",
                "2. Biến và kiểu dữ liệu: Kiểm tra biến và kiểu dữ liệu.",
                "3. Phong cách lập trình: Tuân thủ chuẩn lập trình.",
                "4. Điều khiển và vòng lặp: Cấu trúc điều khiển và vòng lặp.",
                "5. Bảo mật và bảo trì: Các biện pháp bảo mật và khả năng bảo trì.",
                "6. Xử lý lỗi: Kiểm tra lỗi và xử lý ngoại lệ.",
                "7. Thử nghiệm: Xác thực và kiểm thử mã nguồn.",
                shared_memory.load("technical_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/Code_Review_Checklist.docx"
        ) and shared_memory.save("code_review_checklist", output)
    )

    # Tác vụ tạo Conversion Plan
    conversion_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Kế hoạch chuyển đổi (Conversion Plan) dựa trên dữ liệu từ `srs` trong SharedMemory. "
            "Tài liệu này mô tả kế hoạch chuyển đổi hệ thống hoặc dữ liệu, bao gồm: mục đích, tài liệu tham khảo, mô tả hệ thống và chiến lược chuyển đổi, các loại chuyển đổi, yếu tố rủi ro, lịch trình chuyển đổi, hỗ trợ chuyển đổi (phần cứng, phần mềm, nhân lực), đảm bảo an ninh và chất lượng dữ liệu. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `Conversion_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `conversion_plan`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `Conversion_Plan.docx` chứa kế hoạch chuyển đổi, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `conversion_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch chuyển đổi",
            [
                "1. Mục đích: Mục tiêu của kế hoạch chuyển đổi (lấy từ srs).",
                "2. Mô tả hệ thống: Hệ thống hiện tại và chiến lược chuyển đổi.",
                "3. Các loại chuyển đổi: Dữ liệu, ứng dụng, hoặc hệ thống.",
                "4. Yếu tố rủi ro: Các rủi ro liên quan đến chuyển đổi.",
                "5. Lịch trình chuyển đổi: Thời gian và các bước thực hiện.",
                "6. Hỗ trợ chuyển đổi: Phần cứng, phần mềm, và nhân lực.",
                "7. An ninh và chất lượng: Đảm bảo an ninh và chất lượng dữ liệu.",
                shared_memory.load("srs") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/Conversion_Plan.docx"
        ) and shared_memory.save("conversion_plan", output)
    )

    # Tác vụ tạo System Architecture
    system_architecture_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Kiến trúc hệ thống (System Architecture) dựa trên dữ liệu từ `software_architecture_plan` và `non_functional_requirements` trong SharedMemory. "
            "Tài liệu này mô tả kiến trúc tổng thể của hệ thống, bao gồm các thành phần, mối quan hệ, và yêu cầu phi chức năng. "
            "Nội dung bao gồm: tổng quan kiến trúc, các thành phần hệ thống, mối quan hệ giữa các thành phần, yêu cầu hiệu suất, bảo mật, khả năng mở rộng. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `System_Architecture.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `system_architecture`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `System_Architecture.docx` chứa kiến trúc hệ thống, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `system_architecture`."
        ),
        callback=lambda output: create_docx(
            "Kiến trúc hệ thống",
            [
                "1. Tổng quan kiến trúc: Mô tả tổng thể kiến trúc (lấy từ software_architecture_plan).",
                "2. Thành phần hệ thống: Các thành phần chính của hệ thống.",
                "3. Mối quan hệ: Tương tác giữa các thành phần.",
                "4. Yêu cầu phi chức năng: Hiệu suất, bảo mật, khả năng mở rộng (lấy từ non_functional_requirements).",
                shared_memory.load("software_architecture_plan") or "Không có dữ liệu",
                shared_memory.load("non_functional_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/System_Architecture.docx"
        ) and shared_memory.save("system_architecture", output)
    )

    # Tác vụ tạo Data Flow Diagrams (DFD)
    dfd_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Sơ đồ luồng dữ liệu (Data Flow Diagrams - DFD) dựa trên dữ liệu từ `srs` trong SharedMemory. "
            "Tài liệu này mô tả luồng dữ liệu trong hệ thống, bao gồm các quá trình, lưu trữ dữ liệu, và luồng dữ liệu giữa các thành phần. "
            "Nội dung bao gồm: sơ đồ DFD cấp 0, các sơ đồ DFD cấp thấp hơn, mô tả các quá trình, lưu trữ dữ liệu, và luồng dữ liệu. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `Data_Flow_Diagrams.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `dfd`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `Data_Flow_Diagrams.docx` chứa sơ đồ luồng dữ liệu, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `dfd`."
        ),
        callback=lambda output: create_docx(
            "Sơ đồ luồng dữ liệu",
            [
                "1. Sơ đồ DFD cấp 0: Tổng quan luồng dữ liệu (lấy từ srs).",
                "2. Sơ đồ DFD cấp thấp: Chi tiết các luồng dữ liệu.",
                "3. Mô tả quá trình: Các quá trình trong DFD.",
                "4. Lưu trữ dữ liệu: Các kho dữ liệu trong hệ thống.",
                "5. Luồng dữ liệu: Tương tác giữa các thành phần.",
                shared_memory.load("srs") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/Data_Flow_Diagrams.docx"
        ) and shared_memory.save("dfd", output)
    )

    # Tác vụ tạo Sequence Diagrams
    sequence_diagrams_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Sơ đồ tuần tự (Sequence Diagrams) dựa trên dữ liệu từ `functional_requirements` và `use_case_template` trong SharedMemory. "
            "Tài liệu này mô tả tương tác giữa các đối tượng trong hệ thống theo thời gian, dựa trên các kịch bản sử dụng. "
            "Nội dung bao gồm: sơ đồ tuần tự cho các kịch bản chính, mô tả các đối tượng, thông điệp, và trình tự tương tác. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `Sequence_Diagrams.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `sequence_diagrams`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `Sequence_Diagrams.docx` chứa sơ đồ tuần tự, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `sequence_diagrams`."
        ),
        callback=lambda output: create_docx(
            "Sơ đồ tuần tự",
            [
                "1. Sơ đồ tuần tự: Sơ đồ cho các kịch bản chính (lấy từ use_case_template).",
                "2. Đối tượng: Các đối tượng tham gia tương tác (lấy từ functional_requirements).",
                "3. Thông điệp: Các thông điệp giữa các đối tượng.",
                "4. Trình tự: Trình tự thời gian của các tương tác.",
                shared_memory.load("functional_requirements") or "Không có dữ liệu",
                shared_memory.load("use_case_template") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/Sequence_Diagrams.docx"
        ) and shared_memory.save("sequence_diagrams", output)
    )

    # Tác vụ tạo Security Architecture Document
    security_architecture_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Kiến trúc bảo mật (Security Architecture Document) dựa trên dữ liệu từ `privacy_security_requirements` và `system_architecture` trong SharedMemory. "
            "Tài liệu này mô tả các biện pháp bảo mật trong hệ thống, bao gồm: yêu cầu bảo mật, kiến trúc bảo mật, biện pháp kiểm soát truy cập, mã hóa dữ liệu, và tuân thủ quy định. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `Security_Architecture_Document.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `security_architecture`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `Security_Architecture_Document.docx` chứa kiến trúc bảo mật, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `security_architecture`."
        ),
        callback=lambda output: create_docx(
            "Kiến trúc bảo mật",
            [
                "1. Yêu cầu bảo mật: Các yêu cầu bảo mật hệ thống (lấy từ privacy_security_requirements).",
                "2. Kiến trúc bảo mật: Tổng quan kiến trúc bảo mật (lấy từ system_architecture).",
                "3. Kiểm soát truy cập: Các biện pháp kiểm soát truy cập.",
                "4. Mã hóa dữ liệu: Phương pháp mã hóa dữ liệu.",
                "5. Tuân thủ quy định: Các quy định pháp lý liên quan.",
                shared_memory.load("privacy_security_requirements") or "Không có dữ liệu",
                shared_memory.load("system_architecture") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/Security_Architecture_Document.docx"
        ) and shared_memory.save("security_architecture", output)
    )

    # Tác vụ tạo High-Level Design (HLD)
    hld_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Thiết kế cấp cao (High-Level Design - HLD) dựa trên dữ liệu từ `srs` và `software_architecture_plan` trong SharedMemory. "
            "Tài liệu này cung cấp thiết kế tổng thể của hệ thống, bao gồm: tổng quan hệ thống, các thành phần chính, mối quan hệ giữa các thành phần, kiến trúc phần mềm và phần cứng. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `High_Level_Design.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `hld`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `High_Level_Design.docx` chứa thiết kế cấp cao, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `hld`."
        ),
        callback=lambda output: create_docx(
            "Thiết kế cấp cao",
            [
                "1. Tổng quan hệ thống: Mô tả tổng thể hệ thống (lấy từ srs).",
                "2. Thành phần chính: Các thành phần hệ thống (lấy từ software_architecture_plan).",
                "3. Mối quan hệ: Tương tác giữa các thành phần.",
                "4. Kiến trúc: Kiến trúc phần mềm và phần cứng.",
                shared_memory.load("srs") or "Không có dữ liệu",
                shared_memory.load("software_architecture_plan") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/High_Level_Design.docx"
        ) and shared_memory.save("hld", output)
    )

    # Tác vụ tạo Low-Level Design (LLD)
    lld_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Thiết kế cấp thấp (Low-Level Design - LLD) dựa trên dữ liệu từ `hld` và `technical_requirements` trong SharedMemory. "
            "Tài liệu này cung cấp thiết kế chi tiết cho từng thành phần hệ thống, bao gồm: mô tả chi tiết các module, giao diện, thuật toán, cấu trúc dữ liệu. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `Low_Level_Design.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `lld`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `Low_Level_Design.docx` chứa thiết kế cấp thấp, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `lld`."
        ),
        callback=lambda output: create_docx(
            "Thiết kế cấp thấp",
            [
                "1. Mô tả module: Chi tiết từng module hệ thống (lấy từ hld).",
                "2. Giao diện: Giao diện của các module.",
                "3. Thuật toán: Các thuật toán được sử dụng (lấy từ technical_requirements).",
                "4. Cấu trúc dữ liệu: Cấu trúc dữ liệu chi tiết.",
                shared_memory.load("hld") or "Không có dữ liệu",
                shared_memory.load("technical_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/Low_Level_Design.docx"
        ) and shared_memory.save("lld", output)
    )

    # Tác vụ tạo API Design Document
    api_design_task = Task(
        description=(
            "Sử dụng công cụ `create_design_document` để tạo tài liệu Thiết kế API (API Design Document) dựa trên dữ liệu từ `functional_requirements` và `technical_requirements` trong SharedMemory. "
            "Tài liệu này mô tả thiết kế các API của hệ thống, bao gồm: mô tả API, endpoint, phương thức, tham số, phản hồi, và bảo mật. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/3_design` với tên `API_Design_Document.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `api_design`."
        ),
        agent=design_agent,
        expected_output=(
            "Tài liệu `API_Design_Document.docx` chứa thiết kế API, "
            "được lưu trong `output/3_design` và SharedMemory với khóa `api_design`."
        ),
        callback=lambda output: create_docx(
            "Thiết kế API",
            [
                "1. Mô tả API: Tổng quan về các API (lấy từ functional_requirements).",
                "2. Endpoint: Danh sách các endpoint API.",
                "3. Phương thức: Phương thức HTTP (GET, POST, PUT, DELETE).",
                "4. Tham số: Các tham số đầu vào của API.",
                "5. Phản hồi: Cấu trúc dữ liệu phản hồi.",
                "6. Bảo mật: Các biện pháp bảo mật API (lấy từ technical_requirements).",
                shared_memory.load("functional_requirements") or "Không có dữ liệu",
                shared_memory.load("technical_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/3_design/API_Design_Document.docx"
        ) and shared_memory.save("api_design", output)
    )

    tasks.extend([
        srs_task,
        analysis_design_task,
        app_dev_project_list_task,
        technical_requirements_task,
        database_design_task,
        website_planning_checklist_task,
        ui_design_template_task,
        report_design_template_task,
        code_review_checklist_task,
        conversion_plan_task,
        system_architecture_task,
        dfd_task,
        sequence_diagrams_task,
        security_architecture_task,
        hld_task,
        lld_task,
        api_design_task
    ])

    return tasks
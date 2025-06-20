from crewai import Task
from utils.output_formats import create_docx, create_xlsx
from memory.shared_memory import SharedMemory
import os

def create_testing_tasks(shared_memory: SharedMemory, output_base_dir: str, input_agent, researcher_agent, project_manager_agent, testing_agent):
    """
    Tạo các tác vụ cho giai đoạn Kiểm thử (Testing Phase).
    """
    tasks = []

    # Tác vụ tạo Documentation Quality Assurance Checklist
    doc_qa_checklist_task = Task(
        description=(
            "Sử dụng công cụ `create_test_plan_document` để tạo tài liệu Danh sách kiểm tra đảm bảo chất lượng tài liệu (Documentation Quality Assurance Checklist) dựa trên dữ liệu từ `dev_standards` trong SharedMemory. "
            "Tài liệu này kiểm tra chất lượng tài liệu trước khi triển khai, đảm bảo tài liệu đạt tiêu chuẩn. "
            "Nội dung phải bao gồm: thuộc tính tài liệu, track changes, trang bìa, mục lục, header/footer, chính tả và ngữ pháp, định dạng và bố cục, từ viết tắt, phụ lục, thông tin liên hệ, cross-reference, chú thích, hình ảnh, liên kết, chỉ mục, ngắt trang, sơ đồ quy trình, bảng biểu. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/5_testing` với tên `Documentation_QA_Checklist.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `doc_qa_checklist`."
        ),
        agent=project_manager_agent,
        expected_output=(
            "Tài liệu `Documentation_QA_Checklist.docx` chứa danh sách kiểm tra chất lượng tài liệu, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `doc_qa_checklist`."
        ),
        callback=lambda output: create_docx(
            "Danh sách kiểm tra đảm bảo chất lượng tài liệu",
            [
                "1. Thuộc tính tài liệu: Tên, phiên bản, ngày phát hành (lấy từ dev_standards).",
                "2. Track Changes: Kiểm tra trạng thái track changes.",
                "3. Trang bìa và mục lục: Kiểm tra trang bìa và mục lục.",
                "4. Header/Footer: Kiểm tra định dạng header/footer.",
                "5. Chính tả và ngữ pháp: Kiểm tra lỗi chính tả và ngữ pháp.",
                "6. Định dạng và bố cục: Kiểm tra định dạng và bố cục tài liệu.",
                "7. Từ viết tắt: Kiểm tra danh sách từ viết tắt.",
                "8. Phụ lục và thông tin liên hệ: Kiểm tra phụ lục và thông tin liên hệ.",
                "9. Cross-reference và chú thích: Kiểm tra liên kết chéo và chú thích.",
                "10. Hình ảnh và liên kết: Kiểm tra hình ảnh và liên kết.",
                "11. Chỉ mục và ngắt trang: Kiểm tra chỉ mục và ngắt trang.",
                "12. Sơ đồ quy trình và bảng biểu: Kiểm tra sơ đồ và bảng biểu.",
                shared_memory.load("dev_standards") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/5_testing/Documentation_QA_Checklist.docx"
        ) and shared_memory.save("doc_qa_checklist", output)
    )

    # Tác vụ tạo Building Test Scenarios
    test_scenarios_task = Task(
        description=(
            "Sử dụng công cụ `create_test_plan_document` để tạo tài liệu Xây dựng kịch bản kiểm thử (Building Test Scenarios) dựa trên dữ liệu từ `functional_requirements` và `use_case_template` trong SharedMemory. "
            "Tài liệu này xác định các kịch bản kiểm thử để kiểm tra hệ thống hoặc tình huống cụ thể. "
            "Nội dung phải bao gồm: phân biệt test case và scenario, cách xây dựng test scenario tốt, mã phiên bản, mã build, ID kịch bản, mô tả, mục tiêu, dữ liệu thử nghiệm, ngày sửa đổi, người kiểm thử, người duyệt, các bước kiểm thử. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/5_testing` với tên `Building_Test_Scenarios.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `test_scenarios`."
        ),
        agent=testing_agent,
        expected_output=(
            "Tài liệu `Building_Test_Scenarios.docx` chứa kịch bản kiểm thử, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `test_scenarios`."
        ),
        callback=lambda output: create_docx(
            "Xây dựng kịch bản kiểm thử",
            [
                "1. Phân biệt test case và scenario: Sự khác biệt giữa test case và scenario.",
                "2. Cách xây dựng test scenario: Hướng dẫn xây dựng kịch bản kiểm thử tốt.",
                "3. Mã phiên bản và mã build: Thông tin phiên bản và build (lấy từ functional_requirements).",
                "4. ID kịch bản, mô tả, mục tiêu: Chi tiết kịch bản kiểm thử (lấy từ use_case_template).",
                "5. Dữ liệu thử nghiệm: Dữ liệu dùng để kiểm thử.",
                "6. Ngày sửa đổi, người kiểm thử, người duyệt: Thông tin quản lý kịch bản.",
                "7. Các bước kiểm thử: Các bước thực hiện kiểm thử.",
                shared_memory.load("functional_requirements") or "Không có dữ liệu",
                shared_memory.load("use_case_template") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/5_testing/Building_Test_Scenarios.docx"
        ) and shared_memory.save("test_scenarios", output)
    )

    # Tác vụ tạo Test Plan
    test_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_test_plan_document` để tạo tài liệu Kế hoạch kiểm thử (Test Plan) dựa trên dữ liệu từ `rtm`, `project_plan`, và `non_functional_requirements` trong SharedMemory. "
            "Tài liệu này mô tả chiến lược, phạm vi, quy trình, và tiêu chí đánh giá kiểm thử phần mềm. "
            "Nội dung phải bao gồm: mô tả phương pháp kiểm thử, phân loại kiểm thử (đơn vị, tích hợp, UAT,...), các ràng buộc, giả định, quy trình thông báo, leo thang vấn đề, các thước đo chất lượng, tiêu chí tạm dừng và khôi phục kiểm thử, phê duyệt. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/5_testing` với tên `Test_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `test_plan`."
        ),
        agent=testing_agent,
        expected_output=(
            "Tài liệu `Test_Plan.docx` chứa kế hoạch kiểm thử, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `test_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch kiểm thử",
            [
                "1. Phương pháp kiểm thử: Mô tả phương pháp kiểm thử (lấy từ rtm).",
                "2. Phân loại kiểm thử: Đơn vị, tích hợp, UAT,... (lấy từ project_plan).",
                "3. Ràng buộc và giả định: Các ràng buộc và giả định kiểm thử.",
                "4. Quy trình thông báo: Quy trình báo cáo và leo thang vấn đề.",
                "5. Thước đo chất lượng: Tiêu chí đánh giá chất lượng (lấy từ non_functional_requirements`).",
                "6. Tiêu chí tạm dừng/khôi phục: Điều kiện dừng và tiếp tục kiểm thử.",
                "7. Phê duyệt: Quy trình phê duyệt kế hoạch kiểm thử.",
                shared_memory.load("rtm") or "Không có dữ liệu",
                shared_memory.load("project_plan") or "Không có dữ liệu",
                shared_memory.load("non_functional_requirements") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/5_testing/Test_Plan.docx"
        ) and shared_memory.save("test_plan", output)
    )

    # Tác vụ tạo System Quality Assurance Checklist
    system_qa_checklist_task = Task(
        description=(
            "Sử dụng công cụ `create_test_plan_document` để tạo tài liệu Danh sách kiểm tra đảm bảo chất lượng hệ thống (System Quality Assurance Checklist) dựa trên dữ liệu từ `test_plan` và `srs` trong SharedMemory. "
            "Tài liệu này kiểm tra chất lượng toàn hệ thống để đảm bảo đáp ứng yêu cầu. "
            "Nội dung phải bao gồm: quản lý dự án (nguồn lực, quy trình, giám sát), phương pháp phát triển phần mềm/phần cứng, rà soát kỹ thuật, thông tin yêu cầu, thiết kế, mã nguồn, lịch sử bảo trì, hiệu năng, sản phẩm/phần cứng/phần mềm mua ngoài, bảo mật, tương thích, sạch virus. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/5_testing` với tên `System_QA_Checklist.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `system_qa_checklist`."
        ),
        agent=testing_agent,
        expected_output=(
            "Tài liệu `System_QA_Checklist.docx` chứa danh sách kiểm tra chất lượng hệ thống, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `system_qa_checklist`."
        ),
        callback=lambda output: create_docx(
            "Danh sách kiểm tra đảm bảo chất lượng hệ thống",
            [
                "1. Quản lý dự án: Kiểm tra nguồn lực và quy trình (lấy từ test_plan`).",
                "2. Phương pháp phát triển: Kiểm tra phương pháp phát triển phần mềm/phần cứng.",
                "3. Rà soát kỹ thuật: Kiểm tra tài liệu yêu cầu và thiết kế (lấy từ srs`).",
                "4. Mã nguồn: Kiểm tra chất lượng mã nguồn.",
                "5. Lịch sử bảo trì: Kiểm tra lịch sử bảo trì và hiệu năng.",
                "6. Sản phẩm mua ngoài: Kiểm tra phần cứng/phần mềm mua ngoài.",
                "7. Bảo mật và tương thích: Kiểm tra bảo mật và tương thích hệ thống.",
                shared_memory.load("test_plan") or "Không có dữ liệu",
                shared_memory.load("srs") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/5_testing/System_QA_Checklist.docx"
        ) and shared_memory.save("system_qa_checklist", output)
    )

    # Tác vụ tạo System Test Plan
    system_test_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_test_plan_document` để tạo tài liệu Kế hoạch kiểm thử hệ thống (System Test Plan) dựa trên dữ liệu từ `test_plan` và `srs` trong SharedMemory. "
            "Tài liệu này mô tả kế hoạch kiểm thử toàn bộ hệ thống theo yêu cầu tài liệu. "
            "Nội dung phải bao gồm: mục tiêu và tiêu chí vào/ra kiểm thử, phạm vi và loại kiểm thử, phân tích rủi ro, môi trường kiểm thử (phần cứng/phần mềm), lịch kiểm thử, ma trận kiểm thử (điều kiện, rủi ro, hướng dẫn). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/5_testing` với tên `System_Test_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `system_test_plan`."
        ),
        agent=testing_agent,
        expected_output=(
            "Tài liệu `System_Test_Plan.docx` chứa kế hoạch kiểm thử hệ thống, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `system_test_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch kiểm thử hệ thống",
            [
                "1. Mục tiêu: Mục tiêu kiểm thử hệ thống (lấy từ test_plan`).",
                "2. Tiêu chí vào/ra: Tiêu chí bắt đầu và kết thúc kiểm thử.",
                "3. Phạm vi và loại kiểm thử: Các loại kiểm thử hệ thống (lấy từ srs`).",
                "4. Phân tích rủi ro: Các rủi ro liên quan đến kiểm thử.",
                "5. Môi trường kiểm thử: Phần cứng và phần mềm kiểm thử.",
                "6. Lịch kiểm thử: Lịch trình kiểm thử hệ thống.",
                "7. Ma trận kiểm thử: Điều kiện, rủi ro, và hướng dẫn kiểm thử.",
                shared_memory.load("test_plan") or "Không có dữ liệu",
                shared_memory.load("srs") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/5_testing/System_Test_Plan.docx"
        ) and shared_memory.save("system_test_plan", output)
    )

    # Tác vụ tạo User Acceptance Test Plan (UAT)
    uat_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_test_plan_document` để tạo tài liệu Kế hoạch kiểm thử chấp nhận người dùng (User Acceptance Test Plan - UAT) dựa trên dữ liệu từ `functional_requirements` và `brd` trong SharedMemory. "
            "Tài liệu này mô tả kế hoạch kiểm thử để đảm bảo hệ thống đáp ứng yêu cầu người dùng. "
            "Nội dung phải bao gồm: mục đích, tài liệu tham chiếu, mô tả kiểm thử, tiêu chí vào/ra, phạm vi, hạng mục kiểm thử, rủi ro, giả định, ràng buộc, môi trường kiểm thử, kiểm thử chức năng, lịch kiểm thử, vai trò và trách nhiệm. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/5_testing` với tên `User_Acceptance_Test_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `uat_plan`."
        ),
        agent=testing_agent,
        expected_output=(
            "Tài liệu `User_Acceptance_Test_Plan.docx` chứa kế hoạch kiểm thử chấp nhận người dùng, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `uat_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch kiểm thử chấp nhận người dùng",
            [
                "1. Mục đích: Mục tiêu của UAT (lấy từ brd).",
                "2. Tài liệu tham chiếu: Các tài liệu liên quan.",
                "3. Mô tả kiểm thử: Mô tả quy trình kiểm thử (lấy từ functional_requirements).",
                "4. Tiêu chí vào/ra: Tiêu chí bắt đầu và kết thúc UAT.",
                "5. Phạm vi và hạng mục: Các hạng mục kiểm thử.",
                "6. Rủi ro, giả định, ràng buộc: Các yếu tố ảnh hưởng UAT.",
                "7. Môi trường kiểm thử: Môi trường thực hiện UAT.",
                "8. Lịch kiểm thử: Lịch trình và vai trò trách nhiệm.",
                shared_memory.load("functional_requirements") or "Không có dữ liệu",
                shared_memory.load("brd") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/5_testing/User_Acceptance_Test_Plan.docx"
        ) and shared_memory.save("uat_plan", output)
    )

    # Tác vụ tạo Test Case Specification
    test_case_spec_task = Task(
        description=(
            "Sử dụng công cụ `create_test_plan_document` để tạo tài liệu Đặc tả trường hợp kiểm thử (Test Case Specification) dựa trên dữ liệu từ `test_scenarios` và `rtm` trong SharedMemory. "
            "Tài liệu này chi tiết hóa các trường hợp kiểm thử dựa trên kịch bản kiểm thử. "
            "Nội dung phải bao gồm: ID test case, mô tả, mục tiêu, điều kiện tiên quyết, dữ liệu kiểm thử, các bước thực hiện, kết quả mong đợi, trạng thái pass/fail. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/5_testing` với tên `Test_Case_Specification.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `test_case_spec`."
        ),
        agent=testing_agent,
        expected_output=(
            "Tài liệu `Test_Case_Specification.docx` chứa đặc tả trường hợp kiểm thử, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `test_case_spec`."
        ),
        callback=lambda output: create_docx(
            "Đặc tả trường hợp kiểm thử",
            [
                "1. ID test case: Mã định danh test case (lấy từ test_scenarios).",
                "2. Mô tả và mục tiêu: Mô tả và mục tiêu của test case.",
                "3. Điều kiện tiên quyết: Các điều kiện cần thiết để thực hiện (lấy từ rtm).",
                "4. Dữ liệu kiểm thử: Dữ liệu dùng để kiểm thử.",
                "5. Các bước thực hiện: Các bước thực hiện test case.",
                "6. Kết quả mong đợi: Kết quả dự kiến của test case.",
                "7. Trạng thái: Pass/fail của test case.",
                shared_memory.load("test_scenarios") or "Không có dữ liệu",
                shared_memory.load("rtm") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/5_testing/Test_Case_Specification.docx"
        ) and shared_memory.save("test_case_spec", output)
    )

    # Tác vụ tạo Testing Bug Report
    bug_report_task = Task(
        description=(
            "Sử dụng công cụ `create_test_plan_document` để tạo tài liệu Báo cáo lỗi kiểm thử (Testing Bug Report) dựa trên dữ liệu từ `test_case_spec` và `system_test_plan` trong SharedMemory. "
            "Tài liệu này ghi nhận chi tiết các lỗi phát hiện trong quá trình kiểm thử. "
            "Nội dung phải bao gồm: mô tả lỗi, vị trí xuất hiện, mức độ nghiêm trọng, trạng thái, mức ưu tiên, môi trường thử nghiệm, phương pháp và người phụ trách. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/5_testing` với tên `Testing_Bug_Report.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `bug_report`."
        ),
        agent=testing_agent,
        expected_output=(
            "Tài liệu `Testing_Bug_Report.docx` chứa báo cáo lỗi kiểm thử, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `bug_report`."
        ),
        callback=lambda output: create_docx(
            "Báo cáo lỗi kiểm thử",
            [
                "1. Mô tả lỗi: Chi tiết về lỗi phát hiện (lấy từ test_case_spec).",
                "2. Vị trí xuất hiện: Vị trí lỗi trong hệ thống (lấy từ system_test_plan).",
                "3. Mức độ nghiêm trọng: Mức độ ảnh hưởng của lỗi.",
                "4. Trạng thái: Trạng thái hiện tại của lỗi (mới, đang xử lý, đã sửa).",
                "5. Mức ưu tiên: Ưu tiên xử lý lỗi.",
                "6. Môi trường thử nghiệm: Môi trường phát hiện lỗi.",
                "7. Phương pháp và người phụ trách: Phương pháp kiểm thử và người xử lý.",
                shared_memory.load("test_case_spec") or "Không có dữ liệu",
                shared_memory.load("system_test_plan") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/5_testing/Testing_Bug_Report.docx"
        ) and shared_memory.save("bug_report", output)
    )

    # Tác vụ tạo Testing Bug List
    bug_list_task = Task(
        description=(
            "Sử dụng công cụ `create_xlsx` để tạo tài liệu Danh sách lỗi kiểm thử (Testing Bug List) dựa trên dữ liệu từ `bug_report` trong SharedMemory. "
            "Tài liệu này liệt kê tất cả các lỗi phát hiện trong quá trình kiểm thử. "
            "Nội dung phải bao gồm: ngày phát hiện, ID lỗi, ID test case, tên và mô tả lỗi, mức độ nghiêm trọng, trạng thái, người kiểm thử, phương pháp thử nghiệm. "
            "Lưu tài liệu dưới dạng `.xlsx` trong thư mục `output/5_testing` với tên `Testing_Bug_List.xlsx`. "
            "Lưu kết quả vào SharedMemory với khóa `bug_list`."
        ),
        agent=testing_agent,
        expected_output=(
            "Tài liệu `Testing_Bug_List.xlsx` chứa danh sách lỗi kiểm thử, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `bug_list`."
        ),
        callback=lambda output: create_xlsx(
            [
                ["Ngày phát hiện", "ID lỗi", "ID test case", "Tên lỗi", "Mô tả lỗi", "Mức độ nghiêm trọng", "Trạng thái", "Người kiểm thử", "Phương pháp thử nghiệm"],
                ["2025-06-20", "BUG-001", "TC-001", "Lỗi giao diện", "Nút submit không hoạt động", "Cao", "Mới", "Tester1", "Kiểm thử thủ công"],
                ["2025-06-20", "BUG-002", "TC-002", "Lỗi API", "API trả về lỗi 500", "Trung bình", "Đang xử lý", "Tester2", "Kiểm thử tự động"]
            ],
            f"{output_base_dir}/5_testing/Testing_Bug_List.xlsx"
        ) and shared_memory.save("bug_list", output)
    )

    # Tác vụ tạo Regression Testing Plan
    regression_test_plan_task = Task(
        description=(
            "Sử dụng công cụ `create_test_plan_document` để tạo tài liệu Kế hoạch kiểm thử hồi quy (Regression Testing Plan) dựa trên dữ liệu từ `bug_report` và `rtm` trong SharedMemory. "
            "Tài liệu này mô tả kế hoạch kiểm thử hồi quy sau khi vá lỗi hoặc cập nhật hệ thống. "
            "Nội dung phải bao gồm: định nghĩa và phạm vi kiểm thử hồi quy, phương pháp kiểm thử, loại kiểm thử, rủi ro, giả định, ràng buộc, lịch trình (công việc, số ngày, ngày bắt đầu/kết thúc), hướng dẫn (bước kiểm thử, kết quả mong đợi, pass/fail). "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/5_testing` với tên `Regression_Testing_Plan.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `regression_test_plan`."
        ),
        agent=testing_agent,
        expected_output=(
            "Tài liệu `Regression_Testing_Plan.docx` chứa kế hoạch kiểm thử hồi quy, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `regression_test_plan`."
        ),
        callback=lambda output: create_docx(
            "Kế hoạch kiểm thử hồi quy",
            [
                "1. Định nghĩa: Mục đích của kiểm thử hồi quy (lấy từ bug_report).",
                "2. Phạm vi: Phạm vi kiểm thử hồi quy (lấy từ rtm).",
                "3. Phương pháp kiểm thử: Phương pháp thực hiện kiểm thử.",
                "4. Loại kiểm thử: Các loại kiểm thử hồi quy.",
                "5. Rủi ro, giả định, ràng buộc: Các yếu tố ảnh hưởng kiểm thử.",
                "6. Lịch trình: Công việc, ngày bắt đầu/kết thúc.",
                "7. Hướng dẫn: Bước kiểm thử, kết quả mong đợi, pass/fail.",
                shared_memory.load("bug_report") or "Không có dữ liệu",
                shared_memory.load("rtm") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/5_testing/Regression_Testing_Plan.docx"
        ) and shared_memory.save("regression_test_plan", output)
    )

    # Tác vụ tạo Project Acceptance Document
    project_acceptance_task = Task(
        description=(
            "Sử dụng công cụ `create_test_plan_document` để tạo tài liệu Văn bản nghiệm thu dự án (Project Acceptance Document) dựa trên dữ liệu từ `test_summary_report` và `uat_plan` trong SharedMemory. "
            "Tài liệu này xác nhận dự án đã được nghiệm thu sau khi triển khai chính thức. "
            "Nội dung phải bao gồm: tên và mã dự án, bộ phận sử dụng, người bảo trợ, quản lý dự án, mô tả dự án, tuyên bố chấp thuận, chữ ký xác nhận. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/5_testing` với tên `Project_Acceptance_Document.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `project_acceptance`."
        ),
        agent=testing_agent,
        expected_output=(
            "Tài liệu `Project_Acceptance_Document.docx` chứa văn bản nghiệm thu dự án, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `project_acceptance`."
        ),
        callback=lambda output: create_docx(
            "Văn bản nghiệm thu dự án",
            [
                "1. Tên và mã dự án: Thông tin dự án (lấy từ test_summary_report).",
                "2. Bộ phận sử dụng: Đơn vị sử dụng hệ thống.",
                "3. Người bảo trợ và quản lý: Thông tin người bảo trợ và quản lý (lấy từ uat_plan).",
                "4. Mô tả dự án: Tóm tắt dự án.",
                "5. Tuyên bố chấp thuận: Xác nhận nghiệm thu.",
                "6. Chữ ký xác nhận: Chữ ký của các bên liên quan.",
                shared_memory.load("test_summary_report") or "Không có dữ liệu",
                shared_memory.load("uat_plan") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/5_testing/Project_Acceptance_Document.docx"
        ) and shared_memory.save("project_acceptance", output)
    )

    # Tác vụ tạo Test Summary Report
    test_summary_report_task = Task(
        description=(
            "Sử dụng công cụ `create_test_plan_document` để tạo tài liệu Báo cáo tóm tắt kiểm thử (Test Summary Report) dựa trên dữ liệu từ `bug_report` và `test_case_spec` trong SharedMemory. "
            "Tài liệu này tóm tắt kết quả kiểm thử, bao gồm các lỗi đã phát hiện và trạng thái kiểm thử. "
            "Nội dung phải bao gồm: tổng quan kiểm thử, kết quả kiểm thử, số lượng test case (pass/fail), danh sách lỗi chính, khuyến nghị cải tiến, trạng thái sẵn sàng triển khai. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/5_testing` với tên `Test_Summary_Report.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `test_summary_report`."
        ),
        agent=testing_agent,
        expected_output=(
            "Tài liệu `Test_Summary_Report.docx` chứa báo cáo tóm tắt kiểm thử, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `test_summary_report`."
        ),
        callback=lambda output: create_docx(
            "Báo cáo tóm tắt kiểm thử",
            [
                "1. Tổng quan kiểm thử: Tóm tắt quy trình kiểm thử (lấy từ test_case_spec).",
                "2. Kết quả kiểm thử: Tóm tắt kết quả kiểm thử.",
                "3. Số lượng test case: Số lượng pass/fail (lấy từ bug_report).",
                "4. Danh sách lỗi chính: Các lỗi nghiêm trọng phát hiện.",
                "5. Khuyến nghị cải tiến: Đề xuất cải tiến hệ thống.",
                "6. Trạng thái triển khai: Đánh giá sẵn sàng triển khai.",
                shared_memory.load("bug_report") or "Không có dữ liệu",
                shared_memory.load("test_case_spec") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/5_testing/Test_Summary_Report.docx"
        ) and shared_memory.save("test_summary_report", output)
    )

    # Tác vụ tạo Risk Management Register
    risk_management_register_task = Task(
        description=(
            "Sử dụng công cụ `create_xlsx` để tạo tài liệu Sổ đăng ký quản lý rủi ro (Risk Management Register) dựa trên dữ liệu từ `risk_analysis_plan` và `bug_report` trong SharedMemory. "
            "Tài liệu này liệt kê và quản lý các rủi ro trong quá trình kiểm thử và triển khai. "
            "Nội dung phải bao gồm: mô tả rủi ro, người chịu trách nhiệm, ngày báo cáo, ngày cập nhật, mức độ ảnh hưởng, xác suất xảy ra, thời gian tác động, trạng thái phản hồi, hành động đã/thực hiện/đang lên kế hoạch, tình trạng rủi ro hiện tại. "
            "Lưu tài liệu dưới dạng `.xlsx` trong thư mục `output/5_testing` với tên `Risk_Management_Register.xlsx`. "
            "Lưu kết quả vào SharedMemory với khóa `risk_management_register`."
        ),
        agent=testing_agent,
        expected_output=(
            "Tài liệu `Risk_Management_Register.xlsx` chứa sổ đăng ký quản lý rủi ro, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `risk_management_register`."
        ),
        callback=lambda output: create_xlsx(
            [
                ["Mô tả rủi ro", "Người chịu trách nhiệm", "Ngày báo cáo", "Ngày cập nhật", "Mức độ ảnh hưởng", "Xác suất", "Thời gian tác động", "Trạng thái phản hồi", "Hành động", "Tình trạng"],
                ["Lỗi hệ thống nghiêm trọng", "Tester1", "2025-06-20", "2025-06-20", "Cao", "80%", "Gần hạn", "Đã thực hiện", "Vá lỗi", "Đã đóng"],
                ["Hiệu năng thấp", "Tester2", "2025-06-20", "2025-06-20", "Trung bình", "50%", "Trung hạn", "Đang lên kế hoạch", "Tối ưu hóa", "Đang mở"]
            ],
            f"{output_base_dir}/5_testing/Risk_Management_Register.xlsx"
        ) and shared_memory.save("risk_management_register", output)
    )

    # Tác vụ tạo Project Status Report
    project_status_report_task = Task(
        description=(
            "Sử dụng công cụ `create_test_plan_document` để tạo tài liệu Báo cáo tình trạng dự án (Project Status Report) dựa trên dữ liệu từ `test_summary_report` và `dev_progress_report` trong SharedMemory. "
            "Tài liệu này tóm tắt hoạt động, vấn đề, kế hoạch, và tiến độ dự án để báo cáo cho khách hàng hoặc quản lý. "
            "Nội dung phải bao gồm: phân phối báo cáo, tổng quan dự án, quản trị hành chính, hoạt động đã thực hiện, vấn đề hoặc chậm trễ, vấn đề cần xử lý, hoạt động dự kiến kỳ tới, trạng thái deliverables, hoàn thành theo WBS, nhiệm vụ WBS (hoàn thành, quá hạn, sắp đến), thay đổi đang mở/đã duyệt/bị từ chối, vấn đề đang mở/đã đóng, rủi ro đang mở/đã xử lý. "
            "Lưu tài liệu dưới dạng `.docx` trong thư mục `output/5_testing` với tên `Project_Status_Report.docx`. "
            "Lưu kết quả vào SharedMemory với khóa `project_status_report`."
        ),
        agent=testing_agent,
        expected_output=(
            "Tài liệu `Project_Status_Report.docx` chứa báo cáo tình trạng dự án, "
            "được lưu trong `output/5_testing` và SharedMemory với khóa `project_status_report`."
        ),
        callback=lambda output: create_docx(
            "Báo cáo tình trạng dự án",
            [
                "1. Phân phối báo cáo: Đối tượng nhận báo cáo (lấy từ test_summary_report).",
                "2. Tổng quan dự án: Tóm tắt dự án.",
                "3. Quản trị hành chính: Quản lý hành chính dự án.",
                "4. Hoạt động đã thực hiện: Các hoạt động hoàn thành (lấy từ dev_progress_report).",
                "5. Vấn đề/chậm trễ: Các vấn đề và chậm trễ gặp phải.",
                "6. Vấn đề cần xử lý: Các vấn đề cần giải quyết.",
                "7. Hoạt động dự kiến: Kế hoạch cho kỳ tới.",
                "8. Trạng thái deliverables: Trạng thái các sản phẩm bàn giao.",
                "9. Nhiệm vụ WBS: Hoàn thành, quá hạn, sắp đến.",
                "10. Thay đổi: Thay đổi đang mở, đã duyệt, bị từ chối.",
                "11. Rủi ro: Rủi ro đang mở, đã xử lý.",
                shared_memory.load("test_summary_report") or "Không có dữ liệu",
                shared_memory.load("dev_progress_report") or "Không có dữ liệu"
            ],
            f"{output_base_dir}/5_testing/Project_Status_Report.docx"
        ) and shared_memory.save("project_status_report", output)
    )

    tasks.extend([
        doc_qa_checklist_task,
        test_scenarios_task,
        test_plan_task,
        system_qa_checklist_task,
        system_test_plan_task,
        uat_plan_task,
        test_case_spec_task,
        bug_report_task,
        bug_list_task,
        regression_test_plan_task,
        project_acceptance_task,
        test_summary_report_task,
        risk_management_register_task,
        project_status_report_task
    ])

    return tasks
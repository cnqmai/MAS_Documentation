```markdown
# Requirements_Research_Summary.md

## Tổng hợp kiến thức về Quản lý Yêu cầu Phần mềm

Tài liệu này tổng hợp các phương pháp hay nhất (best practices) và tiêu chuẩn ngành trong quản lý yêu cầu phần mềm, hỗ trợ các thành viên trong dự án.  Do thiếu thông tin cụ thể về dự án, tài liệu tập trung vào các khái niệm và nguyên tắc chung.

### I. Phương pháp và Tiêu chuẩn

**1. IEEE 830-1998 (Recommended Practice for Software Requirements Specifications):**  Đây là một tiêu chuẩn được công nhận rộng rãi về cách viết đặc tả yêu cầu phần mềm (SRS).  IEEE 830 đề xuất một cấu trúc chuẩn bao gồm:

* **Giới thiệu:** Mục đích, phạm vi, định nghĩa, tham chiếu.
* **Mô tả tổng quan:** Đặc điểm tổng quan của hệ thống, chức năng chính.
* **Yêu cầu cụ thể:**  Chi tiết về các yêu cầu chức năng và phi chức năng (performance, security, usability...).  Nên sử dụng kỹ thuật viết rõ ràng, không mơ hồ, tránh ngôn ngữ tự nhiên.
* **Mô hình:** Sử dụng các mô hình (ví dụ UML) để minh họa thiết kế hệ thống.
* **Phụ lục:** Tài liệu tham khảo, bảng, biểu đồ.

**2. BABOK (Business Analysis Body of Knowledge):** BABOK là một tập hợp kiến thức về phân tích nghiệp vụ, cung cấp khung cho việc thu thập, phân tích và quản lý yêu cầu.  Nó nhấn mạnh vào việc hiểu rõ nhu cầu của người dùng và chuyển đổi chúng thành yêu cầu phần mềm.

**3. Mô hình MoSCoW:** Phương pháp phân loại yêu cầu theo mức độ ưu tiên:

* **Must have (Phải có):**  Các yêu cầu bắt buộc, ảnh hưởng trực tiếp đến chức năng cốt lõi của hệ thống.
* **Should have (Nên có):**  Các yêu cầu quan trọng, tăng cường chức năng và trải nghiệm người dùng.
* **Could have (Có thể có):**  Các yêu cầu bổ sung, có thể triển khai sau này.
* **Won't have (Sẽ không có):**  Các yêu cầu bị loại bỏ do lý do nào đó (thời gian, chi phí, kỹ thuật...).


**4. Yêu cầu SMART:**  Các yêu cầu cần đáp ứng tiêu chí SMART:

* **Specific (Cụ thể):**  Rõ ràng, không mơ hồ.
* **Measurable (Đo lường được):**  Có thể đánh giá được mức độ hoàn thành.
* **Achievable (Thực hiện được):**  Khả thi về mặt kỹ thuật và tài nguyên.
* **Relevant (Có liên quan):**  Phù hợp với mục tiêu của dự án.
* **Time-bound (Có giới hạn thời gian):**  Có thời hạn hoàn thành cụ thể.


### II. Kỹ thuật thu thập yêu cầu

* **Phỏng vấn:**  Thu thập thông tin trực tiếp từ người dùng và các bên liên quan.
* **Khảo sát:**  Thu thập thông tin từ một số lượng lớn người dùng thông qua bảng câu hỏi.
* **Phân tích tài liệu:**  Phân tích các tài liệu hiện có (ví dụ: báo cáo, quy trình...).
* **Quan sát:**  Quan sát trực tiếp cách người dùng làm việc để hiểu rõ hơn về quy trình và nhu cầu.
* **Workshop:** Tổ chức các buổi workshop để thu thập ý kiến và thống nhất yêu cầu.


### III. Quản lý yêu cầu

* **Sử dụng công cụ quản lý yêu cầu:**  Jira, Trello, Confluence... để theo dõi, quản lý và cập nhật yêu cầu.
* **Kiểm soát phiên bản:** Sử dụng hệ thống quản lý phiên bản (ví dụ Git) để quản lý các thay đổi đối với yêu cầu.
* **Tài liệu hóa:**  Tất cả các yêu cầu cần được ghi chép đầy đủ và rõ ràng.
* **Truy xuất:**  Dễ dàng tìm kiếm và truy xuất các yêu cầu.
* **Phân tích rủi ro:**  Đánh giá các rủi ro có thể ảnh hưởng đến yêu cầu.
* **Quản lý thay đổi:**  Thiết lập quy trình quản lý thay đổi yêu cầu một cách hiệu quả.


### IV. Ví dụ về yêu cầu tốt

* **Yêu cầu xấu:**  "Hệ thống cần nhanh." (Không cụ thể, không đo lường được)
* **Yêu cầu tốt:**  "Hệ thống cần xử lý một yêu cầu trong vòng 2 giây, với độ trễ trung bình không quá 0.5 giây trong 99% trường hợp." (Cụ thể, đo lường được)


### V. Tài liệu tham khảo

* IEEE 830-1998: Recommended Practice for Software Requirements Specifications
* BABOK Guide
* [Thêm các tài liệu tham khảo khác nếu cần]


**Lưu ý:** Tài liệu này chỉ là một tổng quan chung.  Việc áp dụng các phương pháp và tiêu chuẩn cần được điều chỉnh cho phù hợp với từng dự án cụ thể.
```
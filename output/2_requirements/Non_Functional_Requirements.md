```markdown
# Non_Functional_Requirements.md

## Yêu cầu Phi chức năng cho Hệ thống Quản Lý Kho Hàng

Tài liệu này mô tả các yêu cầu phi chức năng cho Hệ thống Quản Lý Kho Hàng.  Các yêu cầu này tập trung vào các thuộc tính chất lượng của hệ thống, bao gồm hiệu suất, bảo mật, khả năng mở rộng, khả năng sử dụng, độ tin cậy, và khả năng bảo trì.

**1. Hiệu suất:**

* **Thời gian phản hồi:** Hệ thống phải phản hồi các yêu cầu của người dùng trong vòng 2 giây.
* **Khả năng xử lý:** Hệ thống phải có thể xử lý tối thiểu 1000 giao dịch/giây trong giờ cao điểm.
* **Thời gian tải:** Trang web phải tải trong vòng 3 giây.

**2. Bảo mật:**

* **Xác thực người dùng:** Hệ thống phải sử dụng cơ chế xác thực mạnh mẽ, bao gồm tên đăng nhập và mật khẩu, với mật khẩu phải tuân thủ các chính sách phức tạp.
* **Phân quyền:** Hệ thống phải có cơ chế phân quyền rõ ràng, cho phép quản trị viên cấp quyền truy cập cho từng người dùng dựa trên vai trò.
* **Mã hóa dữ liệu:** Tất cả dữ liệu nhạy cảm, bao gồm thông tin hàng hóa và thông tin người dùng, phải được mã hóa cả khi lưu trữ và truyền tải.
* **Kiểm soát truy cập:** Hệ thống phải ngăn chặn truy cập trái phép vào dữ liệu và chức năng.
* **Quản lý nhật ký:** Hệ thống phải ghi lại tất cả hoạt động của người dùng để phục vụ mục đích kiểm toán và giám sát.


**3. Khả năng mở rộng:**

* **Khả năng mở rộng:** Hệ thống phải có khả năng mở rộng để đáp ứng nhu cầu tăng trưởng dữ liệu và người dùng trong tương lai.  Hệ thống nên được thiết kế để dễ dàng thêm máy chủ và tài nguyên khi cần thiết.

**4. Khả năng sử dụng:**

* **Giao diện người dùng:** Giao diện người dùng phải trực quan, dễ sử dụng và thân thiện với người dùng.
* **Tài liệu hướng dẫn:** Hệ thống phải đi kèm với tài liệu hướng dẫn sử dụng đầy đủ và dễ hiểu.
* **Hỗ trợ đa ngôn ngữ:** Hệ thống nên hỗ trợ nhiều ngôn ngữ khác nhau.

**5. Độ tin cậy:**

* **Thời gian hoạt động:** Hệ thống phải hoạt động liên tục 99.9% thời gian.
* **Khả năng phục hồi:** Hệ thống phải có khả năng phục hồi nhanh chóng sau khi xảy ra sự cố.  Cơ chế sao lưu và khôi phục dữ liệu phải được thiết lập.

**6. Khả năng bảo trì:**

* **Khả năng bảo trì:** Hệ thống phải được thiết kế để dễ dàng bảo trì và cập nhật.
* **Quản lý lỗi:** Hệ thống phải có cơ chế quản lý lỗi hiệu quả, giúp phát hiện và khắc phục lỗi nhanh chóng.


**7. Khả năng tích hợp:**

* Hệ thống phải có khả năng tích hợp với các hệ thống khác như hệ thống quản lý bán hàng (nếu có).


**8. Khả năng tương thích:**

* Hệ thống phải tương thích với các trình duyệt web phổ biến.

**9. Khả năng an toàn:**

* Hệ thống phải được bảo vệ khỏi các cuộc tấn công mạng.

**10. Hiệu quả về chi phí:**

* Hệ thống phải được thiết kế để tiết kiệm chi phí vận hành và bảo trì.



```
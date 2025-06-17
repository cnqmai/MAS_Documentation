import os
import logging
import re # Cần để làm sạch và phân tích output
from crewai import Task
from utils.file_writer import write_output # Giữ lại cho các file .md
from memory.shared_memory import shared_memory
from docx import Document
from docx.shared import Inches # Có thể cần cho hình ảnh nếu có

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_text_for_docx(text: str) -> str:
    """
    Loại bỏ các ký tự có thể gây lỗi khi ghi vào file .docx hoặc làm phẳng Markdown cơ bản.
    """
    # Loại bỏ các ký tự điều khiển không in được (ví dụ: \x00 đến \x1F, trừ \t, \n, \r)
    clean_text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', text)
    # Thay thế các dấu xuống dòng kép bằng dấu xuống dòng đơn để tránh tạo đoạn trống quá nhiều
    clean_text = re.sub(r'\n\s*\n', '\n\n', clean_text).strip()

    # Có thể thêm các quy tắc để xử lý Markdown cơ bản thành văn bản thuần túy
    clean_text = re.sub(r'#{1,6}\s*', '', clean_text) # Loại bỏ Markdown heading
    clean_text = clean_text.replace('**', '').replace('__', '') # Loại bỏ bold
    clean_text = clean_text.replace('*', '').replace('_', '') # Loại bỏ italic/list item (cần cẩn thận nếu muốn list)
    clean_text = re.sub(r'^- ', '', clean_text, flags=re.MULTILINE) # Loại bỏ list item dấu gạch ngang
    clean_text = re.sub(r'^\d+\.\s*', '', clean_text, flags=re.MULTILINE) # Loại bỏ list item số

    return clean_text

def process_and_save_docx(task_output: str, file_path: str, document_title: str):
    """
    Tạo tài liệu Word (.docx) từ output của agent.
    Cố gắng phân tích các tiêu đề và đoạn văn cơ bản.
    """
    logging.info(f"--- Bắt đầu xử lý và lưu tài liệu Word: {file_path} ---")
    doc = Document()
    doc.add_heading(document_title, level=0) # Tiêu đề chính của tài liệu

    # Làm phẳng nội dung tổng thể để loại bỏ định dạng Markdown phức tạp
    cleaned_output = clean_text_for_docx(task_output)

    # Chia nhỏ nội dung thành các dòng để xử lý từng đoạn
    lines = cleaned_output.split('\n')
    current_section = []

    # Cố gắng thêm nội dung theo từng đoạn, giả định các dòng trống phân tách đoạn văn
    for line in lines:
        stripped_line = line.strip()
        if stripped_line:
            current_section.append(stripped_line)
        else:
            if current_section:
                # Thêm đoạn văn đã thu thập được
                doc.add_paragraph(' '.join(current_section))
                current_section = []
    # Thêm bất kỳ nội dung còn lại nào sau vòng lặp
    if current_section:
        doc.add_paragraph(' '.join(current_section))

    try:
        doc.save(file_path)
        logging.info(f"Đã lưu thành công tài liệu Word: {file_path}")
    except Exception as e:
        logging.error(f"Lỗi khi lưu tài liệu Word {file_path}: {e}", exc_info=True)
        # Lưu nội dung gốc vào file .txt để debug nếu có lỗi
        write_output(file_path + ".error_raw.txt", task_output)


def create_initiation_tasks(vision_agent, conops_agent, charter_agent,
                            project_manager_agent, researcher_agent,
                            output_base_dir):
    """
    Tạo các task liên quan đến khởi tạo dự án.
    Args:
        vision_agent, conops_agent, charter_agent: Agents cụ thể cho Initiation.
        project_manager_agent, researcher_agent: Các agent chung.
        output_base_dir: Đường dẫn thư mục base cho output của giai đoạn này.
    Returns:
        list: Danh sách các Task đã tạo.
    """
    system_request_summary = shared_memory.get("phase_0_initiation", "system_request_summary")
    if not system_request_summary:
        logging.warning("Lỗi: Không tìm thấy 'system_request_summary' trong shared_memory['phase_0_initiation']. Sử dụng giá trị mặc định.")
        system_request_summary = "Thông tin yêu cầu hệ thống bị thiếu."

    phase_output_dir = os.path.join(output_base_dir, "0_initiation")
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục đầu ra cho Phase 0 Initiation: {phase_output_dir}")

    # Task: Vision Document
    vision_task = Task(
        description=(
            f"Phân tích tài liệu System Request Summary sau và tạo tài liệu Tầm nhìn (Vision Document) "
            f"rõ ràng và truyền cảm hứng. Bao gồm mục tiêu, phạm vi, người dùng chính, và các tính năng cấp cao.\n"
            f"Đảm bảo nội dung được định dạng tốt, dễ đọc, không dùng Markdown phức tạp mà hãy viết như một tài liệu chính thức.\n"
            f"--- System Request Summary: {system_request_summary}\n---"
        ),
        expected_output="Tài liệu tiếng Việt 'Vision_Document.docx' đầy đủ và có cấu trúc, KHÔNG chứa Markdown. Chỉ văn bản thuần túy và các tiêu đề.",
        agent=vision_agent,
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Vision Task ---"),
            process_and_save_docx(str(output), os.path.join(phase_output_dir, "Vision_Document.docx"), "Tài liệu Tầm nhìn"),
            shared_memory.set("phase_0_initiation", "vision_document_path", os.path.join(phase_output_dir, "Vision_Document.docx")), # Lưu đường dẫn, không phải nội dung
            logging.info(f"Đã lưu Vision_Document.docx và cập nhật shared_memory.")
        )
    )

    # Task: Concept of Operations (ConOps)
    conops_task = Task(
        description=(
            f"Nghiên cứu System Request Summary và Vision Document (từ context) để tạo Concept of Operations (ConOps) đầy đủ. "
            f"Mô tả cách hệ thống sẽ được sử dụng trong thực tế, các kịch bản người dùng chính, và luồng công việc.\n"
            f"Đảm bảo nội dung được định dạng tốt, dễ đọc, không dùng Markdown phức tạp mà hãy viết như một tài liệu chính thức.\n"
            f"--- System Request Summary: {system_request_summary}\n---"
        ),
        expected_output="Tài liệu tiếng Việt 'Concept_of_Operations.docx' đầy đủ, mô tả cách thức vận hành của hệ thống. KHÔNG chứa Markdown. Chỉ văn bản thuần túy và các tiêu đề.",
        agent=conops_agent,
        context=[vision_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành ConOps Task ---"),
            process_and_save_docx(str(output), os.path.join(phase_output_dir, "Concept_of_Operations.docx"), "Khái niệm Vận hành"),
            shared_memory.set("phase_0_initiation", "conops_document_path", os.path.join(phase_output_dir, "Concept_of_Operations.docx")), # Lưu đường dẫn, không phải nội dung
            logging.info(f"Đã lưu Concept_of_Operations.docx và cập nhật shared_memory.")
        )
    )

    # Task: Project Charter
    charter_task = Task(
        description=(
            f"Dựa trên System Request Summary, Vision Document và ConOps (từ context), xây dựng Project Charter đầy đủ, "
            f"xác định rõ mục tiêu dự án, phạm vi, các bên liên quan, quyền hạn, ngân sách sơ bộ, và các mốc thời gian chính.\n"
            f"Đảm bảo nội dung được định dạng tốt, dễ đọc, không dùng Markdown phức tạp mà hãy viết như một tài liệu chính thức.\n"
            f"--- System Request Summary: {system_request_summary}\n---"
        ),
        expected_output="Tài liệu tiếng Việt 'Project_Charter.docx' đầy đủ, xác định rõ mục tiêu dự án, phạm vi, các bên liên quan và quyền hạn. KHÔNG chứa Markdown. Chỉ văn bản thuần túy và các tiêu đề.",
        agent=charter_agent,
        context=[vision_task, conops_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Charter Task ---"),
            process_and_save_docx(str(output), os.path.join(phase_output_dir, "Project_Charter.docx"), "Điều lệ Dự án"),
            shared_memory.set("phase_0_initiation", "project_charter_path", os.path.join(phase_output_dir, "Project_Charter.docx")), # Lưu đường dẫn, không phải nội dung
            logging.info(f"Đã lưu Project_Charter.docx và cập nhật shared_memory.")
        )
    )

    # Task: Project Initiation Validation
    project_initiation_validation_task = Task(
        description=(
            f"Đánh giá kỹ lưỡng các tài liệu được tạo ra trong Giai đoạn Khởi tạo (Vision Document, ConOps, Project Charter). "
            f"Kiểm tra tính hoàn chỉnh, rõ ràng, nhất quán và tuân thủ các yêu cầu ban đầu. "
            f"Tạo một báo cáo 'Validation_Report_Phase_0.md' tóm tắt kết quả đánh giá, "
            f"liệt kê các điểm cần cải thiện nếu có và xác nhận việc hoàn thành giai đoạn."
        ),
        expected_output="Tài liệu tiếng Việt 'Validation_Report_Phase_0.md' tóm tắt kết quả đánh giá giai đoạn khởi tạo. Tài liệu này là Markdown.",
        agent=project_manager_agent,
        context=[vision_task, conops_task, charter_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Project Initiation Validation Task ---"),
            write_output(os.path.join(phase_output_dir, "Validation_Report_Phase_0.md"), str(output)),
            shared_memory.set("phase_0_initiation", "validation_report_path", os.path.join(phase_output_dir, "Validation_Report_Phase_0.md")), # Lưu đường dẫn
            logging.info(f"Đã lưu Validation_Report_Phase_0.md và cập nhật shared_memory.")
        )
    )

    # Task: Research Initiation Best Practices
    research_initiation_best_practices = Task(
        description=(
            f"Nghiên cứu các phương pháp hay nhất (best practices) và tiêu chuẩn ngành liên quan đến giai đoạn khởi tạo dự án "
            f"để hỗ trợ các agent khác. Ví dụ: cấu trúc điển hình của Vision Document, ConOps, Project Charter.\n"
            f"--- Yêu cầu chung của dự án: {system_request_summary}"
        ),
        expected_output="Tài liệu tiếng Việt 'Initiation_Research_Summary.md' tổng hợp các kiến thức nghiên cứu hữu ích. Tài liệu này là Markdown.",
        agent=researcher_agent,
        context=[project_initiation_validation_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Research Initiation Best Practices Task ---"),
            write_output(os.path.join(phase_output_dir, "Initiation_Research_Summary.md"), str(output)),
            shared_memory.set("phase_0_initiation", "research_summary_path", os.path.join(phase_output_dir, "Initiation_Research_Summary.md")), # Lưu đường dẫn
            logging.info(f"Đã lưu Initiation_Research_Summary.md và cập nhật shared_memory.")
        )
    )

    return [
        vision_task,
        conops_task,
        charter_task,
        project_initiation_validation_task,
        research_initiation_best_practices
    ]
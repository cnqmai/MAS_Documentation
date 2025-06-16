# tasks/design_tasks.py

from crewai import Task
from utils.file_writer import write_output
from memory.shared_memory import shared_memory
from tasks.quality_gate_tasks import create_quality_gate_task
from tasks.research_tasks import create_research_task
import os
import logging # Thêm logging để thông báo rõ hơn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_design_tasks(system_architect_agent, project_manager_agent, researcher_agent, output_base_dir):
    """
    Tạo các task liên quan đến thiết kế hệ thống.
    Args:
        system_architect_agent: Agent chính cho Design.
        project_manager_agent, researcher_agent: Các agent chung.
        output_base_dir: Đường dẫn thư mục base cho đầu ra.
    Returns:
        list: Danh sách các Task đã tạo.
    """
    # Lấy dữ liệu từ phase trước (Requirements)
    srs = shared_memory.get("phase_2_requirements", "srs")
    brd = shared_memory.get("phase_2_requirements", "brd") # Có thể cần BRD cho ngữ cảnh kinh doanh
    project_plan = shared_memory.get("phase_1_planning", "project_plan") # Để xem xét ràng buộc

    if not srs:
        logging.warning("Cảnh báo: Thiếu SRS trong shared_memory cho giai đoạn Thiết kế.")
        srs = "Không có SRS từ giai đoạn Yêu cầu."
    if not brd:
        brd = "Không có BRD từ giai đoạn Yêu cầu."
    if not project_plan:
        project_plan = "Không có Project Plan."

    # Tạo thư mục con cho Phase 3 Design (nếu chưa có)
    phase_output_dir = os.path.join(output_base_dir, "3_design")
    os.makedirs(phase_output_dir, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục đầu ra cho Phase 3: {phase_output_dir}")

    # Task nghiên cứu cho Design Phase
    research_design_task = create_research_task(
        researcher_agent,
        "Phase 3: Design",
        f"phương pháp thiết kế hệ thống (HLD, LLD, DFD, Sequence Diagram, Database Design, API Design, Security Architecture), các tiêu chuẩn thiết kế (IEEE, UML), kiến trúc tham chiếu. Dựa trên yêu cầu: {srs[:200]}...",
        "design_research_summary.md"
    )
    research_design_task.callback = lambda output: (
        logging.info("--- Hoàn thành Research Design Task ---"),
        write_output(os.path.join(phase_output_dir, "design_research_summary.md"), str(output)),
        shared_memory.set("phase_3_design", "design_research_summary", str(output))
    )


    # Task: High-Level Design (HLD)
    hld_task = Task(
        description=(
            f"Dựa trên SRS và kết quả nghiên cứu Design, tạo High-Level Design (HLD) của hệ thống. "
            f"HLD cần mô tả tổng quan kiến trúc hệ thống, các thành phần chính, và cách chúng tương tác. "
            f"Xác định các công nghệ và khung công tác (framework) chính sẽ được sử dụng.\n"
            f"--- SRS: {srs}\n"
            f"--- Nghiên cứu Design: {shared_memory.get('phase_3_design', 'design_research_summary')}"
        ),
        expected_output="Tài liệu tiếng Việt 'High_Level_Design.docx' mô tả kiến trúc tổng quan của hệ thống.",
        agent=system_architect_agent,
        context=[research_design_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành HLD Task ---"),
            write_output(os.path.join(phase_output_dir, "High_Level_Design.docx"), str(output)),
            shared_memory.set("phase_3_design", "hld", str(output))
        )
    )

    # Task: Low-Level Design (LLD)
    lld_task = Task(
        description=(
            f"Dựa trên HLD và SRS, phát triển Low-Level Design (LLD) chi tiết. "
            f"LLD cần đi sâu vào thiết kế từng module, bao gồm cấu trúc dữ liệu, thuật toán, "
            f"thiết kế API, thiết kế cơ sở dữ liệu (schema), và luồng xử lý chi tiết. "
            f"Đảm bảo tính bảo mật được tích hợp vào thiết kế.\n"
            f"--- HLD: {shared_memory.get('phase_3_design', 'hld')}\n"
            f"--- SRS: {srs}\n"
            f"--- Nghiên cứu Design: {shared_memory.get('phase_3_design', 'design_research_summary')}"
        ),
        expected_output="Tài liệu tiếng Việt 'Low_Level_Design.docx' mô tả thiết kế chi tiết từng module, bao gồm DB Schema và API Spec.",
        agent=system_architect_agent,
        context=[hld_task, research_design_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành LLD Task ---"),
            write_output(os.path.join(phase_output_dir, "Low_Level_Design.docx"), str(output)),
            shared_memory.set("phase_3_design", "lld", str(output))
        )
    )

    # Task: Security Architecture & Diagrams (DFD, Sequence)
    security_diagrams_task = Task(
        description=(
            f"Từ HLD và LLD, tạo tài liệu kiến trúc bảo mật (Security Architecture) và các biểu đồ cần thiết "
            f"như Data Flow Diagram (DFD) và Sequence Diagram để minh họa luồng dữ liệu và tương tác giữa các thành phần. "
            f"Đảm bảo tuân thủ các tiêu chuẩn bảo mật đã nghiên cứu.\n"
            f"--- HLD: {shared_memory.get('phase_3_design', 'hld')}\n"
            f"--- LLD: {shared_memory.get('phase_3_design', 'lld')}\n"
            f"--- Nghiên cứu Design: {shared_memory.get('phase_3_design', 'design_research_summary')}"
        ),
        expected_output="Tài liệu tiếng Việt 'Security_Architecture_and_Diagrams.docx' bao gồm kiến trúc bảo mật và các biểu đồ DFD, Sequence.",
        agent=system_architect_agent,
        context=[hld_task, lld_task, research_design_task],
        callback=lambda output: (
            logging.info(f"--- Hoàn thành Security Architecture & Diagrams Task ---"),
            write_output(os.path.join(phase_output_dir, "Security_Architecture_and_Diagrams.docx"), str(output)),
            shared_memory.set("phase_3_design", "security_diagrams", str(output))
        )
    )

    # Task Quality Gate cho Design Phase
    quality_gate_design_task = create_quality_gate_task(
        project_manager_agent,
        "Phase 3: Design",
        "lld", # Key chứa output chính cần kiểm tra
        "High-Level Design (HLD), Low-Level Design (LLD), Database Schema, API Specification, Security Architecture, DFD, Sequence Diagrams",
        "validation_report_phase_3.md"
    )
    quality_gate_design_task.context = [
        hld_task, lld_task, security_diagrams_task, research_design_task
    ]
    quality_gate_design_task.callback = lambda output: (
        logging.info(f"--- Hoàn thành Quality Gate Task cho Design Phase ---"),
        write_output(os.path.join(phase_output_dir, "validation_report_phase_3.md"), str(output)),
        shared_memory.set("phase_3_design", "validation_report", str(output))
    )


    return [research_design_task, hld_task, lld_task, security_diagrams_task, quality_gate_design_task]
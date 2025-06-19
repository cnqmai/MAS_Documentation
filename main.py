import os
import logging
import sys

from crewai import Crew, Process, Task

from bootstrap import initialize_environment
from memory.shared_memory import shared_memory
from utils.file_writer import write_output

from agents.initiation_agent import create_initiation_agent
from agents.planning_agent import create_planning_agent
from agents.requirement_agent import create_requirement_agent
from agents.design_agent import create_design_agent
from agents.development_agent import create_development_agent
from agents.testing_agent import create_testing_agent
from agents.deployment_agent import create_deployment_agent
from agents.maintenance_agent import create_maintenance_agent
from agents.researcher_agent import create_researcher_agent
from agents.project_manager_agent import create_project_manager_agent
from agents.input_agent import create_input_agent

from tasks.input_tasks import run_input_collection_conversation
from tasks.initiation_tasks import create_initiation_tasks
from tasks.planning_tasks import create_planning_tasks
from tasks.requirement_tasks import create_requirement_tasks
from tasks.design_tasks import create_design_tasks
from tasks.development_tasks import create_development_tasks
from tasks.testing_tasks import create_testing_tasks
from tasks.deployment_tasks import create_deployment_tasks
from tasks.maintenance_tasks import create_maintenance_tasks
from tasks.research_tasks import create_research_task
from tasks.quality_gate_tasks import create_quality_gate_task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

OUTPUT_BASE_DIR = "output"
INPUT_BASE_DIR = os.path.join(os.path.dirname(OUTPUT_BASE_DIR), "input")

def run_project_crew():
    """
    Chạy toàn bộ quy trình phát triển dự án phần mềm qua các giai đoạn.
    Mỗi giai đoạn được đại diện bởi một Crew riêng.
    """
    logging.info("Bắt đầu quy trình Project Crew.")

    os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)
    os.makedirs(INPUT_BASE_DIR, exist_ok=True)

    # ----------------------------------------------------
    # GIAI ĐOẠN 0: KHỞI TẠO DỰ ÁN VÀ THU THẬP YÊU CẦU BAN ĐẦU
    # ----------------------------------------------------
    logging.info("--- Bắt đầu Giai đoạn 0: Khởi tạo và Thu thập Yêu cầu Ban đầu ---")

    input_agent = create_input_agent()
    initiation_agent = create_initiation_agent()
    project_manager_agent = create_project_manager_agent()
    researcher_agent = create_researcher_agent()

    logging.info("Bắt đầu thu thập yêu cầu tương tác từ người dùng...")
    run_input_collection_conversation(input_agent, INPUT_BASE_DIR)
    
    system_request_summary = shared_memory.get('phase_0_initiation', 'system_request_summary')
    if not system_request_summary:
        logging.error("Không tìm thấy system_request_summary trong shared_memory. Kết thúc quy trình.")
        sys.exit(1)
    logging.info("Yêu cầu ban đầu đã được thu thập và lưu vào shared_memory.")

    initiation_tasks_list = create_initiation_tasks(
        project_manager_agent,
        researcher_agent,
        initiation_agent,
        OUTPUT_BASE_DIR
    )

    initiation_crew = Crew(
        agents=[project_manager_agent, researcher_agent, initiation_agent],
        tasks=initiation_tasks_list,
        process=Process.sequential,
        verbose=True
    )
    logging.info("Đang chạy Initiation Crew...")
    initiation_result = initiation_crew.kickoff()
    logging.info("Hoàn thành Initiation Crew.")
    print("\n\n#############################################")
    print("## Initiation Crew Completed!              ##")
    print("#############################################\n")
    print(f"Initiation Result:\n{initiation_result}\n")

    # Các giai đoạn khác giữ nguyên
    logging.info("--- Bắt đầu Giai đoạn 1: Lập Kế hoạch Dự án ---")
    planing_agent = create_planning_agent()
    planning_tasks_list = create_planning_tasks(project_manager_agent, researcher_agent, planing_agent, OUTPUT_BASE_DIR)
    planning_crew = Crew(agents=[project_manager_agent, researcher_agent, planing_agent], tasks=planning_tasks_list, process=Process.sequential, verbose=True)
    logging.info("Đang chạy Planning Crew...")
    planning_result = planning_crew.kickoff()
    logging.info("Hoàn thành Planning Crew.")
    print("\n\n#############################################")
    print("## Planning Crew Completed!                ##")
    print("#############################################\n")
    print(f"Planning Result:\n{planning_result}\n")

    logging.info("--- Bắt đầu Giai đoạn 2: Phân tích và Đặc tả Yêu cầu ---")
    requirement_agent = create_requirement_agent()
    requirement_tasks_list = create_requirement_tasks(requirement_agent, project_manager_agent, researcher_agent, OUTPUT_BASE_DIR)
    requirement_crew = Crew(agents=[requirement_agent, project_manager_agent, researcher_agent], tasks=requirement_tasks_list, process=Process.sequential, verbose=True)
    logging.info("Đang chạy Requirement Crew...")
    requirement_result = requirement_crew.kickoff()
    logging.info("Hoàn thành Requirement Crew.")
    print("\n\n#############################################")
    print("## Requirement Crew Completed!             ##")
    print("#############################################\n")
    print(f"Requirement Result:\n{requirement_result}\n")

    logging.info("--- Bắt đầu Giai đoạn 3: Thiết kế Hệ thống ---")
    design_agent = create_design_agent()
    design_tasks_list = create_design_tasks(design_agent, project_manager_agent, researcher_agent, OUTPUT_BASE_DIR)
    design_crew = Crew(agents=[design_agent, project_manager_agent, researcher_agent], tasks=design_tasks_list, process=Process.sequential, verbose=True)
    logging.info("Đang chạy Design Crew...")
    design_result = design_crew.kickoff()
    logging.info("Hoàn thành Design Crew.")
    print("\n\n#############################################")
    print("## Design Crew Completed!                  ##")
    print("#############################################\n")
    print(f"Design Result:\n{design_result}\n")

    logging.info("--- Bắt đầu Giai đoạn 4: Phát triển và Triển khai Thử nghiệm ---")
    development_agent = create_development_agent()
    development_tasks_list = create_development_tasks(development_agent, project_manager_agent, OUTPUT_BASE_DIR)
    development_crew = Crew(agents=[development_agent, project_manager_agent], tasks=development_tasks_list, process=Process.sequential, verbose=True)
    logging.info("Đang chạy Development Crew...")
    development_result = development_crew.kickoff()
    logging.info("Hoàn thành Development Crew.")
    print("\n\n#############################################")
    print("## Development Crew Completed!             ##")
    print("#############################################\n")
    print(f"Development Result:\n{development_result}\n")

    logging.info("--- Bắt đầu Giai đoạn 5: Kiểm thử và Đảm bảo Chất lượng ---")
    testing_agent = create_testing_agent()
    testing_tasks_list = create_testing_tasks(testing_agent, project_manager_agent, OUTPUT_BASE_DIR)
    testing_crew = Crew(agents=[testing_agent, project_manager_agent], tasks=testing_tasks_list, process=Process.sequential, verbose=True)
    logging.info("Đang chạy Testing Crew...")
    testing_result = testing_crew.kickoff()
    logging.info("Hoàn thành Testing Crew.")
    print("\n\n#############################################")
    print("## Testing Crew Completed!                 ##")
    print("#############################################\n")
    print(f"Testing Result:\n{testing_result}\n")

    logging.info("--- Bắt đầu Giai đoạn 6: Triển khai và Giao nộp ---")
    deployment_agent = create_deployment_agent()
    deployment_tasks_list = create_deployment_tasks(deployment_agent, project_manager_agent, researcher_agent, OUTPUT_BASE_DIR)
    deployment_crew = Crew(agents=[deployment_agent, project_manager_agent, researcher_agent], tasks=deployment_tasks_list, process=Process.sequential, verbose=True)
    logging.info("Đang chạy Deployment Crew...")
    deployment_result = deployment_crew.kickoff()
    logging.info("Hoàn thành Deployment Crew.")
    print("\n\n#############################################")
    print("## Deployment Crew Completed!              ##")
    print("#############################################\n")
    print(f"Deployment Result:\n{deployment_result}\n")

    logging.info("--- Bắt đầu Giai đoạn 7: Bảo trì và Hỗ trợ ---")
    site_reliability_engineer_agent = create_maintenance_agent()
    maintenance_tasks_list = create_maintenance_tasks(site_reliability_engineer_agent, project_manager_agent, researcher_agent, OUTPUT_BASE_DIR)
    maintenance_crew = Crew(agents=[site_reliability_engineer_agent, project_manager_agent, researcher_agent], tasks=maintenance_tasks_list, process=Process.sequential, verbose=True)
    logging.info("Đang chạy Maintenance Crew...")
    maintenance_result = maintenance_crew.kickoff()
    logging.info("Hoàn thành Maintenance Crew.")
    print("\n\n#############################################")
    print("## Maintenance Crew Completed!             ##")
    print("#############################################\n")
    print(f"Maintenance Result:\n{maintenance_result}\n")

    logging.info("Quy trình Project Crew hoàn tất.")
    return maintenance_result

if __name__ == "__main__":
    env_initialized = initialize_environment()
    if not env_initialized:
        logging.error("Ứng dụng không thể khởi động do lỗi môi trường. Vui lòng kiểm tra log.")
        sys.exit(1)
    final_project_summary = run_project_crew()
    print(f"\n\nFINAL PROJECT SUMMARY:\n{final_project_summary}")
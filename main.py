import os
import logging
import sys

from crewai import Crew, Process, Task

# Import hàm khởi tạo môi trường từ bootstrap.py
from bootstrap import initialize_environment

# Import shared_memory và file_writer
from memory.shared_memory import shared_memory
from utils.file_writer import write_output

# Imports for agents (assuming they are in agents/ directory)
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

# Imports for tasks (assuming they are in tasks/ directory)
from tasks.input_tasks import run_input_collection_conversation
from tasks.initiation_tasks import create_initiation_tasks
from tasks.planning_tasks import create_planning_tasks
from tasks.requirement_tasks import create_requirement_tasks
from tasks.design_tasks import create_design_tasks
from tasks.development_tasks import create_development_tasks
from tasks.testing_tasks import create_testing_tasks
from tasks.deployment_tasks import create_deployment_tasks
from tasks.maintenance_tasks import create_maintenance_tasks

# Cấu hình logging chính cho ứng dụng
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_project_crew(): # Đã bỏ tham số system_request
    logging.info("Bắt đầu quy trình Project Crew.")

    # --- Định nghĩa và đảm bảo các thư mục đầu ra ---
    # Thư mục cho bản tóm tắt yêu cầu ban đầu (System_Request_Summary.md)
    initial_summary_output_dir = "input"
    # Thư mục gốc cho tất cả các output của các giai đoạn khác (Initiation, Planning, v.v.)
    project_outputs_root = "output" # ĐÃ SỬA TỪ "outputs" THÀNH "output"

    os.makedirs(initial_summary_output_dir, exist_ok=True)
    os.makedirs(project_outputs_root, exist_ok=True)
    logging.info(f"Đã đảm bảo thư mục output cho tóm tắt ban đầu: {initial_summary_output_dir}")
    logging.info(f"Đã đảm bảo thư mục output chính của dự án: {project_outputs_root}")

    # --- Khởi tạo các Agent chung ---
    logging.info("Khởi tạo các Agent chung...")
    input_agent = create_input_agent()
    researcher_agent = create_researcher_agent()
    project_manager_agent = create_project_manager_agent()
    logging.info("Đã khởi tạo các Agent chung: input_agent, researcher_agent, project_manager_agent.")

    # --- Giai đoạn 0: Thu thập yêu cầu ban đầu từ người dùng (Interactive Input) ---
    logging.info("--- Bắt đầu Giai đoạn 0: Thu thập yêu cầu ban đầu (Initial Requirements Gathering) ---")
    # Hàm này sẽ tương tác với người dùng và lưu 'system_request_summary' vào shared_memory
    # Truyền thư mục output riêng cho bản tóm tắt ban đầu
    run_input_collection_conversation(input_agent, initial_summary_output_dir)
    logging.info("--- Hoàn thành Giai đoạn 0: Thu thập yêu cầu ban đầu ---")


    # --- 1. Giai đoạn Khởi tạo (Initiation) ---
    logging.info("Bắt đầu Giai đoạn 1: Khởi tạo dự án (Initiation Phase)")

    # Khởi tạo các agent cụ thể cho Initiation Phase
    vision_agent, conops_agent, charter_agent = create_initiation_agent()

    # Tạo các task của Initiation Phase (sử dụng các agent đã được truyền vào)
    # create_initiation_tasks sẽ lấy system_request_summary từ shared_memory
    initiation_tasks_list = create_initiation_tasks(
        vision_agent, conops_agent, charter_agent,
        project_manager_agent, researcher_agent, # Truyền thêm PM và Researcher vào tạo task
        project_outputs_root # Truyền đường dẫn base dir cho các output chính
    )

    logging.info("Đã tạo các task cho Initiation Phase.")

    initiation_crew = Crew(
        agents=[vision_agent, conops_agent, charter_agent, input_agent, project_manager_agent, researcher_agent],
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


    # --- Các giai đoạn tiếp theo ---

    # 2. Giai đoạn Lập kế hoạch (Planning)
    logging.info("Bắt đầu Giai đoạn 2: Lập kế hoạch (Planning Phase)")
    planning_orchestrator_agent = create_planning_agent()
    planning_tasks_list = create_planning_tasks(
        planning_orchestrator_agent,
        project_manager_agent,
        researcher_agent,
        project_outputs_root # Truyền đường dẫn base dir
    )
    planning_crew = Crew(
        agents=[planning_orchestrator_agent, project_manager_agent, researcher_agent],
        tasks=planning_tasks_list,
        process=Process.sequential,
        verbose=True
    )
    logging.info("Đang chạy Planning Crew...")
    planning_result = planning_crew.kickoff()
    logging.info("Hoàn thành Planning Crew.")
    print("\n\n#############################################")
    print("## Planning Crew Completed!                ##")
    print("#############################################\n")
    print(f"Planning Result:\n{planning_result}\n")

    # 3. Giai đoạn Yêu cầu (Requirements)
    logging.info("Bắt đầu Giai đoạn 3: Yêu cầu (Requirements Phase)")
    requirement_analyst_agent = create_requirement_agent()
    requirement_tasks_list = create_requirement_tasks(
        requirement_analyst_agent,
        project_manager_agent,
        researcher_agent,
        project_outputs_root # Truyền đường dẫn base dir
    )
    requirement_crew = Crew(
        agents=[requirement_analyst_agent, project_manager_agent, researcher_agent],
        tasks=requirement_tasks_list,
        process=Process.sequential,
        verbose=True
    )
    logging.info("Đang chạy Requirements Crew...")
    requirements_result = requirement_crew.kickoff()
    logging.info("Hoàn thành Requirements Crew.")
    print("\n\n#############################################")
    print("## Requirements Crew Completed!            ##")
    print("#############################################\n")
    print(f"Requirements Result:\n{requirements_result}\n")

    # 4. Giai đoạn Thiết kế (Design)
    logging.info("Bắt đầu Giai đoạn 4: Thiết kế (Design Phase)")
    system_architect_agent = create_design_agent()
    design_tasks_list = create_design_tasks(
        system_architect_agent,
        project_manager_agent,
        researcher_agent,
        project_outputs_root # Truyền đường dẫn base dir
    )
    design_crew = Crew(
        agents=[system_architect_agent, project_manager_agent, researcher_agent],
        tasks=design_tasks_list,
        process=Process.sequential,
        verbose=True
    )
    logging.info("Đang chạy Design Crew...")
    design_result = design_crew.kickoff()
    logging.info("Hoàn thành Design Crew.")
    print("\n\n#############################################")
    print("## Design Crew Completed!                  ##")
    print("#############################################\n")
    print(f"Design Result:\n{design_result}\n")

    # 5. Giai đoạn Phát triển (Development)
    logging.info("Bắt đầu Giai đoạn 5: Phát triển (Development Phase)")
    lead_software_engineer_agent = create_development_agent()
    development_tasks_list = create_development_tasks(
        lead_software_engineer_agent,
        project_manager_agent,
        researcher_agent,
        project_outputs_root # Truyền đường dẫn base dir
    )
    development_crew = Crew(
        agents=[lead_software_engineer_agent, project_manager_agent, researcher_agent],
        tasks=development_tasks_list,
        process=Process.sequential,
        verbose=True
    )
    logging.info("Đang chạy Development Crew...")
    development_result = development_crew.kickoff()
    logging.info("Hoàn thành Development Crew.")
    print("\n\n#############################################")
    print("## Development Crew Completed!             ##")
    print("#############################################\n")
    print(f"Development Result:\n{development_result}\n")

    # 6. Giai đoạn Kiểm thử (Testing)
    logging.info("Bắt đầu Giai đoạn 6: Kiểm thử (Testing Phase)")
    qa_automation_engineer_agent = create_testing_agent()
    testing_tasks_list = create_testing_tasks(
        qa_automation_engineer_agent,
        project_manager_agent,
        researcher_agent,
        project_outputs_root # Truyền đường dẫn base dir
    )
    testing_crew = Crew(
        agents=[qa_automation_engineer_agent, project_manager_agent, researcher_agent],
        tasks=testing_tasks_list,
        process=Process.sequential,
        verbose=True
    )
    logging.info("Đang chạy Testing Crew...")
    testing_result = testing_crew.kickoff()
    logging.info("Hoàn thành Testing Crew.")
    print("\n\n#############################################")
    print("## Testing Crew Completed!                 ##")
    print("#############################################\n")
    print(f"Testing Result:\n{testing_result}\n")

    # 7. Giai đoạn Triển khai (Deployment)
    logging.info("Bắt đầu Giai đoạn 7: Triển khai (Deployment Phase)")
    devops_engineer_agent = create_deployment_agent()
    deployment_tasks_list = create_deployment_tasks(
        devops_engineer_agent,
        project_manager_agent,
        researcher_agent,
        project_outputs_root # Truyền đường dẫn base dir
    )
    deployment_crew = Crew(
        agents=[devops_engineer_agent, project_manager_agent, researcher_agent],
        tasks=deployment_tasks_list,
        process=Process.sequential,
        verbose=True
    )
    logging.info("Đang chạy Deployment Crew...")
    deployment_result = deployment_crew.kickoff()
    logging.info("Hoàn thành Deployment Crew.")
    print("\n\n#############################################")
    print("## Deployment Crew Completed!              ##")
    print("#############################################\n")
    print(f"Deployment Result:\n{deployment_result}\n")

    # 8. Giai đoạn Bảo trì (Maintenance)
    logging.info("Bắt đầu Giai đoạn 8: Bảo trì (Maintenance Phase)")
    site_reliability_engineer_agent = create_maintenance_agent()
    maintenance_tasks_list = create_maintenance_tasks(
        site_reliability_engineer_agent,
        project_manager_agent,
        researcher_agent,
        project_outputs_root # Truyền đường dẫn base dir
    )
    maintenance_crew = Crew(
        agents=[site_reliability_engineer_agent, project_manager_agent, researcher_agent],
        tasks=maintenance_tasks_list,
        process=Process.sequential,
        verbose=True
    )
    logging.info("Đang chạy Maintenance Crew...")
    maintenance_result = maintenance_crew.kickoff()
    logging.info("Hoàn thành Maintenance Crew.")
    print("\n\n#############################################")
    print("## Maintenance Crew Completed!             ##")
    print("#############################################\n")
    print(f"Maintenance Result:\n{maintenance_result}\n")


    # Kết thúc toàn bộ quá trình và trả về kết quả cuối cùng
    logging.info("Quy trình Project Crew hoàn tất.")
    return maintenance_result # Hoặc một summary tổng thể

# Đây là điểm khởi chạy chính của ứng dụng
if __name__ == "__main__":
    # 1. Khởi tạo môi trường (gọi từ bootstrap.py)
    # Hàm initialize_environment() trả về True nếu thành công, False nếu thất bại (ví dụ: thiếu API key)
    env_initialized = initialize_environment()

    if not env_initialized:
        logging.error("Ứng dụng không thể khởi động do lỗi môi trường. Vui lòng kiểm tra log.")
        sys.exit(1) # Thoát ứng dụng nếu thiếu API key

    # 2. Chạy toàn bộ quy trình Project Crew
    # initial_request parameter đã được loại bỏ vì input giờ là tương tác
    final_output = run_project_crew()
    print("\nFinal Project Output Summary:")
    print(final_output)
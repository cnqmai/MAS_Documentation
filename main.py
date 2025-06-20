import os
import logging
from crewai import Crew, Process
from memory.shared_memory import SharedMemory

# Import agents
from agents.input_agent import create_input_agent
from agents.researcher_agent import create_researcher_agent
from agents.project_manager_agent import create_project_manager_agent
from agents.initiation_agents import create_initiation_agent
from agents.planning_agents import create_planning_agent
from agents.requirement_agents import create_requirement_agent
from agents.design_agents import create_design_agent
from agents.development_agents import create_development_agent
from agents.testing_agents import create_testing_agent
from agents.deployment_agents import create_deployment_agent
from agents.maintenance_agents import create_maintenance_agent

# Import tasks
from tasks.input_tasks import run_input_collection_conversation
from tasks.initiation_tasks import create_initiation_tasks
from tasks.planning_tasks import create_planning_tasks
from tasks.requirement_tasks import create_requirements_tasks
from tasks.design_tasks import create_design_tasks
from tasks.development_tasks import create_development_tasks
from tasks.testing_tasks import create_testing_tasks
from tasks.deployment_tasks import create_deployment_tasks
from tasks.maintenance_tasks import create_maintenance_tasks
from tasks.quality_gate_tasks import create_quality_gate_tasks
from tasks.research_tasks import create_research_tasks

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_agent(agent):
    """Kiểm tra cấu hình agent để đảm bảo không có lỗi."""
    try:
        if hasattr(agent, 'tools') and agent.tools:
            for tool in agent.tools:
                if not isinstance(tool, (type, object)) or not hasattr(tool, '__call__'):
                    raise ValueError(f"Công cụ không hợp lệ trong agent {agent.role}: {tool}")
        logging.info(f"Agent {agent.role} được xác thực thành công")
    except Exception as e:
        logging.error(f"Lỗi khi xác thực agent {agent.role}: {e}")
        raise

def main():
    INPUT_BASE_DIR = "input"
    OUTPUT_BASE_DIR = "output"
    shared_memory = SharedMemory()

    # Create agents
    try:
        input_agent = create_input_agent()
        validate_agent(input_agent)
        researcher_agent = create_researcher_agent()
        validate_agent(researcher_agent)
        project_manager_agent = create_project_manager_agent()
        validate_agent(project_manager_agent)
        initiation_agent = create_initiation_agent()
        validate_agent(initiation_agent)
        planning_agent = create_planning_agent()
        validate_agent(planning_agent)
        requirement_agent = create_requirement_agent()
        validate_agent(requirement_agent)
        design_agent = create_design_agent()
        validate_agent(design_agent)
        development_agent = create_development_agent()
        validate_agent(development_agent)
        testing_agent = create_testing_agent()
        validate_agent(testing_agent)
        deployment_agent = create_deployment_agent()
        validate_agent(deployment_agent)
        maintenance_agent = create_maintenance_agent()
        validate_agent(maintenance_agent)
    except Exception as e:
        logging.error(f"Lỗi khi tạo agents: {e}")
        raise

    # Create output folders
    phases = [
        "0_initiation", "1_planning", "2_requirements", "3_design",
        "4_development", "5_testing", "6_deployment", "7_maintenance"
    ]
    for phase in phases:
        os.makedirs(os.path.join(OUTPUT_BASE_DIR, phase), exist_ok=True)

    # ✅ Pre-phase: Thu thập yêu cầu ban đầu
    try:
        logging.info("Bắt đầu thu thập yêu cầu ban đầu (pre-phase)")
        print("\n##### BẮT ĐẦU PRE-PHASE: THU THẬP YÊU CẦU BAN ĐẦU #####")
        run_input_collection_conversation(input_agent, INPUT_BASE_DIR, shared_memory)
        print("##### KẾT THÚC PRE-PHASE: THU THẬP YÊU CẦU BAN ĐẦU #####\n")
    except Exception as e:
        logging.error(f"Lỗi khi thực thi thu thập yêu cầu ban đầu: {e}", exc_info=True)
        raise

    # Giai đoạn 0: Khởi tạo (Initiation)
    initiation_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[:1]
    initiation_research_crew = Crew(
        agents=[researcher_agent],
        tasks=initiation_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 0: KHỞI TẠO #####")
    initiation_research_crew.kickoff()
    print("##### KẾT THÚC NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 0: KHỞI TẠO #####\n")

    initiation_tasks = create_initiation_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, initiation_agent)
    initiation_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, initiation_agent],
        tasks=initiation_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 0: KHỞI TẠO #####")
    initiation_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 0: KHỞI TẠO #####\n")

    initiation_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[:1]
    initiation_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=initiation_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 0: KHỞI TẠO #####")
    initiation_quality_crew.kickoff()
    print("##### KẾT THÚC KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 0: KHỞI TẠO #####\n")

    # Giai đoạn 1: Lập kế hoạch (Planning)
    planning_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[1:2]
    planning_research_crew = Crew(
        agents=[researcher_agent],
        tasks=planning_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 1: LẬP KẾ HOẠCH #####")
    planning_research_crew.kickoff()
    print("##### KẾT THÚC NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 1: LẬP KẾ HOẠCH #####\n")

    planning_tasks = create_planning_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, planning_agent)
    planning_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, planning_agent],
        tasks=planning_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 1: LẬP KẾ HOẠCH #####")
    planning_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 1: LẬP KẾ HOẠCH #####\n")

    planning_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[1:2]
    planning_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=planning_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 1: LẬP KẾ HOẠCH #####")
    planning_quality_crew.kickoff()
    print("##### KẾT THÚC KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 1: LẬP KẾ HOẠCH #####\n")

    # Giai đoạn 2: Yêu cầu (Requirements)
    requirements_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[2:3]
    requirements_research_crew = Crew(
        agents=[researcher_agent],
        tasks=requirements_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU NGHIÊN C�ứU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 2: YÊU CẦU #####")
    requirements_research_crew.kickoff()
    print("##### KẾT THÚC NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 2: YÊU CẦU #####\n")

    requirements_tasks = create_requirements_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, requirement_agent)
    requirements_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, requirement_agent],
        tasks=requirements_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 2: YÊU CẦU #####")
    requirements_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 2: YÊU CẦU #####\n")

    requirements_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[2:3]
    requirements_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=requirements_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 2: YÊU CẦU #####")
    requirements_quality_crew.kickoff()
    print("##### KẾT THÚC KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 2: YÊU CẦU #####\n")

    # Giai đoạn 3: Thiết kế (Design)
    design_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[3:4]
    design_research_crew = Crew(
        agents=[researcher_agent],
        tasks=design_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 3: THIẾT KẾ #####")
    design_research_crew.kickoff()
    print("##### KẾT THÚC NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 3: THIẾT KẾ #####\n")

    design_tasks = create_design_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, design_agent)
    design_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, design_agent],
        tasks=design_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 3: THIẾT KẾ #####")
    design_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 3: THIẾT KẾ #####\n")

    design_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[3:4]
    design_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=design_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 3: THIẾT KẾ #####")
    design_quality_crew.kickoff()
    print("##### KẾT THÚC KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 3: THIẾT KẾ #####\n")

    # Giai đoạn 4: Phát triển (Development)
    development_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[4:5]
    development_research_crew = Crew(
        agents=[researcher_agent],
        tasks=development_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 4: PHÁT TRIỂN #####")
    development_research_crew.kickoff()
    print("##### KẾT THÚC NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 4: PHÁT TRIỂN #####\n")

    development_tasks = create_development_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, development_agent)
    development_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, development_agent],
        tasks=development_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 4: PHÁT TRIỂN #####")
    development_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 4: PHÁT TRIỂN #####\n")

    development_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[4:5]
    development_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=development_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 4: PHÁT TRIỂN #####")
    development_quality_crew.kickoff()
    print("##### KẾT THÚC KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 4: PHÁT TRIỂN #####\n")

    # Giai đoạn 5: Kiểm thử (Testing)
    testing_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[5:6]
    testing_research_crew = Crew(
        agents=[researcher_agent],
        tasks=testing_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 5: KIỂM THỬ #####")
    testing_research_crew.kickoff()
    print("##### KẾT THÚC NGHIÊN C�ứU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 5: KIỂM THỬ #####\n")

    testing_tasks = create_testing_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, testing_agent)
    testing_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, testing_agent],
        tasks=testing_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 5: KIỂM THỬ #####")
    testing_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 5: KIỂM THỬ #####\n")

    testing_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[5:6]
    testing_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=testing_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 5: KIỂM THỬ #####")
    testing_quality_crew.kickoff()
    print("##### KẾT THÚC KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 5: KIỂM THỬ #####\n")

    # Giai đoạn 6: Triển khai (Deployment)
    deployment_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[6:7]
    deployment_research_crew = Crew(
        agents=[researcher_agent],
        tasks=deployment_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 6: TRIỂN KHAI #####")
    deployment_research_crew.kickoff()
    print("##### KẾT THÚC NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 6: TRIỂN KHAI #####\n")

    deployment_tasks = create_deployment_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, deployment_agent)
    deployment_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, deployment_agent],
        tasks=deployment_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 6: TRIỂN KHAI #####")
    deployment_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 6: TRIỂN KHAI #####\n")

    deployment_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[6:7]
    deployment_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=deployment_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 6: TRIỂN KHAI #####")
    deployment_quality_crew.kickoff()
    print("##### KẾT THÚC KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 6: TRIỂN KHAI #####\n")

    # Giai đoạn 7: Bảo trì (Maintenance)
    maintenance_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[7:8]
    maintenance_research_crew = Crew(
        agents=[researcher_agent],
        tasks=maintenance_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 7: BẢO TRÌ #####")
    maintenance_research_crew.kickoff()
    print("##### KẾT THÚC NGHIÊN CỨU PHƯƠNG PHÁP TỐT NHẤT - GIAI ĐOẠN 7: BẢO TRÌ #####\n")

    maintenance_tasks = create_maintenance_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, maintenance_agent)
    maintenance_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, maintenance_agent],
        tasks=maintenance_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 7: BẢO TRÌ #####")
    maintenance_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 7: BẢO TRÌ #####\n")

    maintenance_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[7:8]
    maintenance_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=maintenance_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 7: BẢO TRÌ #####")
    maintenance_quality_crew.kickoff()
    print("##### KẾT THÚC KIỂM TRA CHẤT LƯỢNG - GIAI ĐOẠN 7: BẢO TRÌ #####\n")

if __name__ == "__main__":
    main()
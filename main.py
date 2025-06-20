import os
from crewai import Crew, Process
from memory.shared_memory import SharedMemory

# Import agents for all phases
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

# Import tasks for all phases
from tasks.input_tasks import create_input_tasks
from tasks.initiation_tasks import create_initiation_tasks
from tasks.planning_tasks import create_planning_tasks
from tasks.requirement_tasks import create_requirements_tasks
from tasks.design_tasks import create_design_tasks
from tasks.development_tasks import create_development_tasks
from tasks.testing_tasks import create_testing_tasks
from tasks.deployment_tasks import create_deployment_tasks
from tasks.maintenance_tasks import create_maintenance_tasks

def main():
    INPUT_BASE_DIR = "input"
    OUTPUT_BASE_DIR = "output"
    shared_memory = SharedMemory()

    # Create agents
    input_agent = create_input_agent(INPUT_BASE_DIR)
    researcher_agent = create_researcher_agent(OUTPUT_BASE_DIR)
    project_manager_agent = create_project_manager_agent(OUTPUT_BASE_DIR)
    initiation_agent = create_initiation_agent(OUTPUT_BASE_DIR)
    planning_agent = create_planning_agent(OUTPUT_BASE_DIR)
    requirement_agent = create_requirement_agent(OUTPUT_BASE_DIR)
    design_agent = create_design_agent(OUTPUT_BASE_DIR)
    development_agent = create_development_agent(OUTPUT_BASE_DIR)
    testing_agent = create_testing_agent(OUTPUT_BASE_DIR)
    deployment_agent = create_deployment_agent(OUTPUT_BASE_DIR)
    maintenance_agent = create_maintenance_agent(OUTPUT_BASE_DIR)

    # ---

    ## Giai đoạn 0: Thu thập yêu cầu ban đầu (Input)
    # Đây là giai đoạn tương tác trực tiếp với người dùng để hiểu ý tưởng ban đầu
    input_tasks = create_input_tasks(shared_memory, INPUT_BASE_DIR, input_agent)
    input_crew = Crew(
        agents=[input_agent], # Chỉ cần Input Agent cho task này để đảm bảo tính tập trung
        tasks=input_tasks,
        process=Process.sequential,
        verbose=True # Nên để verbose=True ở đây để thấy tương tác của Agent
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 0: THU THẬP YÊU CẦU BAN ĐẦU #####")
    input_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 0: THU THẬP YÊU CẦU BAN ĐẦU #####\n")

    # Giai đoạn 1: Khởi tạo (Initiation)
    initiation_tasks = create_initiation_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, initiation_agent)
    initiation_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, initiation_agent],
        tasks=initiation_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 1: KHỞI TẠO #####")
    initiation_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 1: KHỞI TẠO #####\n")

    # Giai đoạn 2: Lập kế hoạch (Planning)
    planning_tasks = create_planning_tasks(shared_memory, OUTPUT_BASE_DIR, planning_agent) # Đảm bảo planning_agent được truyền vào nếu cần
    planning_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, planning_agent],
        tasks=planning_tasks,
        process=Process.sequential, # Thay thế bằng Process.sequential hoặc Process.hierarchical
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 2: LẬP KẾ HOẠCH #####")
    planning_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 2: LẬP KẾ HOẠCH #####\n")

    # Giai đoạn 3: Yêu cầu (Requirement)
    requirement_tasks = create_requirements_tasks(shared_memory, OUTPUT_BASE_DIR, requirement_agent) # Đảm bảo requirement_agent được truyền vào nếu cần
    requirement_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, requirement_agent],
        tasks=requirement_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 3: YÊU CẦU #####")
    requirement_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 3: YÊU CẦU #####\n")

    # Giai đoạn 4: Thiết kế (Design)
    design_tasks = create_design_tasks(shared_memory, OUTPUT_BASE_DIR, design_agent) # Đảm bảo design_agent được truyền vào nếu cần
    design_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, design_agent],
        tasks=design_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 4: THIẾT KẾ #####")
    design_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 4: THIẾT KẾ #####\n")

    # Giai đoạn 5: Phát triển (Development)
    development_tasks = create_development_tasks(shared_memory, OUTPUT_BASE_DIR, development_agent) # Đảm bảo development_agent được truyền vào nếu cần
    development_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, development_agent],
        tasks=development_tasks,
        process=Process.sequential, 
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 5: PHÁT TRIỂN #####")
    development_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 5: PHÁT TRIỂN #####\n")

    # Giai đoạn 6: Kiểm thử (Testing)
    testing_tasks = create_testing_tasks(shared_memory, OUTPUT_BASE_DIR, testing_agent) # Đảm bảo testing_agent được truyền vào nếu cần
    testing_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, testing_agent],
        tasks=testing_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 6: KIỂM THỬ #####")
    testing_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 6: KIỂM THỬ #####\n")

    # Giai đoạn 7: Triển khai (Deployment)
    deployment_tasks = create_deployment_tasks(shared_memory, OUTPUT_BASE_DIR, deployment_agent) # Đảm bảo deployment_agent được truyền vào nếu cần
    deployment_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, deployment_agent],
        tasks=deployment_tasks,
        process=Process.sequential, 
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 7: TRIỂN KHAI #####")
    deployment_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 7: TRIỂN KHAI #####\n")

    # Giai đoạn 8: Bảo trì (Maintenance)
    maintenance_tasks = create_maintenance_tasks(shared_memory, OUTPUT_BASE_DIR, maintenance_agent) # Đảm bảo maintenance_agent được truyền vào nếu cần
    maintenance_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, maintenance_agent],
        tasks=maintenance_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### BẮT ĐẦU GIAI ĐOẠN 8: BẢO TRÌ #####")
    maintenance_crew.kickoff()
    print("##### KẾT THÚC GIAI ĐOẠN 8: BẢO TRÌ #####\n")


if __name__ == "__main__":
    main()
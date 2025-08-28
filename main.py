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

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_agent(agent):
    """Validate agent configuration to ensure no errors."""
    try:
        if hasattr(agent, 'tools') and agent.tools:
            for tool in agent.tools:
                if not isinstance(tool, (type, object)) or not hasattr(tool, '__call__'):
                    raise ValueError(f"Invalid tool in agent {agent.role}: {tool}")
        logging.info(f"Agent {agent.role} validated successfully")
    except Exception as e:
        logging.error(f"Error validating agent {agent.role}: {e}")
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
        logging.error(f"Error creating agents: {e}")
        raise

    # Create output folders
    phases = [
        "0_initiation", "1_planning", "2_requirements", "3_design",
        "4_development", "5_testing", "6_deployment", "7_maintenance"
    ]
    for phase in phases:
        os.makedirs(os.path.join(OUTPUT_BASE_DIR, phase), exist_ok=True)

    # ✅ Pre-phase: Initial requirements collection
    try:
        logging.info("Starting initial requirements collection (pre-phase)")
        print("\n##### START PRE-PHASE: INITIAL REQUIREMENTS COLLECTION #####")
        run_input_collection_conversation(input_agent, INPUT_BASE_DIR, shared_memory)
        print("##### END PRE-PHASE: INITIAL REQUIREMENTS COLLECTION #####\n")
    except Exception as e:
        logging.error(f"Error during initial requirements collection: {e}", exc_info=True)
        raise

    # Phase 0: Initiation
    initiation_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[:1]
    initiation_research_crew = Crew(
        agents=[researcher_agent],
        tasks=initiation_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START BEST PRACTICE RESEARCH - PHASE 0: INITIATION #####")
    initiation_research_crew.kickoff()
    print("##### END BEST PRACTICE RESEARCH - PHASE 0: INITIATION #####\n")

    initiation_tasks = create_initiation_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, initiation_agent)
    initiation_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, initiation_agent],
        tasks=initiation_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START PHASE 0: INITIATION #####")
    initiation_crew.kickoff()
    print("##### END PHASE 0: INITIATION #####\n")

    initiation_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[:1]
    initiation_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=initiation_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START QUALITY CHECK - PHASE 0: INITIATION #####")
    initiation_quality_crew.kickoff()
    print("##### END QUALITY CHECK - PHASE 0: INITIATION #####\n")

    # Phase 1: Planning
    planning_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[1:2]
    planning_research_crew = Crew(
        agents=[researcher_agent],
        tasks=planning_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START BEST PRACTICE RESEARCH - PHASE 1: PLANNING #####")
    planning_research_crew.kickoff()
    print("##### END BEST PRACTICE RESEARCH - PHASE 1: PLANNING #####\n")

    planning_tasks = create_planning_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, planning_agent)
    planning_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, planning_agent],
        tasks=planning_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START PHASE 1: PLANNING #####")
    planning_crew.kickoff()
    print("##### END PHASE 1: PLANNING #####\n")

    planning_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[1:2]
    planning_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=planning_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START QUALITY CHECK - PHASE 1: PLANNING #####")
    planning_quality_crew.kickoff()
    print("##### END QUALITY CHECK - PHASE 1: PLANNING #####\n")

    # Phase 2: Requirements
    requirements_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[2:3]
    requirements_research_crew = Crew(
        agents=[researcher_agent],
        tasks=requirements_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START BEST PRACTICE RESEARCH - PHASE 2: REQUIREMENTS #####")
    requirements_research_crew.kickoff()
    print("##### END BEST PRACTICE RESEARCH - PHASE 2: REQUIREMENTS #####\n")

    requirements_tasks = create_requirements_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, requirement_agent)
    requirements_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, requirement_agent],
        tasks=requirements_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START PHASE 2: REQUIREMENTS #####")
    requirements_crew.kickoff()
    print("##### END PHASE 2: REQUIREMENTS #####\n")

    requirements_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[2:3]
    requirements_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=requirements_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START QUALITY CHECK - PHASE 2: REQUIREMENTS #####")
    requirements_quality_crew.kickoff()
    print("##### END QUALITY CHECK - PHASE 2: REQUIREMENTS #####\n")

    # Phase 3: Design
    design_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[3:4]
    design_research_crew = Crew(
        agents=[researcher_agent],
        tasks=design_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START BEST PRACTICE RESEARCH - PHASE 3: DESIGN #####")
    design_research_crew.kickoff()
    print("##### END BEST PRACTICE RESEARCH - PHASE 3: DESIGN #####\n")

    design_tasks = create_design_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, design_agent)
    design_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, design_agent],
        tasks=design_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START PHASE 3: DESIGN #####")
    design_crew.kickoff()
    print("##### END PHASE 3: DESIGN #####\n")

    design_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[3:4]
    design_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=design_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START QUALITY CHECK - PHASE 3: DESIGN #####")
    design_quality_crew.kickoff()
    print("##### END QUALITY CHECK - PHASE 3: DESIGN #####\n")

    # Phase 4: Development
    development_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[4:5]
    development_research_crew = Crew(
        agents=[researcher_agent],
        tasks=development_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START BEST PRACTICE RESEARCH - PHASE 4: DEVELOPMENT #####")
    development_research_crew.kickoff()
    print("##### END BEST PRACTICE RESEARCH - PHASE 4: DEVELOPMENT #####\n")

    development_tasks = create_development_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, development_agent)
    development_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, development_agent],
        tasks=development_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START PHASE 4: DEVELOPMENT #####")
    development_crew.kickoff()
    print("##### END PHASE 4: DEVELOPMENT #####\n")

    development_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[4:5]
    development_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=development_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START QUALITY CHECK - PHASE 4: DEVELOPMENT #####")
    development_quality_crew.kickoff()
    print("##### END QUALITY CHECK - PHASE 4: DEVELOPMENT #####\n")

    # Phase 5: Testing
    testing_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[5:6]
    testing_research_crew = Crew(
        agents=[researcher_agent],
        tasks=testing_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START BEST PRACTICE RESEARCH - PHASE 5: TESTING #####")
    testing_research_crew.kickoff()
    print("##### END BEST PRACTICE RESEARCH - PHASE 5: TESTING #####\n")

    testing_tasks = create_testing_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, testing_agent)
    testing_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, testing_agent],
        tasks=testing_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START PHASE 5: TESTING #####")
    testing_crew.kickoff()
    print("##### END PHASE 5: TESTING #####\n")

    testing_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[5:6]
    testing_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=testing_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START QUALITY CHECK - PHASE 5: TESTING #####")
    testing_quality_crew.kickoff()
    print("##### END QUALITY CHECK - PHASE 5: TESTING #####\n")

    # Phase 6: Deployment
    deployment_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[6:7]
    deployment_research_crew = Crew(
        agents=[researcher_agent],
        tasks=deployment_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START BEST PRACTICE RESEARCH - PHASE 6: DEPLOYMENT #####")
    deployment_research_crew.kickoff()
    print("##### END BEST PRACTICE RESEARCH - PHASE 6: DEPLOYMENT #####\n")

    deployment_tasks = create_deployment_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, deployment_agent)
    deployment_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, deployment_agent],
        tasks=deployment_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START PHASE 6: DEPLOYMENT #####")
    deployment_crew.kickoff()
    print("##### END PHASE 6: DEPLOYMENT #####\n")

    deployment_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[6:7]
    deployment_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=deployment_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START QUALITY CHECK - PHASE 6: DEPLOYMENT #####")
    deployment_quality_crew.kickoff()
    print("##### END QUALITY CHECK - PHASE 6: DEPLOYMENT #####\n")

    # Phase 7: Maintenance
    maintenance_research_tasks = create_research_tasks(shared_memory, OUTPUT_BASE_DIR, researcher_agent)[7:8]
    maintenance_research_crew = Crew(
        agents=[researcher_agent],
        tasks=maintenance_research_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START BEST PRACTICE RESEARCH - PHASE 7: MAINTENANCE #####")
    maintenance_research_crew.kickoff()
    print("##### END BEST PRACTICE RESEARCH - PHASE 7: MAINTENANCE #####\n")

    maintenance_tasks = create_maintenance_tasks(shared_memory, OUTPUT_BASE_DIR, input_agent, researcher_agent, project_manager_agent, maintenance_agent)
    maintenance_crew = Crew(
        agents=[input_agent, researcher_agent, project_manager_agent, maintenance_agent],
        tasks=maintenance_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START PHASE 7: MAINTENANCE #####")
    maintenance_crew.kickoff()
    print("##### END PHASE 7: MAINTENANCE #####\n")

    maintenance_quality_tasks = create_quality_gate_tasks(shared_memory, OUTPUT_BASE_DIR, project_manager_agent)[7:8]
    maintenance_quality_crew = Crew(
        agents=[project_manager_agent],
        tasks=maintenance_quality_tasks,
        process=Process.sequential,
        verbose=True
    )
    print("\n##### START QUALITY CHECK - PHASE 7: MAINTENANCE #####")
    maintenance_quality_crew.kickoff()
    print("##### END QUALITY CHECK - PHASE 7: MAINTENANCE #####\n")

if __name__ == "__main__":
    main()
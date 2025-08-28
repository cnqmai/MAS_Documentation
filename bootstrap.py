import os

def create_project_structure():
    # Define directory structure
    directories = [
        "agents",
        "tasks",
        "input",
        "output/0_initiation",
        "output/1_planning",
        "output/2_requirements",
        "output/3_design",
        "output/4_development",
        "output/5_testing",
        "output/6_deployment",
        "output/7_maintenance",
        "memory",
        "utils"
    ]

    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # List of files and sample content
    files = {
        "agents/input_agent.py": "# Agent for initial requirements gathering\n",
        "agents/researcher_agent.py": "# Agent for research and best practice consulting\n",
        "agents/project_manager_agent.py": "# Agent for project management and document quality check\n",
        "agents/initiation_agents.py": "# Agent for initiation phase (Phase 0)\n",
        "agents/planning_agents.py": "# Agent for planning phase (Phase 1)\n",
        "agents/requirement_agents.py": "# Agent for requirements phase (Phase 2)\n",
        "agents/design_agents.py": "# Agent for design phase (Phase 3)\n",
        "agents/development_agents.py": "# Agent for development phase (Phase 4)\n",
        "agents/testing_agents.py": "# Agent for testing phase (Phase 5)\n",
        "agents/deployment_agents.py": "# Agent for deployment phase (Phase 6)\n",
        "agents/maintenance_agents.py": "# Agent for maintenance phase (Phase 7)\n",
        "tasks/input_tasks.py": "# Tasks for initial requirements gathering phase (Pre-phase)\n",
        "tasks/initiation_tasks.py": "# Tasks for initiation phase (Phase 0)\n",
        "tasks/planning_tasks.py": "# Tasks for planning phase (Phase 1)\n",
        "tasks/requirement_tasks.py": "# Tasks for requirements phase (Phase 2)\n",
        "tasks/design_tasks.py": "# Tasks for design phase (Phase 3)\n",
        "tasks/development_tasks.py": "# Tasks for development phase (Phase 4)\n",
        "tasks/testing_tasks.py": "# Tasks for testing phase (Phase 5)\n",
        "tasks/deployment_tasks.py": "# Tasks for deployment phase (Phase 6)\n",
        "tasks/maintenance_tasks.py": "# Tasks for maintenance phase (Phase 7)\n",
        "tasks/quality_gate_tasks.py": "# Quality gate tasks for all phases\n",
        "tasks/research_tasks.py": "# Research tasks for best practices for all phases\n",
        "input/system_request_summary.docx": "",  # Empty file
        "memory/shared_memory.py": "# Shared memory class\n",
        "utils/output_formats.py": "# Output formatting functions (docx, xlsx, etc.)\n",
        "main.py": "# Main file to orchestrate and run the project\n",
        "requirements.txt": """# Core dependencies
            crewai==0.130.0
            crewai-tools==0.46.0
            chromadb==0.5.23
            embedchain==0.1.128
            langchain-community>=0.3.1
            langchain-core==0.3.62
            pydantic==2.8.0
            langsmith==0.3.18

            # Utilities
            python-dotenv==1.0.1
            unidecode==1.3.8

            # Document & Data processing
            python-docx==1.1.0
            python-pptx==0.6.23
            openpyxl==3.1.5
            PyYAML==6.0.1
            jinja2==3.1.4
            graphviz==0.20.3
            pandas

            # Logging
            loguru==0.7.2
            tenacity==8.3.0
            """
    }

    # Create files
    for file_path, content in files.items():
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

if __name__ == "__main__":
    create_project_structure()
    print("Project structure created successfully!")
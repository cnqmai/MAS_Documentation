import os

def create_project_structure():
    # Định nghĩa cấu trúc thư mục
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

    # Tạo các thư mục
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    # Danh sách các file và nội dung mẫu
    files = {
        "agents/input_agent.py": "# Agent để thu thập yêu cầu ban đầu\n",
        "agents/researcher_agent.py": "# Agent để nghiên cứu và tư vấn phương pháp tốt nhất\n",
        "agents/project_manager_agent.py": "# Agent để quản lý dự án và kiểm tra chất lượng tài liệu\n",
        "agents/initiation_agents.py": "# Agent cho giai đoạn khởi tạo (Phase 0)\n",
        "agents/planning_agents.py": "# Agent cho giai đoạn lập kế hoạch (Phase 1)\n",
        "agents/requirement_agents.py": "# Agent cho giai đoạn yêu cầu (Phase 2)\n",
        "agents/design_agents.py": "# Agent cho giai đoạn thiết kế (Phase 3)\n",
        "agents/development_agents.py": "# Agent cho giai đoạn phát triển (Phase 4)\n",
        "agents/testing_agents.py": "# Agent cho giai đoạn kiểm thử (Phase 5)\n",
        "agents/deployment_agents.py": "# Agent cho giai đoạn triển khai (Phase 6)\n",
        "agents/maintenance_agents.py": "# Agent cho giai đoạn bảo trì (Phase 7)\n",
        "tasks/input_tasks.py": "# Tác vụ cho giai đoạn thu thập yêu cầu ban đầu (Pre-phase)\n",
        "tasks/initiation_tasks.py": "# Tác vụ cho giai đoạn khởi tạo (Phase 0)\n",
        "tasks/planning_tasks.py": "# Tác vụ cho giai đoạn lập kế hoạch (Phase 1)\n",
        "tasks/requirement_tasks.py": "# Tác vụ cho giai đoạn yêu cầu (Phase 2)\n",
        "tasks/design_tasks.py": "# Tác vụ cho giai đoạn thiết kế (Phase 3)\n",
        "tasks/development_tasks.py": "# Tác vụ cho giai đoạn phát triển (Phase 4)\n",
        "tasks/testing_tasks.py": "# Tác vụ cho giai đoạn kiểm thử (Phase 5)\n",
        "tasks/deployment_tasks.py": "# Tác vụ cho giai đoạn triển khai (Phase 6)\n",
        "tasks/maintenance_tasks.py": "# Tác vụ cho giai đoạn bảo trì (Phase 7)\n",
        "tasks/quality_gate_tasks.py": "# Tác vụ kiểm tra chất lượng cho tất cả các giai đoạn\n",
        "tasks/research_tasks.py": "# Tác vụ nghiên cứu phương pháp tốt nhất cho tất cả các giai đoạn\n",
        "input/system_request_summary.docx": "",  # File rỗng
        "memory/shared_memory.py": "# Lớp bộ nhớ dùng chung\n",
        "utils/output_formats.py": "# Hàm định dạng đầu ra (docx, xlsx, v.v.)\n",
        "main.py": "# File chính để điều phối và chạy dự án\n",
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

    # Tạo các file
    for file_path, content in files.items():
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

if __name__ == "__main__":
    create_project_structure()
    print("Cấu trúc dự án đã được tạo thành công!")
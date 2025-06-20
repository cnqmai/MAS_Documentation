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
        "agents/input_agent.py": "# Agent để thu thập yêu cầu\n",
        "agents/researcher_agent.py": "# Agent để nghiên cứu và tư vấn\n",
        "agents/project_manager_agent.py": "# Agent để quản lý và xác thực tài liệu\n",
        "agents/initiation_agents.py": "# Agent cho giai đoạn khởi tạo\n",
        "agents/planning_agents.py": "# Agent cho giai đoạn lập kế hoạch\n",
        "agents/requirement_agents.py": "# Agent cho giai đoạn yêu cầu\n",
        "agents/design_agents.py": "# Agent cho giai đoạn thiết kế\n",
        "agents/development_agents.py": "# Agent cho giai đoạn phát triển\n",
        "agents/testing_agents.py": "# Agent cho giai đoạn kiểm thử\n",
        "agents/deployment_agents.py": "# Agent cho giai đoạn triển khai\n",
        "agents/maintenance_agents.py": "# Agent cho giai đoạn bảo trì\n",
        "tasks/initiation_tasks.py": "# Tác vụ cho giai đoạn khởi tạo\n",
        "tasks/planning_tasks.py": "# Tác vụ cho giai đoạn lập kế hoạch\n",
        "tasks/requirement_tasks.py": "# Tác vụ cho giai đoạn yêu cầu\n",
        "tasks/design_tasks.py": "# Tác vụ cho giai đoạn thiết kế\n",
        "tasks/development_tasks.py": "# Tác vụ cho giai đoạn phát triển\n",
        "tasks/testing_tasks.py": "# Tác vụ cho giai đoạn kiểm thử\n",
        "tasks/deployment_tasks.py": "# Tác vụ cho giai đoạn triển khai\n",
        "tasks/maintenance_tasks.py": "# Tác vụ cho giai đoạn bảo trì\n",
        "input/system_request_summary.docx": "",  # File rỗng
        "memory/shared_memory.py": "# Lớp bộ nhớ dùng chung\n",
        "utils/output_formats.py": "# Hàm định dạng đầu ra\n",
        "main.py": "# File chính để chạy dự án\n",
        "requirements.txt": "\ncrewai\npython-docx\nopenpyxl\npandas\n"
    }

    # Tạo các file
    for file_path, content in files.items():
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

if __name__ == "__main__":
    create_project_structure()
    print("Cấu trúc dự án đã được tạo thành công!")
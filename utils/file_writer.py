# utils/file_writer.py

import os

def write_output(file_path: str, content: str):
    """Ghi nội dung vào một file, tạo thư mục nếu chưa tồn tại."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Đã ghi output vào: {file_path}")
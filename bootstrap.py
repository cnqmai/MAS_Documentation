# bootstrap.py

import os
import logging
from dotenv import load_dotenv

# Cấu hình logging cơ bản cho file bootstrap
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_environment():
    """
    Khởi tạo môi trường:
    - Tải biến môi trường từ .env.
    - Đảm bảo các thư mục output và input tồn tại.
    """
    logging.info("Đang khởi tạo môi trường...")

    # Tải biến môi trường từ .env file
    load_dotenv()
    logging.info("Đã tải biến môi trường từ .env")

    # Đảm bảo thư mục output và input tồn tại
    output_base_dir = "output"
    os.makedirs(output_base_dir, exist_ok=True)
    logging.info(f"Đã tạo thư mục output: {output_base_dir}")

    input_base_dir = "input"
    os.makedirs(input_base_dir, exist_ok=True)
    logging.info(f"Đã tạo thư mục input: {input_base_dir}")

    # Kiểm tra GEMINI_API_KEY
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        logging.error("Lỗi: Biến môi trường GEMINI_API_KEY chưa được đặt trong file .env")
        return False # Trả về False nếu không tìm thấy key
    else:
        logging.info("GEMINI_API_KEY đã được tải.")
        return True # Trả về True nếu key tồn tại
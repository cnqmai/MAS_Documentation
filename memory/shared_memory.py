import threading
import logging

class SharedMemory:
    _data = {}  
    _lock = threading.Lock()

    def __init__(self):
        logging.info("Khởi tạo SharedMemory")

    def save(self, key, value):
        with self._lock:
            self.__class__._data[key] = value
            logging.info(f"✅ Đã lưu dữ liệu với khóa: {key}")

    def load(self, key):
        with self._lock:
            value = self.__class__._data.get(key)
            if value is not None:
                logging.info(f"✅ Đã truy xuất dữ liệu với khóa: {key}")
            else:
                logging.warning(f"⚠️ Không tìm thấy dữ liệu với khóa: {key}")
            return value

    def clear(self):
        with self._lock:
            self.__class__._data.clear()
            logging.info("🧹 Đã xóa toàn bộ dữ liệu trong SharedMemory")

    def keys(self):
        with self._lock:
            keys = list(self.__class__._data.keys())
            logging.info("📋 Đã lấy danh sách các khóa")
            return keys

    set = save
    get = load

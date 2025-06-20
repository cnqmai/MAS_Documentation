import threading
import logging

class SharedMemory:
    def __init__(self):
        """
        Khởi tạo bộ nhớ dùng chung với khóa thread-safe.
        """
        self._data = {}
        self._lock = threading.Lock()
        logging.info("Khởi tạo SharedMemory")

    def save(self, key, value):
        """
        Lưu dữ liệu vào bộ nhớ với key được chỉ định.
        Args:
            key (str): Khóa để xác định dữ liệu.
            value: Giá trị cần lưu (có thể là str, dict, list, v.v.).
        """
        with self._lock:
            self._data[key] = value
            logging.info(f"Đã lưu dữ liệu với khóa: {key}")

    def load(self, key):
        """
        Truy xuất dữ liệu từ bộ nhớ theo key.
        Args:
            key (str): Khóa để lấy dữ liệu.
        Returns:
            Giá trị tương ứng hoặc None nếu không tìm thấy.
        """
        with self._lock:
            value = self._data.get(key)
            logging.info(f"Đã truy xuất dữ liệu với khóa: {key}")
            return value

    def clear(self):
        """
        Xóa tất cả dữ liệu trong bộ nhớ.
        """
        with self._lock:
            self._data.clear()
            logging.info("Đã xóa toàn bộ dữ liệu trong SharedMemory")

    def keys(self):
        """
        Lấy danh sách tất cả các khóa trong bộ nhớ.
        Returns:
            list: Danh sách các khóa.
        """
        with self._lock:
            keys = list(self._data.keys())
            logging.info("Đã lấy danh sách các khóa")
            return keys
        
    set = save
    get = load
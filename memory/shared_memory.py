# memory/shared_memory.py

class SharedMemory:
    """
    Lớp để quản lý bộ nhớ chia sẻ giữa các tác vụ và các phase.
    Cấu trúc: { 'phase_name': { 'key': value } }
    """
    def __init__(self):
        self._data = {}

    def set(self, phase_name: str, key: str, value):
        """
        Lưu trữ một giá trị vào bộ nhớ chia sẻ.
        """
        if phase_name not in self._data:
            self._data[phase_name] = {}
        self._data[phase_name][key] = value
        print(f"[SharedMemory] Đã lưu: Phase '{phase_name}', Key '{key}'")

    def get(self, phase_name: str, key: str):
        """
        Lấy một giá trị từ bộ nhớ chia sẻ.
        Trả về None nếu không tìm thấy.
        """
        if phase_name in self._data and key in self._data[phase_name]:
            return self._data[phase_name][key]
        print(f"[SharedMemory] Không tìm thấy: Phase '{phase_name}', Key '{key}'")
        return None

    def get_phase_data(self, phase_name: str):
        """
        Lấy tất cả dữ liệu cho một phase cụ thể.
        """
        return self._data.get(phase_name, {})

    def clear(self):
        """
        Xóa toàn bộ bộ nhớ.
        """
        self._data = {}
        print("[SharedMemory] Đã xóa toàn bộ bộ nhớ.")

# Khởi tạo một thể hiện toàn cục để sử dụng
shared_memory = SharedMemory()
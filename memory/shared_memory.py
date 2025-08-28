import threading
import logging

class SharedMemory:
    _data = {}  
    _lock = threading.Lock()

    def __init__(self):
        logging.info("Initializing SharedMemory")

    def save(self, key, value):
        with self._lock:
            self.__class__._data[key] = value
            logging.info(f"✅ Data saved with key: {key}")

    def load(self, key):
        with self._lock:
            value = self.__class__._data.get(key)
            if value is not None:
                logging.info(f"✅ Data retrieved with key: {key}")
            else:
                logging.warning(f"⚠️ No data found with key: {key}")
            return value

    def clear(self):
        with self._lock:
            self.__class__._data.clear()
            logging.info("🧹 All data cleared in SharedMemory")

    def keys(self):
        with self._lock:
            keys = list(self.__class__._data.keys())
            logging.info("📋 Retrieved list of keys")
            return keys

    set = save
    get = load

import os
import psutil


def get_memory_in_use_mb():
    # Get information about system memory
    memory_info = psutil.virtual_memory()
    used_memory_mb = memory_info.used / (1024**2)
    return used_memory_mb


def get_file_size(file_path):
    # Get the size of a file in bytes.
    return os.path.getsize(file_path)

import os
import shutil
import time
from pathlib import Path


def get_folder_size(path: str):
    bytes_size = sum(
        file.stat().st_size
        for file in Path(path).rglob('*')
    )
    mb_size = bytes_size / 1024 ** 2
    return round(mb_size, 2)


def get_chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i: i + size]


def create_dir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)

    os.mkdir(dir)


def time_exec():
    def wrapper(f):
        def inner(*a, **kw):
            start_time = time.monotonic()
            result = f(*a, **kw)
            finish_time = time.monotonic() - start_time
            print(f'Execution time of "{f.__name__}": {round(finish_time, 2)} s')
            return result

        return inner

    return wrapper

import os
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image
from tqdm import tqdm


def compress_images(
        images_paths: list[str],
        images_folder_path: str,
        compressed_images_folder_path: str
) -> None:
    if not os.path.exists(compressed_images_folder_path):
        os.mkdir(compressed_images_folder_path)

    for image_name in images_paths:
        image_path = os.path.join(images_folder_path, image_name)
        image = Image.open(image_path)
        width, height = image.size

        resized_image = image.resize((width // 2, height // 2))
        image_name = os.path.basename(image_path)

        image_path = os.path.join(compressed_images_folder_path, image_name)
        resized_image.save(image_path, optimize=True, quality=50)


def get_folder_size(path: str):
    bytes_size = sum(
        file.stat().st_size
        for file in Path(path).rglob('*')
    )
    mb_size = bytes_size / 1024 ** 2
    return round(mb_size, 2)


def chunk(items, size):
    for i in range(0, len(items), size):
        yield items[i: i + size]


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


current_path = os.getcwd()  # Path(__file__).parent.resolve()
images_folder_path = os.path.join(current_path, "images")
compressed_images_folder_path = os.path.join(current_path, 'compressed_images')
images_paths = os.listdir(images_folder_path)


@time_exec()
def run():
    progress_bar = tqdm(total=len(images_paths))

    for image_path in images_paths:
        compress_images([image_path], images_folder_path, compressed_images_folder_path)
        progress_bar.update(1)

    print(f"Before compression: {get_folder_size(images_folder_path)} MB")
    print(f"After compression: {get_folder_size(compressed_images_folder_path)} MB")


@time_exec()
def run_multiprocessing():
    chunks_count = len(images_paths) // 8 + 8

    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(compress_images, image_chunk, images_folder_path, compressed_images_folder_path)
            for image_chunk in chunk(images_paths, chunks_count)
        ]

        while not all([f.done() for f in futures]):
            pass

    print(f"Before compression: {get_folder_size(images_folder_path)} MB")
    print(f"After compression: {get_folder_size(compressed_images_folder_path)} MB")


if __name__ == "__main__":
    run()
    print("")
    run_multiprocessing()

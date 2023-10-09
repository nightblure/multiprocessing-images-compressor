import os
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Lock, Value, Manager

from PIL import Image
from tqdm import tqdm

from utils import time_exec, get_folder_size, get_chunks, create_dir


def compress_images(
        images_paths: list[str],
        images_folder_path: str,
        compressed_images_folder_path: str,
        progress_counter: Value = None,
        lock: Lock = None
) -> None:
    for image_name in images_paths:
        image_path = os.path.join(images_folder_path, image_name)
        image = Image.open(image_path)
        width, height = image.size

        resized_image = image.resize((width // 2, height // 2))
        image_name = os.path.basename(image_path)

        image_path = os.path.join(compressed_images_folder_path, image_name)
        resized_image.save(image_path, optimize=True, quality=50)

        if lock is not None:
            with lock:
                progress_counter.value += 1


@time_exec()
def run():
    create_dir(compressed_images_folder_path)

    for chunk in get_chunks(image_names, 10):
        compress_images(chunk, images_folder_path, compressed_images_folder_path)
        progress_bar.update(len(chunk))

    print(f"Before compression: {get_folder_size(images_folder_path)} MB")
    print(f"After compression: {get_folder_size(compressed_images_folder_path)} MB")


@time_exec()
def run_multiprocessing():
    create_dir(compressed_images_folder_path)
    workers = os.cpu_count()
    chunks_count = len(image_names) // workers

    manager = Manager()
    lock = manager.Lock()
    counter = manager.Value(int, 0, lock=lock)  # value that shared between all processes

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                compress_images, image_chunk, images_folder_path, compressed_images_folder_path, counter, lock
            )
            for image_chunk in get_chunks(image_names, chunks_count)
        ]

        while not all([f.done() for f in futures]):
            progress_bar.update(counter.value - progress_bar.n)

    print(f"Before compression: {get_folder_size(images_folder_path)} MB")
    print(f"After compression: {get_folder_size(compressed_images_folder_path)} MB")


current_path = os.getcwd()  # Path(__file__).parent.resolve()
images_folder_path = os.path.join(current_path, "images")
compressed_images_folder_path = os.path.join(current_path, 'compressed_images')
image_names = os.listdir(images_folder_path)
progress_bar = tqdm(total=len(image_names))

if __name__ == "__main__":
    run()
    print("")
    progress_bar.update(0)
    run_multiprocessing()

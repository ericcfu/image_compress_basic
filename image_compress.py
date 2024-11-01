import pathlib
from PIL import Image
import os
import shutil
from pillow_heif import register_heif_opener

#########################################
#
# This python script is a basic script that downsizes images until they are smaller than a certain target size
#
#########################################

image_path = "INPUT DIR HERE"
output_path = "OUTPUT DIR HERE"
STEP_SIZE = 5
TARGET_SIZE = 1048576 # 1MB in bytes

def compress_image(image_path: str, output_path: str, target_size: int = TARGET_SIZE) -> bool:
    """
    Compress an image to a target size.

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the compressed image.
        target_size (int): Target size in bytes. Defaults to 1048576 (1MB).
    """
    output_path = output_path.replace('.png', '.jpg')
    print(f"trying to compress image: {image_path}")
    image = Image.open(image_path)
    image = image.convert('RGB')

    # Get initial image size
    initial_size = os.path.getsize(image_path)
    print(f"filepath: {image_path}, Initial size: {initial_size} bytes")
    if initial_size < target_size:
        print(f"filepath: {image_path} file size: {initial_size} already less than target size: {target_size}")
        shutil.copy(image_path, output_path)
        return False

    # Compress image
    quality = 100
    while True:
        image.save(output_path, optimize=True, quality=quality)
        compressed_size = os.path.getsize(output_path)
        print(f"one iteration done, compressed_size {compressed_size}, quality {quality}")
        
        if compressed_size <= target_size:
            print(f"filepath: {image_path} new file size: {compressed_size} compressed from old size: {initial_size}")
            return True

        if quality < 60:
            print("quality has reached 60, move towards downsizing")
            break

        quality -= STEP_SIZE

    scaling_factor = 0.95
    while True:
        downsized_img = image.resize((int(image.width * scaling_factor), int(image.height * scaling_factor)))
        downsized_img.save(output_path, optimize=True, quality=quality)
        compressed_size = os.path.getsize(output_path)
        print(f"one iteration done, compressed_size {compressed_size}, quality {quality}")

        if compressed_size <= target_size:
            print(f"filepath: {image_path} new file size: {compressed_size} compressed from old size: {initial_size}")
            return True
        
        scaling_factor -= 0.05


def get_filenames(directory: str):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]


def compress_dir(input_dir: str, output_dir: str):
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    filenames = get_filenames(input_dir)
    num_compressed = 0
    num_skipped = 0
    num_failed = 0
    for filename in filenames:
        try:
            compressed = compress_image('/'.join([input_dir, filename]), '/'.join([output_dir, filename]))
            if compressed:
                num_compressed += 1
            else:
                num_skipped += 1
        except Exception as e:
            print(f"UNABLE TO COMPRESS IMAGE {'/'.join([input_dir, filename])} with exception: {e}")
            num_failed += 1
    
    print(f"Stats: num_compressed: {num_compressed} num_skipped: {num_skipped} num_failed: {num_failed}")


register_heif_opener()
compress_dir(image_path, output_path)
import glob
import os

VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif')

def scan_folders(folders):
    image_paths = []
    for folder in folders:
        found = glob.glob(os.path.join(os.path.expanduser(folder), '**', '*.*'), recursive=True)
        image_paths.extend([p for p in found if p.lower().endswith(VALID_EXTENSIONS)])
    image_paths.sort(key=lambda p: os.path.getmtime(p))
    return image_paths

from scanner import scan_folders
from viewer import PicbinViewer

def main():
    print("Welcome to picbin!")
    print("Example: Pictures Downloads Desktop")
    input_folders = input("Enter folders (space separated): ").strip().split()

    if not input_folders:
        print("No folders provided. Exiting.")
        return

    print("Scanning...")
    image_paths = scan_folders([f"~/{f.strip()}" for f in input_folders])

    if not image_paths:
        print("No images found.")
        return

    viewer = PicbinViewer(image_paths)
    viewer.launch()

if __name__ == "__main__":
    main()

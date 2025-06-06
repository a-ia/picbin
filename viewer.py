import dearpygui.dearpygui as dpg
from PIL import Image
import os
import time
import random

class PicbinViewer:
    def __init__(self, image_paths):
        self.all_image_paths = image_paths
        self.image_paths = image_paths
        self.index = 0
        self.current_texture = None
        self.image_widget_tag = "ImagePlaceholder"
        self.header_text_id = None
        self.path_text_id = None
        self.size_text_id = None
        self.current_filter = "All Images"
        self.sort_ascending = True

    def launch(self):
        dpg.create_context()
        dpg.create_viewport(title="picbin", width=250, height=720)
        
        with dpg.window(tag="MainWindow"):
            self.header_text_id = dpg.add_text("Loading...", tag="Header")
            dpg.add_spacer(height=10)
            
            with dpg.group(horizontal=True):
                dpg.add_button(label="< Prev", callback=self.prev_image)
                dpg.add_button(label="Next >", callback=self.next_image)
                dpg.add_button(label="Delete X", callback=self.delete_image)
                dpg.add_button(label="Shuffle ~", callback=self.shuffle_images)
                dpg.add_button(label="Reorder", callback=self.reorder_images)
                dpg.add_button(label="Date Directory", callback=self.show_date_picker)
            
            dpg.add_spacer(height=10)
            self.path_text_id = dpg.add_text("", tag="PathText", wrap=800)
            self.size_text_id = dpg.add_text("", tag="SizeText", wrap=800)
            dpg.add_spacer(height=5)
            
        with dpg.handler_registry():
            dpg.add_key_press_handler(callback=self.key_callback)

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("MainWindow", True)
        
        self.show_image()
        dpg.start_dearpygui()
        dpg.destroy_context()

    def show_image(self):
        if not self.image_paths:
            dpg.set_value(self.header_text_id, "No images found.")
            return

        img_path = os.path.expanduser(self.image_paths[self.index])
        
        try:
            # Load and process image
            image = Image.open(img_path).convert("RGBA")
            image.thumbnail((800, 600), Image.Resampling.LANCZOS)
            width, height = image.size
            
            # Convert image data to the format DearPyGui expects
            image_data = []
            for pixel in image.getdata():
                image_data.extend([pixel[0]/255.0, pixel[1]/255.0, pixel[2]/255.0, pixel[3]/255.0])

            # Clean up previous texture if it exists
            if self.current_texture and dpg.does_item_exist(self.current_texture):
                dpg.delete_item(self.current_texture)
            
            # Remove existing image widget if it exists
            if dpg.does_item_exist(self.image_widget_tag):
                dpg.delete_item(self.image_widget_tag)

            # Create new texture with unique tag
            texture_tag = f"texture_{self.index}_{int(time.time())}"
            
            # Create static texture in texture registry for the image widget to avoid flickering
            with dpg.texture_registry():
                dpg.add_static_texture(width, height, image_data, tag=texture_tag)
            
            # Add new image widget
            dpg.add_image(texture_tag, tag=self.image_widget_tag, parent="MainWindow")
            
            # Update the path text
            dpg.set_value("PathText", f"Path: {img_path}")
            
            # Get and format file size
            file_size_bytes = os.path.getsize(img_path)
            file_size_str = self.format_file_size(file_size_bytes)
            dpg.set_value("SizeText", f"Size: {file_size_str}")
            
            self.current_texture = texture_tag

            # Update header with image info
            date_str = time.strftime('%Y-%m-%d', time.localtime(os.path.getmtime(img_path)))
            filename = os.path.basename(img_path)
            header = f"{date_str} | {filename} | [{self.index + 1}/{len(self.image_paths)}] | {self.current_filter}"
            dpg.set_value(self.header_text_id, header)
            
        except Exception as e:
            error_msg = f"Error loading image: {str(e)}"
            dpg.set_value(self.header_text_id, error_msg)
            dpg.set_value("SizeText", "")
            print(f"Error loading {img_path}: {e}")

    def next_image(self, *args):
        if self.index < len(self.image_paths) - 1:
            self.index += 1
            self.show_image()

    def prev_image(self, *args):
        if self.index > 0:
            self.index -= 1
            self.show_image()

    def delete_image(self, *args):
        if self.image_paths:
            img_path = os.path.expanduser(self.image_paths[self.index])
            try:
                os.remove(img_path)
                print(f"Deleted: {img_path}")
            except Exception as e:
                print(f"Error deleting file: {e}")
                return
            
            self.image_paths.pop(self.index)
            if not self.image_paths:
                dpg.set_value(self.header_text_id, "No more images.")
                dpg.set_value("SizeText", "")
                if dpg.does_item_exist(self.image_widget_tag):
                    dpg.delete_item(self.image_widget_tag)
                return
                
            if self.index >= len(self.image_paths):
                self.index = len(self.image_paths) - 1
            self.show_image()

    def shuffle_images(self, *args):
        if self.image_paths:
            random.shuffle(self.image_paths)
            self.index = 0
            self.show_image()

    def key_callback(self, sender, key):
        if key == dpg.mvKey_Right or key == ord('k') or key == ord('K'):
            self.next_image()
        elif key == dpg.mvKey_Left or key == ord('h') or key == ord('H'):
            self.prev_image()
        elif key == ord('d') or key == ord('D'):
            self.delete_image()
        elif key == ord('r') or key == ord('R'):
            self.shuffle_images()
        elif key == ord('o') or key == ord('O'):
            self.reorder_images()
        elif key == dpg.mvKey_Escape:
            dpg.stop_dearpygui()

    def show_date_picker(self, *args):
        # Get the unique year-month combinations from all images
        months = {}
        for img_path in self.all_image_paths:
            try:
                expanded_path = os.path.expanduser(img_path)
                if os.path.exists(expanded_path):
                    mtime = os.path.getmtime(expanded_path)
                    year_month = time.strftime('%Y-%m', time.localtime(mtime))
                    month_name = time.strftime('%Y %B', time.localtime(mtime))
                    if year_month not in months:
                        months[year_month] = month_name
            except:
                continue
        
        # Sort months
        sorted_months = sorted(months.items())
        
        if not sorted_months:
            return
            
        # Date Directory popup window
        if dpg.does_item_exist("date_picker_window"):
            dpg.delete_item("date_picker_window")
            
        with dpg.window(label="Select Month", modal=True, tag="date_picker_window", 
                       width=300, height=400, pos=[8, 137]):
            dpg.add_text("Choose a month:")
            dpg.add_separator()
            
            # All Images option
            dpg.add_button(label=f"All Images ({len(self.all_image_paths)} photos)", 
                          callback=self.create_all_callback(), width=280)
            dpg.add_separator()
            
            # Month buttons
            for year_month, month_name in sorted_months:
                count = sum(1 for img_path in self.all_image_paths 
                           if self.get_image_month(img_path) == year_month)
                dpg.add_button(label=f"{month_name} ({count} photos)", 
                              callback=self.create_month_callback(year_month), 
                              width=280)
            
            dpg.add_separator()
            dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("date_picker_window"))

    def get_image_month(self, img_path):
        try:
            expanded_path = os.path.expanduser(img_path)
            if os.path.exists(expanded_path):
                mtime = os.path.getmtime(expanded_path)
                return time.strftime('%Y-%m', time.localtime(mtime))
        except:
            pass
        return None

    def filter_by_month(self, target_month):
        if target_month is None:
            # Show all images
            self.image_paths = self.all_image_paths.copy()
            self.current_filter = "All Images"
        else:
            # Filter by month
            self.image_paths = []
            for img_path in self.all_image_paths:
                if self.get_image_month(img_path) == target_month:
                    self.image_paths.append(img_path)
            
            # Format date string
            sample_time = time.strptime(f"{target_month}-01", '%Y-%m-%d')
            self.current_filter = time.strftime('%Y %B', sample_time)

        # Show helpful output log about the filter
        print(f"Filtered to {len(self.image_paths)} images for {self.current_filter}")
        
        # Reset index and show first image
        self.index = 0
        if self.image_paths:
            self.show_image()
        else:
            dpg.set_value(self.header_text_id, f"No images found for {self.current_filter}")
            dpg.set_value("SizeText", "")
            if dpg.does_item_exist(self.image_widget_tag):
                dpg.delete_item(self.image_widget_tag)
        
        # Close the picker window
        if dpg.does_item_exist("date_picker_window"):
            dpg.delete_item("date_picker_window")

    def create_month_callback(self, month_str):
        def callback(*args):
            self.filter_by_month(month_str)
        return callback
    
    def create_all_callback(self):
        def callback(*args):
            self.filter_by_month(None)
        return callback

    def reorder_images(self, *args):
        if not self.image_paths:
            return
        
        # Toggle sort order
        self.sort_ascending = not self.sort_ascending

        try:
            self.image_paths.sort(
                key=lambda img_path: os.path.getmtime(os.path.expanduser(img_path)),
                reverse=not self.sort_ascending
            )
            
            # Reset current position to the beginning index of the new order
            self.index = 0
            
            self.show_image()
            
            # Show helpful output log about sort order   
            order_text = "oldest to newest" if self.sort_ascending else "newest to oldest"
            print(f"Reordered images: {order_text}")
            
        except Exception as e:
            print(f"Error reordering images: {e}")

    def format_file_size(self, size_bytes):
        if size_bytes == 0:
            return "0 B"
        
        size_units = ['B', 'KB', 'MB', 'GB', 'TB']
        unit_index = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and unit_index < len(size_units) - 1:
            size /= 1024.0
            unit_index += 1
        
        if unit_index == 0:
            return f"{int(size)} {size_units[unit_index]}"
        else:
            return f"{size:.1f} {size_units[unit_index]}"
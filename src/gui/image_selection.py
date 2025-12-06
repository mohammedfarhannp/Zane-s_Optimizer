import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from PIL import Image, ImageTk

class ImageSelection:
    def __init__(self, parent_frame, update_callback=None):
        self.parent = parent_frame
        self.update_callback = update_callback  # Callback to update main window
        self.selected_images = []
        self.setup_image_selection_ui()
        
    def setup_image_selection_ui(self):
        # Setup the image selection interface
        # Main selection frame
        selection_frame = ttk.LabelFrame(self.parent, text="Image Selection", padding="10")
        selection_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        selection_frame.columnconfigure(1, weight=1)
        
        # Select images button
        self.select_btn = ttk.Button(selection_frame, text="Select Images", 
                                   command=self.select_images)
        self.select_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Selected images count label
        self.count_label = ttk.Label(selection_frame, text="No images selected")
        self.count_label.grid(row=0, column=1, sticky=tk.W)
        
        # Clear selection button
        self.clear_btn = ttk.Button(selection_frame, text="Clear All", 
                                  command=self.clear_images, state="disabled")
        self.clear_btn.grid(row=0, column=2, padx=(10, 0))
        
        # Image list frame (with scrollbar)
        list_frame = ttk.Frame(self.parent)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Create treeview for image list
        columns = ('filename', 'size', 'dimensions', 'path')
        self.image_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=6)
        
        # Define headings
        self.image_tree.heading('filename', text='Filename')
        self.image_tree.heading('size', text='Size')
        self.image_tree.heading('dimensions', text='Dimensions')
        self.image_tree.heading('path', text='Path')
        
        # Define columns
        self.image_tree.column('filename', width=150)
        self.image_tree.column('size', width=80)
        self.image_tree.column('dimensions', width=100)
        self.image_tree.column('path', width=200)
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.image_tree.yview)
        self.image_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Grid treeview and scrollbar
        self.image_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Remove button for individual images
        button_frame = ttk.Frame(self.parent)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        self.remove_btn = ttk.Button(button_frame, text="Remove Selected", 
                                   command=self.remove_selected_image, state="disabled")
        self.remove_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Bind treeview selection event
        self.image_tree.bind('<<TreeviewSelect>>', self.on_treeview_select)
        
    def select_images(self):
        # Open file dialog to select multiple images
        file_types = [
            ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.tif"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=file_types
        )
        
        if files:
            new_images = []
            unsupported_files = []
            oversized_files = []
            
            # Calculate max allowed size (A4 page with margins)
            # A4: 794x1123 pixels at 96 DPI
            max_width = 794 - (5 * 3.78 * 2)  # 5mm margins both sides
            max_height = 1123 - (5 * 3.78 * 2)
            
            a4_width_px = 794   # 210mm * 3.78
            a4_height_px = 1123 # 297mm * 3.78
            
            for file_path in files:
                if self.is_supported_image(file_path):
                    # Validate image size
                    is_valid, error_msg = self.validate_image_size(file_path, a4_width_px, a4_height_px)
                    if is_valid:
                        new_images.append(file_path)
                    else:
                        oversized_files.append(f"{os.path.basename(file_path)}: {error_msg}")
                else:
                    unsupported_files.append(os.path.basename(file_path))
            
            # Add new images to selection
            self.selected_images.extend(new_images)
            self.update_image_list()
            
            # Show warnings for problematic files
            all_warnings = []
            if unsupported_files:
                all_warnings.append(f"Unsupported format: {', '.join(unsupported_files[:3])}")
            if oversized_files:
                all_warnings.append(f"Too large: {', '.join(oversized_files[:3])}")
            
            if all_warnings:
                messagebox.showwarning(
                    "Some images were not added",
                    "\n".join(all_warnings) + 
                    f"\n\n{len(unsupported_files) + len(oversized_files)} file(s) skipped."
                )
            
            # Update callback if provided
            if self.update_callback:
                self.update_callback(self.selected_images)
    
    def clear_images(self):
        # Clear all selected images
        self.selected_images.clear()
        self.update_image_list()
        
        # Update callback if provided
        if self.update_callback:
            self.update_callback(self.selected_images)
    
    def remove_selected_image(self):
        # Remove the currently selected image from the list
        selection = self.image_tree.selection()
        if selection:
            # Get the index of selected item
            item = selection[0]
            index = self.image_tree.index(item)
            
            # Remove from selected images
            if 0 <= index < len(self.selected_images):
                self.selected_images.pop(index)
                self.update_image_list()
                
                # Update callback if provided
                if self.update_callback:
                    self.update_callback(self.selected_images)
    
    def on_treeview_select(self, event):
        # Enable/disable remove button based on selection 
        selection = self.image_tree.selection()
        if selection:
            self.remove_btn.config(state="normal")
        else:
            self.remove_btn.config(state="disabled")
    
    def update_image_list(self):
        # Update the treeview with current image list
        # Clear existing items
        for item in self.image_tree.get_children():
            self.image_tree.delete(item)
        
        # Add images to treeview
        for image_path in self.selected_images:
            try:
                # Get image info
                with Image.open(image_path) as img:
                    width, height = img.size
                    dimensions = f"{width}×{height}"
                
                # Get file size
                file_size = os.path.getsize(image_path)
                size_kb = file_size / 1024
                size_text = f"{size_kb:.1f} KB"
                
                # Get filename and path
                filename = os.path.basename(image_path)
                directory = os.path.dirname(image_path)
                
                # Add to treeview
                self.image_tree.insert('', 'end', values=(filename, size_text, dimensions, directory))
                
            except Exception as e:
                # If we can't read the image, still add it with error info
                filename = os.path.basename(image_path)
                self.image_tree.insert('', 'end', values=(filename, "Error", "N/A", "Cannot read image"))
        
        # Update count label and button states
        count = len(self.selected_images)
        if count == 0:
            self.count_label.config(text="No images selected")
            self.clear_btn.config(state="disabled")
            self.remove_btn.config(state="disabled")
        else:
            self.count_label.config(text=f"{count} image{'s' if count != 1 else ''} selected")
            self.clear_btn.config(state="normal")
    
    def is_supported_image(self, file_path):
        # Check if file is a supported image format
        supported_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif'}
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in supported_extensions
    
    def get_selected_images(self):
        # Return the list of selected image paths
        return self.selected_images.copy()
    
    def set_selected_images(self, image_paths):
        # Set the selected images list
        self.selected_images = image_paths.copy()
        self.update_image_list()
        
    def validate_image_size(self, file_path, max_width, max_height):
        # Simple validation using PIL
        try:
            from PIL import Image
            with Image.open(file_path) as img:
                width, height = img.size
                # Allow images up to 2x the max size (will be resized)
                if width > max_width or height > max_height:
                    return False, f"{width}x{height}px"
                return True, None
        except:
            return False, "Cannot read image"

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import math

class PreviewPanel:
    def __init__(self, parent_frame):
        self.parent = parent_frame
        self.canvas = None
        self.scrollbar_y = None
        self.scrollbar_x = None
        self.setup_preview_area()
        
        # Store page layouts and image references
        self.page_layouts = []
        self.photo_references = []  # Keep references to prevent garbage collection
        
    def setup_preview_area(self):
        # Setup the preview canvas with scrollbars
        # Create main frame for preview
        self.main_frame = ttk.Frame(self.parent)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(self.main_frame, bg='white', highlightthickness=1, highlightbackground='#cccccc')
        
        self.scrollbar_y = ttk.Scrollbar(self.main_frame, orient='vertical', command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self.main_frame, orient='horizontal', command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure weights for resizing
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        
    def clear_preview(self):
        # Clear the preview canvas
        if self.canvas:
            self.canvas.delete("all")
        self.photo_references.clear()
        self.page_layouts.clear()
        
    def show_layout_preview(self, page_layouts, scale_factor=0.2):
        
        ## Display page layouts in the preview panel
        ## scale_factor: Scale down factor for preview (0.2 = 20% of actual size)
        
        self.clear_preview()
        self.page_layouts = page_layouts
        
        if not page_layouts:
            self.canvas.create_text(200, 100, text="No layout to preview", 
                                  fill="gray", font=("Arial", 12))
            return
            
        # Calculate total preview height
        page_width_px = 794  # A4 width in pixels at 96 DPI
        page_height_px = 1123  # A4 height in pixels at 96 DPI
        
        preview_width = int(page_width_px * scale_factor)
        preview_height = int(page_height_px * scale_factor)
        page_spacing = 20  # Space between pages in preview
        
        current_y = 20  # Start position
        
        for page_num, page in enumerate(page_layouts, 1):
            # Draw page background
            page_x = 20
            page_y = current_y
            
            # Page border
            self.canvas.create_rectangle(
                page_x, page_y, 
                page_x + preview_width, 
                page_y + preview_height,
                outline='#666666', 
                fill='#f8f8f8',
                width=2
            )
            
            # Page number
            self.canvas.create_text(
                page_x + preview_width // 2, 
                page_y + preview_height + 10,
                text=f"Page {page_num}",
                font=("Arial", 10, "bold"),
                fill="#333333"
            )
            
            # Draw images on this page
            for img_data in page['images']:
                # Scale coordinates for preview
                img_x = page_x + int(img_data['x'] * scale_factor)
                img_y = page_y + int(img_data['y'] * scale_factor)
                img_width = int(img_data['width'] * scale_factor)
                img_height = int(img_data['height'] * scale_factor)
                
                # Draw image placeholder
                self.canvas.create_rectangle(
                    img_x, img_y,
                    img_x + img_width,
                    img_y + img_height,
                    outline='#0066cc',
                    fill='#e6f2ff',
                    width=1
                )
                
                # Draw diagonal lines for rotated images
                if img_data.get('rotated', False):
                    self.canvas.create_line(
                        img_x, img_y,
                        img_x + img_width, img_y + img_height,
                        fill='#ff6600', width=1, dash=(4, 2)
                    )
                    self.canvas.create_line(
                        img_x + img_width, img_y,
                        img_x, img_y + img_height,
                        fill='#ff6600', width=1, dash=(4, 2)
                    )
                
                # Image info text
                info_text = f"{img_width//3.78:.0f}x{img_height//3.78:.0f}mm"
                if img_data.get('rotated', False):
                    info_text += " ⭮"
                if img_data.get('resized', False):
                    info_text += " 📐"
                
                # Only show text if there's enough space
                if img_width > 50 and img_height > 30:
                    self.canvas.create_text(
                        img_x + img_width // 2,
                        img_y + img_height // 2,
                        text=info_text,
                        font=("Arial", 7),
                        fill="#333333",
                        width=img_width - 10
                    )
            
            current_y += preview_height + page_spacing + 30
        
        # Update scroll region
        total_height = current_y + 20
        self.canvas.configure(scrollregion=(0, 0, preview_width + 100, total_height))
        
        # Enable scrolling
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        # Handle mouse wheel scrolling
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def show_loading_message(self, message="Calculating layout..."):
        # Show loading message in preview
        self.clear_preview()
        self.canvas.create_text(200, 100, text=message, 
                              fill="gray", font=("Arial", 12))
    
    def show_error_message(self, message):
        # Show error message in preview
        self.clear_preview()
        self.canvas.create_text(200, 100, text=f"Error: {message}", 
                              fill="red", font=("Arial", 12))
    
    def show_image_selection(self, image_paths):
        # Show basic preview of selected images (before layout)
        self.clear_preview()
        
        if not image_paths:
            self.canvas.create_text(200, 100, text="No images selected", 
                                  fill="gray", font=("Arial", 12))
            return
            
        # Show simple list of selected images
        self.canvas.create_text(200, 30, text=f"Selected Images: {len(image_paths)}", 
                              fill="#333333", font=("Arial", 12, "bold"))
        
        current_y = 60
        for i, path in enumerate(image_paths[:10]):  # Show first 10
            filename = path.split('/')[-1] if '/' in path else path.split('\\')[-1]
            self.canvas.create_text(20, current_y, text=f"{i+1}. {filename}", 
                                  fill="#333333", font=("Arial", 9), anchor='w')
            current_y += 20
            
        if len(image_paths) > 10:
            self.canvas.create_text(20, current_y, text=f"... and {len(image_paths) - 10} more images", fill="#666666", font=("Arial", 9), anchor='w')
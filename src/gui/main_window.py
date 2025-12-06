import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import copy

# Add the src directory to Python path so we can import our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from gui.image_selection import ImageSelection
from gui.settings_panel import SettingsPanel
from gui.preview_panel import PreviewPanel
from layout.page_layout import PageLayout
from exporter.document_exporter import DocumentExporter

from PIL import Image, ImageTk

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Zane's Optimizer")
        self.root.geometry("1000x700")
        
        # Initialize modules
        self.page_layout = PageLayout()
        self.document_exporter = DocumentExporter()
        
        self.selected_images = []
        self.current_page_layouts = []
        
        self.setup_ui()
        self.set_window_icon()
        
    def setup_ui(self):
        # Set up main user interface #
        # Main Frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure Grid weights for resizing - TWO COLUMNS NOW
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=3)  # Preview gets 3 parts
        main_frame.columnconfigure(0, weight=1)  # Left side gets 1 part (25%)
        main_frame.rowconfigure(2, weight=1)     # Preview row gets weight
        
        # Title - spans both columns
        title_label = ttk.Label(main_frame, text="Zane's Optimizer", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Image Selection Section - spans both columns
        image_selection_frame = ttk.Frame(main_frame)
        image_selection_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        image_selection_frame.columnconfigure(0, weight=1)
        
        self.image_selection = ImageSelection(image_selection_frame, self.on_images_updated)
        self.image_selection.setup_image_selection_ui()
        
        # LEFT COLUMN: Settings Section
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        
        self.settings_panel = SettingsPanel(left_frame, self.on_settings_updated)
        self.settings_panel.setup_settings_ui()
        
        # RIGHT COLUMN: Preview area
        preview_frame = ttk.LabelFrame(main_frame, text="Preview", padding="10")
        preview_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        self.preview_panel = PreviewPanel(preview_frame)
        
        # Export button - spans both columns at bottom
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        button_frame.columnconfigure(0, weight=1)

        self.export_btn = ttk.Button(button_frame, text="Export PDF", command=self.export_document, state="disabled")
        self.export_btn.grid(row=0, column=0)
        
    def on_images_updated(self, images):
        # Callback when images are updated in ImageSelection component
        ### print(f"DEBUG: on_images_updated called with {len(images)} images")
        self.selected_images = images
        self.update_export_button()
        
        if images:
            # Show basic image selection preview
            self.preview_panel.show_image_selection(images)
            # Calculate and show layout preview
            self.calculate_layout_preview()
        else:
            ### print("DEBUG: Clearing preview and page layouts")
            self.preview_panel.clear_preview()
            self.current_page_layouts = []

    
    def on_settings_updated(self, settings):
        # Callback when settings are updated
        if self.selected_images:
            # Recalculate layout when settings change
            self.calculate_layout_preview()
    
    def calculate_layout_preview(self):
        # Calculate layout and update preview
        if not self.selected_images:
            return
            
        try:
            self.preview_panel.show_loading_message("Calculating optimal layout...")
            self.root.update()
            
            # Get current settings
            settings = self.settings_panel.get_settings()
            ### print(f"DEBUG: Processing {len(self.selected_images)} images with settings: {settings}")

            # Calculate layout
            page_layouts = self.page_layout.calculate_layout(
                image_paths=self.selected_images,
                margin_mm=settings['margin_mm'],
                spacing_mm=settings['spacing_mm'],
                allow_rotation=settings['allow_rotation'],
                max_reduction=settings['max_reduction']  # Fixed parameter name
            )
            
            ### print(f"DEBUG: Generated {len(page_layouts)} pages")
            ### for i, page in enumerate(page_layouts):
                ### print(f"DEBUG: Page {i+1} has {len(page['images'])} images")
            
            # Store the layout - make a deep copy
            self.current_page_layouts = copy.deepcopy(page_layouts)
            ### print(f"DEBUG: Stored {len(self.current_page_layouts)} pages in current_page_layouts")
            
            # Show layout in preview
            self.preview_panel.show_layout_preview(self.current_page_layouts)
            self.update_export_button()
            
        except Exception as e:
            print(f"DEBUG: Layout calculation error: {e}")
            self.preview_panel.show_error_message(str(e))
            messagebox.showerror("Layout Error", f"Error calculating layout: {str(e)}")
        
    def update_export_button(self):
        # Enable/disable export button based on current state
        has_images = len(self.selected_images) > 0
        has_layout = len(self.current_page_layouts) > 0
        
        if has_images and has_layout:
            self.export_btn.config(state="normal")
        else:
            self.export_btn.config(state="disabled")
    
    def export_document(self):
        # Handle document export
        ### print(f"DEBUG: export_document - current_page_layouts has {len(self.current_page_layouts)} pages")
        
        if not self.selected_images or not self.current_page_layouts:
            messagebox.showerror("Error", "No images selected or layout calculated!")
            return
        
        try:
            # Get output file path
            settings = self.settings_panel.get_settings()
            format_type = settings['output_format']
            
            file_types = [
                ("PDF Document", "*.pdf"),
                ("All files", "*.*")
            ]
            
            default_extension = ".pdf"
            default_name = f"optimized_layout{default_extension}"
            
            output_path = filedialog.asksaveasfilename(
                title="Save PDF Document As",
                defaultextension=default_extension,
                filetypes=file_types,
                initialfile=default_name
            )
            
            if not output_path:
                return  # User cancelled
                        
            ### print(f"DEBUG: About to export {len(self.current_page_layouts)} pages to PDF")
            
            # Export document
            success, message = self.document_exporter.export_document(
                pages=self.current_page_layouts,
                output_path=output_path,
                format_type=format_type
            )
            
            if success:
                messagebox.showinfo("Export Successful", message)
                # Refresh preview
                self.preview_panel.show_layout_preview(self.current_page_layouts)
            else:
                messagebox.showerror("Export Failed", message)
                self.preview_panel.show_error_message(message)
                
        except Exception as e:
            error_msg = f"Error during export: {str(e)}"
            messagebox.showerror("Export Error", error_msg)
            self.preview_panel.show_error_message(error_msg)
    
    def set_window_icon(self):
        # Replace default Tkinter feather with our ZO icon
        try:
            # Method 1: If running from project root (python src/main.py)
            project_root = os.getcwd()
            icons_dir = os.path.join(project_root, 'assets', 'icons')
            
            # Method 2: If running from src/ directory (python main.py)
            if not os.path.exists(icons_dir):
                # Try going up one level
                project_root = os.path.dirname(os.getcwd())
                icons_dir = os.path.join(project_root, 'assets', 'icons')
            
            
            # Try icon sizes in order
            icon_files = ['icon-128.png', 'icon-64.png', 'icon-32.png', 'icon-16.png', 'icon-512.png']
            
            for icon_file in icon_files:
                icon_path = os.path.join(icons_dir, icon_file)
                if os.path.exists(icon_path):
                    
                    # For all OS - use PhotoImage method (most reliable with Tkinter)
                    img = Image.open(icon_path)
                    photo = ImageTk.PhotoImage(img)
                    self.root.iconphoto(False, photo)  # False = don't use as default
                    
                    # Keep reference to prevent garbage collection
                    self.icon_photo = photo
                    return
            
            print("Icon not found - using default Tkinter feather")
            
        except Exception as e:
            print(f"Could not set icon: {e}")
            # Keep default feather icon if error

    def run(self):
        # Start the application
        self.root.mainloop()

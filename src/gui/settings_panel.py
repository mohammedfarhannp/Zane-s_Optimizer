import tkinter as tk
from tkinter import ttk

class SettingsPanel:
    def __init__(self, parent_frame, settings_callback=None):
        self.parent = parent_frame
        self.settings_callback = settings_callback
        self.setup_settings_ui()
        
        # Default settings
        self.settings = {
            'output_format': 'pdf',
            'margin_mm': 5,
            'spacing_mm': 3,
            'allow_rotation': True,
            'max_reduction': 0.25,  # 25% default
            'dpi': 96,
            'jpeg_quality': 95
        }
        
    def setup_settings_ui(self):
        # Setup the export settings interface
        # Main settings frame
        settings_frame = ttk.LabelFrame(self.parent, text="Export Settings", padding="10")
        settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # Output format
        ttk.Label(settings_frame, text="Output Format:").grid(row=0, column=0, sticky=tk.W)
        self.format_var = tk.StringVar(value="pdf")
        format_combo = ttk.Combobox(settings_frame, textvariable=self.format_var, values=["pdf"], state="readonly", width=10)
        format_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        format_combo.bind('<<ComboboxSelected>>', self.on_settings_change)
        
        # Margin settings
        ttk.Label(settings_frame, text="Margin (mm):").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.margin_var = tk.StringVar(value="5")
        margin_spin = ttk.Spinbox(settings_frame, from_=1, to=50, textvariable=self.margin_var, width=10, command=self.on_settings_change)
        margin_spin.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        margin_spin.bind('<KeyRelease>', self.on_settings_change)
        
        # Spacing settings
        ttk.Label(settings_frame, text="Spacing (mm):").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.spacing_var = tk.StringVar(value="3")
        spacing_spin = ttk.Spinbox(settings_frame, from_=1, to=20, textvariable=self.spacing_var, width=10, command=self.on_settings_change)
        spacing_spin.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(10, 0))
        spacing_spin.bind('<KeyRelease>', self.on_settings_change)
        
        # Allow rotation checkbox
        self.rotation_var = tk.BooleanVar(value=True)
        rotation_cb = ttk.Checkbutton(settings_frame, text="Allow image rotation for better fit", variable=self.rotation_var, command=self.on_settings_change)
        rotation_cb.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # Size reduction slider
        ttk.Label(settings_frame, text="Max Size Reduction:").grid(row=4, column=0, sticky=tk.W, pady=(10, 0))
        
        # Frame for slider and value label
        reduction_frame = ttk.Frame(settings_frame)
        reduction_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(10, 0))
        
        self.reduction_var = tk.IntVar(value=25)  # Default 25%
        
        # Slider
        reduction_slider = ttk.Scale(reduction_frame, from_=0, to=25, variable=self.reduction_var, orient='horizontal', command=self.on_reduction_change)
        reduction_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Value label
        self.reduction_label = ttk.Label(reduction_frame, text="25%", width=5)
        self.reduction_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Advanced settings frame (collapsible)
        self.advanced_frame = ttk.LabelFrame(settings_frame, text="Advanced Settings", padding="5")
        self.advanced_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        self.advanced_frame.columnconfigure(1, weight=1)
        
        # Show/Hide advanced button
        self.advanced_visible = False
        self.advanced_btn = ttk.Button(settings_frame, text="Show Advanced Settings", command=self.toggle_advanced_settings)
        self.advanced_btn.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        # Setup advanced settings (initially hidden)
        self.setup_advanced_settings()
        self.advanced_frame.grid_remove()
        
    def setup_advanced_settings(self):
        # Setup advanced settings options
        # Output DPI setting
        ttk.Label(self.advanced_frame, text="Output DPI:").grid(row=0, column=0, sticky=tk.W)
        self.dpi_var = tk.StringVar(value="96")
        dpi_combo = ttk.Combobox(self.advanced_frame, textvariable=self.dpi_var, values=["72", "96", "150", "200", "300"], state="readonly", width=10)
        dpi_combo.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        dpi_combo.bind('<<ComboboxSelected>>', self.on_settings_change)
        
        # Image quality setting (for JPEG)
        ttk.Label(self.advanced_frame, text="JPEG Quality:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.quality_var = tk.StringVar(value="95")
        quality_scale = ttk.Scale(self.advanced_frame, from_=50, to=100, variable=self.quality_var, orient='horizontal')
        quality_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=(5, 0))
        quality_scale.bind('<ButtonRelease-1>', self.on_settings_change)
        
        # Quality value label
        self.quality_label = ttk.Label(self.advanced_frame, text="95%")
        self.quality_label.grid(row=1, column=2, padx=(5, 0), pady=(5, 0))
        
        # Update quality label when scale changes
        quality_scale.configure(command=self.update_quality_label)
        
    def toggle_advanced_settings(self):
        # Toggle advanced settings visibility
        self.advanced_visible = not self.advanced_visible
        
        if self.advanced_visible:
            self.advanced_frame.grid()
            self.advanced_btn.config(text="Hide Advanced Settings")
        else:
            self.advanced_frame.grid_remove()
            self.advanced_btn.config(text="Show Advanced Settings")
        
    def on_reduction_change(self, value=None):
        # Update reduction label when slider changes
        reduction_value = int(float(self.reduction_var.get()))
        self.reduction_label.config(text=f"{reduction_value}%")
        self.on_settings_change()
        
    def update_quality_label(self, value):
        # Update the quality percentage label
        self.quality_label.config(text=f"{int(float(value))}%")
        self.on_settings_change()
        
    def on_settings_change(self, event=None):
        # Handle settings changes and update internal settings dictionary
        try:
            # Update settings dictionary
            self.settings.update({
                'output_format': self.format_var.get(),
                'margin_mm': int(self.margin_var.get()),
                'spacing_mm': int(self.spacing_var.get()),
                'allow_rotation': self.rotation_var.get(),
                'max_reduction': int(self.reduction_var.get()) / 100.0,  # Convert % to decimal
                'dpi': int(self.dpi_var.get()),
                'jpeg_quality': int(self.quality_var.get())
            })
            
            # Validate margin and spacing values
            margin = int(self.margin_var.get())
            spacing = int(self.spacing_var.get())
            
            if margin < 1 or margin > 50:
                self.margin_var.set("5")
                
            if spacing < 1 or spacing > 20:
                self.spacing_var.set("3")
            
            # Call callback if provided
            if self.settings_callback:
                self.settings_callback(self.settings)
                
        except ValueError:
            pass
            
    def get_settings(self):
        # Return current settings dictionary
        return self.settings.copy()
        
    def set_settings(self, new_settings):
        # Update settings from external source
        if 'output_format' in new_settings:
            self.format_var.set(new_settings['output_format'])
        if 'margin_mm' in new_settings:
            self.margin_var.set(str(new_settings['margin_mm']))
        if 'spacing_mm' in new_settings:
            self.spacing_var.set(str(new_settings['spacing_mm']))
        if 'allow_rotation' in new_settings:
            self.rotation_var.set(new_settings['allow_rotation'])
        if 'max_reduction' in new_settings:
            reduction_percent = int(new_settings['max_reduction'] * 100)
            self.reduction_var.set(reduction_percent)
            self.reduction_label.config(text=f"{reduction_percent}%")
        if 'dpi' in new_settings:
            self.dpi_var.set(str(new_settings['dpi']))
        if 'jpeg_quality' in new_settings:
            self.quality_var.set(str(new_settings['jpeg_quality']))
        
        self.on_settings_change()
import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PIL import Image

class DocumentExporter:
    def __init__(self):
        self.a4_width = 210  # mm
        self.a4_height = 297  # mm
        
    def export_to_pdf(self, pages, output_path):
        # Export layout to PDF document with precise positioning
        try:
            # Create PDF canvas
            c = canvas.Canvas(output_path, pagesize=A4)
            page_width_pt, page_height_pt = A4
            
            ### print(f"DEBUG: Exporting {len(pages)} pages to PDF")
            
            for page_num, page in enumerate(pages):
                ### print(f"DEBUG: Processing page {page_num + 1} with {len(page['images'])} images")
                
                if page_num > 0:
                    c.showPage()  # Start new page
                
                for img_num, img_data in enumerate(page['images']):
                    # Get image data
                    pil_image = img_data['image']
                    img_width_px = img_data['width']
                    img_height_px = img_data['height']
                    
                    # Convert pixel coordinates to PDF points
                    # PDF uses points: 1 point = 1/72 inch
                    # Assuming 96 DPI: 1 pixel = 72/96 = 0.75 points
                    x_pt = img_data['x'] * 0.75
                    y_pt = img_data['y'] * 0.75
                    width_pt = img_width_px * 0.75
                    height_pt = img_height_px * 0.75
                    
                    # Convert from top-left to bottom-left coordinate system
                    # PDF origin is bottom-left, our layout uses top-left
                    y_pt = page_height_pt - y_pt - height_pt
                    
                    ### print(f"DEBUG: Image {img_num + 1} at ({x_pt:.1f}pt, {y_pt:.1f}pt) size {width_pt:.1f}x{height_pt:.1f}pt")
                    
                    # Save image to temporary file
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                        pil_image.save(temp_file, format='PNG')
                        temp_path = temp_file.name
                    
                    # Draw image at calculated position
                    c.drawImage(temp_path, x_pt, y_pt, 
                               width=width_pt, height=height_pt)
                    
                    # Clean up temp file
                    os.unlink(temp_path)
            
            # Save PDF
            c.save()
            ### print(f"DEBUG: PDF saved successfully to {output_path}")
            return True, f"PDF document saved to {output_path}"
            
        except Exception as e:
            print(f"DEBUG: Error exporting to PDF: {str(e)}")
            return False, f"Error exporting to PDF: {str(e)}"
    
    def export_document(self, pages, output_path, format_type='pdf'):
        # Main export method - PDF only supported
        if format_type.lower() == 'pdf':
            return self.export_to_pdf(pages, output_path)
        else:
            return False, f"Unsupported format: {format_type}. Only PDF is supported."
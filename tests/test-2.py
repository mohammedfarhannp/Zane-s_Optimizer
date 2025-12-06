import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PIL import Image as PILImage
import io
import tempfile

def test_pdf_image_positioning(image_path, output_path="test_output.pdf"):
    """Test placing an image at specific coordinates in PDF"""
    
    print(f"Testing PDF image positioning...")
    print(f"Input image: {image_path}")
    print(f"Output PDF: {output_path}")
    
    try:
        # Create a canvas (PDF document)
        c = canvas.Canvas(output_path, pagesize=A4)
        
        # A4 dimensions: 210mm x 297mm
        page_width, page_height = A4
        
        print(f"\nA4 Page size: {page_width/mm:.0f}mm x {page_height/mm:.0f}mm")
        print(f"In points: {page_width:.0f}pt x {page_height:.0f}pt")
        
        # Load the image
        pil_image = PILImage.open(image_path)
        img_width_px, img_height_px = pil_image.size
        print(f"\nImage size: {img_width_px}x{img_height_px} pixels")
        
        # Convert to desired size (let's use 50mm width)
        target_width_mm = 50
        target_width_pt = target_width_mm * mm
        aspect_ratio = img_height_px / img_width_px
        target_height_pt = target_width_pt * aspect_ratio
        
        print(f"\nTarget size: {target_width_mm}mm width")
        print(f"Target height: {target_height_pt/mm:.1f}mm")
        
        # Desired position: 5mm from left, 5mm from top
        # Note: PDF coordinates start from BOTTOM-left (0,0)
        # So we need to convert from top-left coordinates
        
        x_mm = 5
        y_from_top_mm = 5  # From top of page
        
        # Convert to PDF coordinates
        x_pt = x_mm * mm
        y_from_top_pt = y_from_top_mm * mm
        y_pt = page_height - y_from_top_pt - target_height_pt
        
        print(f"\nPositioning coordinates:")
        print(f"Requested: ({x_mm}mm, {y_from_top_mm}mm) from top-left")
        print(f"PDF coords: ({x_pt:.1f}pt, {y_pt:.1f}pt)")
        print(f"Which is: ({x_pt/mm:.1f}mm, {y_pt/mm:.1f}mm) from bottom-left")
        
        # Save image to a temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            pil_image.save(temp_file, format='PNG')
            temp_path = temp_file.name
        
        # Draw image at specified position
        print(f"\nDrawing image at ({x_pt:.1f}pt, {y_pt:.1f}pt)")
        c.drawImage(temp_path, x_pt, y_pt, 
                   width=target_width_pt, height=target_height_pt)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Add some reference lines and text
        c.setStrokeColorRGB(1, 0, 0)  # Red color
        c.setLineWidth(0.5)
        
        # Draw a cross at the 5mm,5mm point (from top-left)
#         cross_size = 5 * mm
#         c.line(x_pt - cross_size, y_pt + target_height_pt/2, 
#                x_pt + cross_size, y_pt + target_height_pt/2)
#         c.line(x_pt, y_pt + target_height_pt/2 - cross_size,
#                x_pt, y_pt + target_height_pt/2 + cross_size)
        
        # Add text labels
        c.setFillColorRGB(0, 0, 1)  # Blue color
        c.setFont("Helvetica", 8)
        
        # Label the cross
        #c.drawString(x_pt + 10, y_pt + target_height_pt/2 + 10, f"Start: ({x_mm}mm, {y_from_top_mm}mm) from top-left")
        
        # Label the page corners
#         c.drawString(10, 10, "Bottom-Left (0,0)")
#         c.drawString(page_width - 100, 10, f"Bottom-Right ({page_width/mm:.0f}mm, 0)")
#         c.drawString(10, page_height - 20, f"Top-Left (0, {page_height/mm:.0f}mm)")
#         c.drawString(page_width - 100, page_height - 20, 
#                     f"Top-Right ({page_width/mm:.0f}mm, {page_height/mm:.0f}mm)")
#         
        # Draw page border
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(0.5)
        c.rect(0, 0, page_width, page_height)
        
        # Save the PDF
        c.save()
        
        print(f"\n✅ PDF created successfully!")
        print(f"Image placed at {x_mm}mm from left, {y_from_top_mm}mm from top")
        print(f"Open '{output_path}' to see the result")
        
        # Verify file was created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / 1024
            print(f"PDF file size: {file_size:.1f} KB")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test with your actual image
    test_image_path = ""
    
    # Run the test
    success = test_pdf_image_positioning(test_image_path)
    
    if success:
        print("\n📋 Summary:")
        print("1. The image should be placed 5mm from left edge")
        print("2. The image should be placed 5mm from top edge")
        print("3. A red cross marks the starting point (top-left corner of image)")
        print("4. Blue text labels show coordinates")
        print("5. Black border shows the A4 page boundaries")
        print("\nOpen 'test_output.pdf' to verify positioning!")
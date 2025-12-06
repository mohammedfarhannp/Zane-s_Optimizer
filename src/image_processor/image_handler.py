from PIL import Image, ImageOps
import os

class ImageHandler:
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff']
    
    def load_image(self, image_path):
        # Load an image from file path
        try:
            image = Image.open(image_path)
            # Convert to RGB if necessary (for JPEG compatibility)
            if image.mode in ('RGBA', 'P', 'LA'):
                image = image.convert('RGB')
            return image
        except Exception as e:
            raise Exception(f"Error loading image {image_path}: {str(e)}")
    
    def get_image_info(self, image_path):
        # Get basic information about an image
        try:
            image = self.load_image(image_path)
            width, height = image.size
            file_size = os.path.getsize(image_path) / 1024  # Size in KB
            
            return {
                'path': image_path,
                'width': width,
                'height': height,
                'size_kb': round(file_size, 2),
                'aspect_ratio': width / height,
                'filename': os.path.basename(image_path)
            }
        except Exception as e:
            raise Exception(f"Error getting image info for {image_path}: {str(e)}")
    
    def should_resize_by_threshold(self, image, container_width, container_height, threshold=0.6):
        # Check if image occupies more than threshold% of container
        # threshold: 0.6 = 60%
        # Returns: True if image should be resized
        
        img_width, img_height = image.size
        
        # Calculate how much space image would occupy
        width_ratio = img_width / container_width
        height_ratio = img_height / container_height
        
        # Image is "too big" if either dimension exceeds threshold
        return width_ratio > threshold or height_ratio > threshold
        
    def resize_image(self, image, max_width, max_height, max_reduction=0.25, threshold=0.6):
        # Resize image while maintaining aspect ratio
        # Only resize if image occupies more than threshold% of available space
        # max_reduction: Maximum allowed size reduction (0.25 = 25%)
        # threshold: Only resize if image > threshold% of space (0.6 = 60%)
        # Returns: (resized_image, was_resized)

        original_width, original_height = image.size
        
        # Check if image is too big (occupies more than threshold)
        width_ratio = original_width / max_width
        height_ratio = original_height / max_height
        
        # Only resize if image exceeds threshold in either dimension
        if not (width_ratio > threshold or height_ratio > threshold):
            return image, False  # Don't resize - image is not "too big"
        
        # If max_reduction is 0, don't resize at all
        if max_reduction <= 0:
            return image, False
        
        # Calculate scaling factors
        width_ratio = max_width / original_width
        height_ratio = max_height / original_height
        
        # Use the smaller ratio to maintain aspect ratio and fit within bounds
        scale_ratio = min(width_ratio, height_ratio)
        
        # Apply maximum reduction limit
        if scale_ratio < (1 - max_reduction):
            scale_ratio = 1 - max_reduction
        
        # Only resize if needed and within allowed reduction
        if scale_ratio < 1:
            new_width = int(original_width * scale_ratio)
            new_height = int(original_height * scale_ratio)
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            return resized_image, True
        
        return image, False
    
    def rotate_image(self, image, allow_rotation=True):
        # Rotate image by 90 degrees if allowed
        # Returns: (rotated_image, was_rotated)
        if not allow_rotation:
            return image, False
        
        # Rotate 90 degrees clockwise
        rotated_image = image.rotate(-90, expand=True)
        return rotated_image, True
    
    def calculate_best_fit(self, image, container_width, container_height, allow_rotation=True):
        # Calculate whether image fits better in original or rotated orientation
        # Returns: (should_rotate, fit_ratio)
        original_width, original_height = image.size
        
        # Calculate fit ratio for original orientation
        width_ratio_orig = container_width / original_width
        height_ratio_orig = container_height / original_height
        fit_ratio_orig = min(width_ratio_orig, height_ratio_orig)
        
        if not allow_rotation:
            return False, fit_ratio_orig
        
        # Calculate fit ratio for rotated orientation
        width_ratio_rot = container_width / original_height
        height_ratio_rot = container_height / original_width
        fit_ratio_rot = min(width_ratio_rot, height_ratio_rot)
        
        # Choose orientation with better fit
        if fit_ratio_rot > fit_ratio_orig:
            return True, fit_ratio_rot
        else:
            return False, fit_ratio_orig
    
    def prepare_image_for_page(self, image, page_width, page_height, margin_mm, allow_rotation=True, max_reduction=0.25, threshold=0.6):
        # Prepare image for placement on page with given constraints
        # threshold: Only resize if image > threshold% of available space (0.6 = 60%)
        # Returns: (prepared_image, was_rotated, was_resized, actual_width, actual_height)

        # Convert mm to pixels (assuming 96 DPI)
        margin_px = int(margin_mm * 3.78)
        available_width = page_width - (2 * margin_px)
        available_height = page_height - (2 * margin_px)
        
        # Determine best orientation
        should_rotate, fit_ratio = self.calculate_best_fit(
            image, available_width, available_height, allow_rotation
        )
        
        # Apply rotation if needed
        if should_rotate:
            image, was_rotated = self.rotate_image(image, allow_rotation)
        else:
            was_rotated = False
        
        # Apply resizing if needed (with threshold check)
        image, was_resized = self.resize_image(
            image, available_width, available_height, max_reduction, threshold
        )
        
        final_width, final_height = image.size
        
        return image, was_rotated, was_resized, final_width, final_height
    
    def is_supported_format(self, file_path):
        # Check if file format is supported
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_formats
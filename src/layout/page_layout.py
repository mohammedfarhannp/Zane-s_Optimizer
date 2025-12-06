from image_processor.image_handler import ImageHandler

class PageLayout:
    def __init__(self):
        self.image_handler = ImageHandler()
        # A4 dimensions in pixels at 96 DPI
        self.a4_width = 794   # 210mm * 3.78
        self.a4_height = 1123  # 297mm * 3.78
        
    def calculate_layout(self, image_paths, margin_mm=5, spacing_mm=3, allow_rotation=True, max_reduction=0.25):
        # Calculate optimal layout for images on A4 pages
        # Returns: List of pages with image positions
        
        # Convert mm to pixels
        margin_px = int(margin_mm * 3.78)
        spacing_px = int(spacing_mm * 3.78)
        
        available_width = self.a4_width - (2 * margin_px)
        available_height = self.a4_height - (2 * margin_px)
        
        # Load and prepare all images
        prepared_images = []
        for path in image_paths:
            image = self.image_handler.load_image(path)
            prepared_image, was_rotated, was_resized, width, height = self.image_handler.prepare_image_for_page(
                    image, available_width, available_height, margin_mm,
                    allow_rotation, max_reduction
                )
            
            prepared_images.append({
                'original_path': path,
                'image': prepared_image,
                'width': width,
                'height': height,
                'was_rotated': was_rotated,
                'was_resized': was_resized
            })
        
        # Sort by maximum dimension first, then by area
        prepared_images.sort(key=lambda x: (max(x['width'], x['height']), x['width'] * x['height']), reverse=True)
        
        # Pack images into pages using optimized algorithm
        pages = self._pack_images(prepared_images, available_width, available_height, margin_px, spacing_px)
        
        return pages
    
    def _pack_images(self, images, page_width, page_height, margin_px, spacing_px):
        # Pack images into pages using look-ahead free rectangle packing
        # Added safety limits to prevent infinite loops
        
        try:
            pages = []
            
            # Make a mutable copy of images to track unplaced ones
            unplaced_images = images.copy()
            
            # SAFETY: Maximum pages to prevent infinite loop
            # No academic project needs more than 50 pages
            max_total_pages = 50
            
            while unplaced_images and len(pages) < max_total_pages:
                # Start a new page
                current_page = {
                    'page_number': len(pages) + 1,
                    'images': [],
                    'free_rectangles': [(margin_px, margin_px, 
                                       page_width - 2 * margin_px, 
                                       page_height - 2 * margin_px)]
                }
                
                placed_on_this_page = True
                
                # SAFETY: Maximum attempts on current page
                # Prevents infinite search loop
                max_page_attempts = 100
                page_attempts = 0
                
                # Keep trying to place images until nothing fits
                while placed_on_this_page and unplaced_images and page_attempts < max_page_attempts:
                    page_attempts += 1
                    placed_on_this_page = False
                    
                    # Try each unplaced image (look-ahead)
                    for img_idx, img_data in enumerate(unplaced_images):
                        img_width = img_data['width']
                        img_height = img_data['height']
                        
                        # Try both orientations
                        best_rect = None
                        best_rotation = False
                        
                        for rotation in [False, True]:
                            if rotation and not img_data.get('was_rotated', False):
                                continue
                            
                            w = img_height if rotation else img_width
                            h = img_width if rotation else img_height
                            
                            # Find fitting free rectangle
                            for rect in current_page['free_rectangles']:
                                rx, ry, rw, rh = rect
                                if w <= rw and h <= rh:
                                    if best_rect is None or ry < best_rect[1] or (ry == best_rect[1] and rx < best_rect[0]):
                                        best_rect = rect
                                        best_rotation = rotation
                        
                        if best_rect:
                            # Place this image
                            rx, ry, rw, rh = best_rect
                            w = img_height if best_rotation else img_width
                            h = img_width if best_rotation else img_height
                            
                            x = rx
                            y = ry
                            
                            current_page['images'].append({
                                'image': img_data['image'],
                                'original_path': img_data['original_path'],
                                'x': x,
                                'y': y,
                                'width': w,
                                'height': h,
                                'rotated': best_rotation or img_data['was_rotated'],
                                'resized': img_data['was_resized']
                            })
                            
                            # Remove used rectangle and split space
                            current_page['free_rectangles'].remove(best_rect)
                            
                            # Split remaining space
                            # Right rectangle
                            if rw - w - spacing_px > 0:
                                current_page['free_rectangles'].append(
                                    (rx + w + spacing_px, ry, rw - w - spacing_px, h)
                                )
                            
                            # Bottom rectangle
                            if rh - h - spacing_px > 0:
                                current_page['free_rectangles'].append(
                                    (rx, ry + h + spacing_px, rw, rh - h - spacing_px)
                                )
                            
                            # Top-right corner
                            if rw - w - spacing_px > 0 and rh - h - spacing_px > 0:
                                current_page['free_rectangles'].append(
                                    (rx + w + spacing_px, ry + h + spacing_px, 
                                     rw - w - spacing_px, rh - h - spacing_px)
                                )
                            
                            # Merge adjacent rectangles
                            self._merge_free_rectangles(current_page['free_rectangles'])
                            
                            # Remove image from unplaced list
                            unplaced_images.pop(img_idx)
                            placed_on_this_page = True
                            break  # Restart the search after placement
                
                # SAFETY: If we hit max attempts, force start new page
                if page_attempts >= max_page_attempts:
                    print(f"DEBUG: Safety limit reached on page {len(pages) + 1}")
                    # Force place first image on new page
                    if unplaced_images:
                        img_data = unplaced_images[0]
                        x = margin_px
                        y = margin_px
                        
                        current_page['images'].append({
                            'image': img_data['image'],
                            'original_path': img_data['original_path'],
                            'x': x,
                            'y': y,
                            'width': img_data['width'],
                            'height': img_data['height'],
                            'rotated': img_data['was_rotated'],
                            'resized': img_data['was_resized']
                        })
                        
                        unplaced_images.pop(0)
                
                # Add completed page
                if current_page['images']:
                    pages.append(self._finalize_page(current_page))
            
            # SAFETY: Warn if we hit page limit
            if len(pages) >= max_total_pages and unplaced_images:
                print(f"WARNING: Stopped at {max_total_pages} pages. {len(unplaced_images)} images not placed.")
            
            return pages
            
        except Exception as e:
            print(f"DEBUG: Error in _pack_images: {e}")
            import traceback
            traceback.print_exc()
            return []  # Return empty instead of freezing
    
    def _merge_free_rectangles(self, rectangles):
        # Merge adjacent free rectangles to reduce fragmentation
        
        merged = True
        while merged:
            merged = False
            i = 0
            while i < len(rectangles):
                j = i + 1
                while j < len(rectangles):
                    r1 = rectangles[i]
                    r2 = rectangles[j]
                    
                    # Merge if same width and adjacent vertically
                    if r1[0] == r2[0] and r1[2] == r2[2] and r1[1] + r1[3] == r2[1]:
                        rectangles[i] = (r1[0], r1[1], r1[2], r1[3] + r2[3])
                        rectangles.pop(j)
                        merged = True
                    # Merge if same height and adjacent horizontally
                    elif r1[1] == r2[1] and r1[3] == r2[3] and r1[0] + r1[2] == r2[0]:
                        rectangles[i] = (r1[0], r1[1], r1[2] + r2[2], r1[3])
                        rectangles.pop(j)
                        merged = True
                    else:
                        j += 1
                i += 1
    
    def _finalize_page(self, page_data):
        # Convert internal page format to final output format
        return {
            'page_number': page_data['page_number'],
            'images': page_data['images']
        }
    
    def get_layout_summary(self, pages):
        # Get summary information about the layout
        
        total_images = sum(len(page['images']) for page in pages)
        total_pages = len(pages)
        
        rotated_count = 0
        resized_count = 0
        
        for page in pages:
            for img in page['images']:
                if img['rotated']:
                    rotated_count += 1
                if img['resized']:
                    resized_count += 1
        
        return {
            'total_pages': total_pages,
            'total_images': total_images,
            'rotated_images': rotated_count,
            'resized_images': resized_count,
            'efficiency': total_images / (total_pages * 8) if total_pages > 0 else 0
        }
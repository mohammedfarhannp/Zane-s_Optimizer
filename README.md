# Zane's Optimizer

A Python tool that automatically arranges multiple images optimally on A4 PDF pages.

Perfect for academic lab work output printouts.

## Quick Start
1. Install: `pip install -r requirements.txt`
2. Run: `python src/main.py`

## How to Use
1. Click **Select Images** to choose your images
2. Adjust settings (margins, spacing, rotation, size reduction)
3. Preview the layout
4. Click **Export PDF** to save

## Features
- Smart image selection with preview
- Automatic optimal layout calculation
- Adjustable margins, spacing, and rotation
- 0-25% size reduction control
- PDF export with precise positioning

## Settings
- **Margin:** Space from page edges (recommended: 5mm)
- **Spacing:** Gap between images (recommended: 3mm)
- **Rotation:** Allow 90° rotation for better fit
- **Size Reduction:** Shrink large images up to 25%

## Supported Image Formats
PNG, JPG, JPEG, BMP, GIF, TIFF

## Requirements
- Python 3.8+
- Pillow (for images)
- ReportLab (for PDF)

## Troubleshooting
- **Images overlapping?** Increase spacing setting
- **Can't select images?** Check file format
- **App won't start?** Run `pip install -r requirements.txt`

## Project Structure
- `src/main.py` - Main application
- `src/gui/` - User interface
- `src/layout/` - Layout algorithm
- `src/exporter/` - PDF export

---

# Contribution
We welcome contributions to improve Zane's Optimizer! Here's how you can help:

1. **Fork** the repository
2. **Create a feature branch** for your changes
3. **Implement improvements** or bug fixes
4. **Test thoroughly** to ensure functionality
5. **Submit a Pull Request** with clear description of changes

Please ensure your code follows the existing style and includes appropriate comments.

---

## Contributions
### 1. Icon preparation by ![Shad C T](https://github.com/shad-ct) 

import aspose.words as aw
from PIL import Image

PAGE_WIDTH = aw.ConvertUtil.millimeter_to_point(210)
PAGE_HEIGHT = aw.ConvertUtil.millimeter_to_point(297)
MARGIN = aw.ConvertUtil.millimeter_to_point(5)

usable_width = PAGE_WIDTH
usable_height = PAGE_HEIGHT

doc = aw.Document()
builder = aw.DocumentBuilder(doc)

cursor_y = MARGIN
shelf_height = 0
cursor_x = MARGIN

def new_page():
    global cursor_x, cursor_y, shelf_height
    builder.insert_break(aw.BreakType.PAGE_BREAK)
    cursor_x = MARGIN
    cursor_y = MARGIN
    shelf_height = 0

def add_image(path):
    global cursor_x, cursor_y, shelf_height

    # load image to get pixel size
    img = Image.open(path)
    w, h = img.size
    aspect = w / h

    max_w = usable_width * 0.48
    if w > max_w:
        w = max_w
        h = w / aspect

    # new shelf if needed
    if cursor_x + w > PAGE_WIDTH - MARGIN:
        cursor_x = MARGIN
        cursor_y += shelf_height + 10
        shelf_height = 0

    # new page if needed
    if cursor_y + h > PAGE_HEIGHT - MARGIN:
        new_page()

    # --- create positioned shape ---
    shape = aw.drawing.Shape(doc, aw.drawing.ShapeType.IMAGE)

    shape.width = w
    shape.height = h
    shape.left = cursor_x
    shape.top = cursor_y

    shape.wrap_type = aw.drawing.WrapType.NONE
    shape.relative_horizontal_position = aw.drawing.RelativeHorizontalPosition.PAGE
    shape.relative_vertical_position = aw.drawing.RelativeVerticalPosition.PAGE

    # load image into shape
    import io
    with open(path, "rb") as f:
        shape.image_data.set_image(f)

    # insert shape into document
    builder.insert_node(shape)

    # update shelf
    cursor_x += w + 5
    shelf_height = max(shelf_height, h)


# --- Insert your images ---
add_image("")
# add_image("…") more images

doc.save("album.docx")

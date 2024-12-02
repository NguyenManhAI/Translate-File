import io
import os
from PIL import Image
import uuid
from reportlab.pdfbase.pdfmetrics import stringWidth
import math
from reportlab.lib.colors import Color

def save_txt(text, text_file):
    with open(text_file, 'w') as file:
        file.write(text)
        print("ghi thành công")

def get_text_block(block):
    lines = block['lines']
    text_lines = []
    for line in lines:
        # Mỗi line chứa các span - là các thành phần text được chia nhỏ từ 1 line
        text_line = ""
        for span in line['spans']:
            text_line += span['text']
        text_lines.append(text_line)
    text_lines = "\n".join(text_lines)
    return text_lines
# text = _get_text_block(block)
# save_txt(text, 'text.txt')

def stringwidth_with_new_text(original_text, new_text, block):
    # Bước 1: với fontname và fontsize cũ, tính tổng stringwidth (sw)
    lines = block['lines']
    k0 = new_text / original_text
    sw = 0
    start = 0
    for line in lines:
        # Mỗi line chứa các span - là các thành phần text được chia nhỏ từ 1 line
        for span in line['spans']:
            text = span['text']
            end = start + len(text)*k0
            
            new_text_for_span = new_text[start:end]
            sw += stringWidth(text=new_text_for_span, fontName= span['font'], fontSize= span['size'])

            # cập nhật start
            start = end
    return sw
    
def get_all_spans_len(block):
    lines = block['lines']
    len = 0
    for line in lines:
        # Mỗi line chứa các span - là các thành phần text được chia nhỏ từ 1 line
        for span in line['spans']:
            x0, y0, x1, y1 = span['bbox']
            len += x1 - x0
    return len

# Hàm chuyển đổi màu từ định dạng int sang (R, G, B)
def int_to_rgb(color_int):
    r = (color_int >> 16) & 0xFF
    g = (color_int >> 8) & 0xFF
    b = color_int & 0xFF
    return Color(r / 255, g / 255, b / 255)

# lưu 1 line vào file pdf
def write_line(c, line):
    # lấy thông tin của line
    spans = line['spans']
    dir = line['dir']
    # tính góc xoay của line
    angle = math.degrees(math.atan2(dir[1], dir[0]))  # Góc xoay từ dir

    for span in spans:
        text = span['text']
        font = span['font']
        font_size = span['size']
        color = span['color']
        x0, y0, _, _ = span['bbox'] # tọa độ đã được điều chỉnh theo report lab

        # Thiết lập font, kích thước, và màu
        c.setFont(font, font_size)
        c.setFillColor(int_to_rgb(color))

        # Lưu trạng thái trước khi xoay
        c.saveState()

        # Xoay canvas tại điểm (x, adjusted_y)
        c.translate(x0, y0)  # Di chuyển gốc tọa độ đến vị trí văn bản
        c.rotate(angle)  # Xoay theo góc angle

        # Vẽ văn bản tại gốc mới
        c.drawString(0, 0, text)

        # Khôi phục trạng thái sau khi xoay
        c.restoreState()

def write_block_image(c, block):
    # Lấy dữ liệu hình ảnh từ block
    image_data = block['image']

    # Tạo một đối tượng hình ảnh từ dữ liệu nhị phân
    image = Image.open(io.BytesIO(image_data))

    # Lưu hình ảnh tạm để sử dụng với ReportLab
    temp_image_path = f"temp_image_{uuid.uuid4().hex}.png"
    image.save(temp_image_path)

    # Lấy kích thước bbox để đặt hình ảnh trong PDF
    x0, y0, x1, y1 = block['bbox']
    width = x1 - x0
    height = y1 - y0

    # Đặt hình ảnh vào PDF
    c.drawImage(temp_image_path, x0, y0, width, height)

    os.remove(temp_image_path)
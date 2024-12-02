# Hàm để lấy các text trong file pdf và các thông tin xung quanh nó
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import Color
import math
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import fitz

from .create import *

# Đăng ký font
pdfmetrics.registerFont(TTFont('Tinos', 'asset/font/Tinos-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Tajawal', 'asset/font/Tajawal-Regular.ttf'))
pdfmetrics.registerFont(TTFont('PlayfairDisplay', 'asset/font/PlayfairDisplay-Regular.ttf'))
pdfmetrics.registerFont(TTFont('MPLUS1p', 'asset/font/MPLUS1p-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NanumGothic', 'asset/font/NanumGothic-Regular.ttf'))
pdfmetrics.registerFont(TTFont('Sarabun', 'asset/font/Sarabun-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NotoSans', 'asset/font/NotoSans-Regular.ttf'))

config_font = {
    "en": 'PlayfairDisplay',
    "vi": 'Tinos',
    "fr": 'PlayfairDisplay',
    "es": 'PlayfairDisplay',
    "ja": 'MPLUS1p',
    "de": 'PlayfairDisplay',
    "it": 'PlayfairDisplay',
    "ko": 'NanumGothic',
    "zh": 'NanumGothic',
    "ru": 'PlayfairDisplay',
    "ar": 'Tajawal',
    "th": 'Sarabun',
    "hi": 'NotoSans'
}

def translate_pdf(input_file, output_file, translate, src_lang, trg_lang):
    # lấy tài liệu từ file pdf
    doc = fitz.open(input_file)

    # lấy số trang của tài liệu
    page_count = doc.page_count

    # Tạo 1 file pdf mới
    c = canvas.Canvas(output_file, pagesize=A4)
    page_width, page_height = A4  # Kích thước trang

    # lặp qua từng page của tài liệu
    for page_num in range(page_count):
        # lấy thông tin của 1 trang
        page = doc[page_num].get_text("dict")
        # lấy chiều dài, chiều rộng của page (tạo page sau khi dịch tương ứng)
        width, height = page['width'], page['height']
        # lấy các block có trong page
        blocks = page['blocks']

        for idx_block, block in enumerate(blocks):
            # Xử lý văn bản
            if 'lines' in block:
                # phase 1: lấy tất cả text trong block để dịch
                text = get_text_block(block)
                translated_text = translate(text, src_lang, trg_lang)

                # phase 2: chia đều text đã dịch vào các lines cũng như spans
                """
                Lấy tỉ lệ độ dài trước và sau khi dịch làm tỉ lệ font
                """
                # Lấy chiều dài của văn bản trước và sau khi dịch
                original_text_length = len(text)
                translated_text_length = len(translated_text)
                k = max(translated_text_length / original_text_length, 1)

                lines = block['lines']
                start = 0
                for idx_line, line in enumerate(lines):
                    # Mỗi line chứa các span - là các thành phần text được chia nhỏ từ 1 line
                    vx, vy = line['dir']
                    dir = vx, vy*(-1) # y trong reportlab ngược so với fitz
                    new_spans = []
                    for idx_span, span in enumerate(line['spans']):
                        text_span = span['text']
                        fontname = config_font[trg_lang]

                        # cắt văn bản dịch phù hợp với span
                        end = round(start + len(text_span)*k)
                        new_text_span = translated_text[start:end].strip()
                        # Xử lý khi end không chạm đến phần cuối của translated text
                        if idx_line == len(lines) - 1 and idx_span == len(line['spans']) - 1:
                            new_text_span = translated_text[start:].strip()
                        # padding
                        if end > translated_text_length:
                            new_text_span += " "*(end - max(translated_text_length, start))
                        # Xử lý khi new_text_span trống
                        if len(new_text_span) == 0:
                            new_text_span = " "

                        # lấy chiều dài span
                        x0, y0, x1, y1 = span['bbox']
                        width_span = math.sqrt(((x1 - x0)*dir[0])**2 + ((y1 - y0)*dir[1])**2)
                        
                        # Thiết lập fontsize, fontname
                        new_fontsize = width_span / stringWidth(new_text_span, fontname, 1)

                        # Ràng buộc: new fontsize không được vượt quá 1.3 lần fontsize gốc
                        new_fontsize = min(new_fontsize, 1.3*span['size'])

                        # cập nhật span
                        span['font'] = config_font[trg_lang]
                        span['text'] = new_text_span
                        span['size'] = new_fontsize
                        span['dir'] = dir
                        span['bbox'] = span['bbox'][0], page_height - span['bbox'][1], span['bbox'][2], page_height - span['bbox'][3] # điều chinh theo report lab
                        span['origin'] = span['origin'][0], page_height - span['origin'][1] # điều chinh theo report lab

                        new_spans.append(span)
                        # cập nhật start
                        start = end

                    # cập nhật line
                    line['spans'] = new_spans
                    line['bbox'] = line['bbox'][0], page_height - line['bbox'][1], line['bbox'][2], page_height - line['bbox'][3] # điều chinh theo report lab

                    # ghi 1 line mới vào file pdf, c sẽ được thay đổi tùy thuộc vào các thuộc tính của span hiện tại
                    write_line(c, line)
                    print(f"Xong line {idx_line + 1}/{len(lines)}")

            # Xử lý hình ảnh
            if 'image' in block:
                x0, y0, x1, y1 = block['bbox']
                y0 = page_height - y0 # điều chinh theo report lab
                y1 = page_height - y1 # điều chinh theo report lab
                block['bbox'] = x0, y0, x1, y1

                # ghi ảnh
                write_block_image(c, block)
            
            print(f"Xong block {idx_block + 1}/{len(blocks)}")
        
        print(f"Xong page {page_num + 1}")
        # Kết thúc trang và chuyển sang trang mới nếu còn trang
        c.showPage()
    # Sau khi đã duyệt xong hết tất cả các page, lưu file mới
    c.save()
    # đóng pdf
    doc.close()
    print(f"Dịch thành công: {output_file}")

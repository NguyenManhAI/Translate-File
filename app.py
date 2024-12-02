from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import os
from modules.powerpoint.extract_text import extract_text_with_powerpoint
from modules.powerpoint.create_powerpoint import create_translated_pptx
from modules.excel.extract_excel import extract_text_image_with_excel
from modules.excel.create_excel import create_translated_excel
from modules.pdf.extract import translate_pdf
from modules.db.db import *
from modules.translate.translate import translate
from enum import Enum

from docx2pdf import convert

from pdf2docx import Converter
def pdf_to_docx(pdf_path, docx_path):
    # Tạo một đối tượng Converter
    cv = Converter(pdf_path)
    
    # Chuyển đổi PDF sang DOCX
    cv.convert(docx_path, start=0, end=None)  # start=0 để bắt đầu từ trang đầu, end=None để chuyển đổi toàn bộ
    cv.close()

import logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Đường dẫn để lưu các file tạm thời
UPLOAD_DIRECTORY = "./uploads"
TRANSLATED_DIRECTORY = "./translated"

# Đảm bảo FastAPI phục vụ các tệp tĩnh từ thư mục 'static'
app.mount("/static", StaticFiles(directory="static"), name="static")

# Đảm bảo thư mục tồn tại
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
os.makedirs(TRANSLATED_DIRECTORY, exist_ok=True)

config = {
    'model_translatation': translate
}

class Language(str, Enum):
    ENGLISH = "en"
    VIETNAMESE = "vi"
    FRENCH = "fr"
    SPANISH = "es"
    JAPANESE = "ja"
    GERMAN = "de"
    ITALIAN = "it"
    KOREAN = "ko"
    CHINESE = "zh"
    RUSSIAN = "ru"
    ARABIC = "ar"
    THAI = "th"
    HINDI = "hi"

    @classmethod
    def list_languages(cls):
        """Trả về danh sách tất cả các ngôn ngữ và mã của chúng."""
        return {lang.name.lower(): lang.value for lang in cls}

def get_file_extension(filename: str):
    return filename.split('.')[-1].lower()

# Hàm xác định MIME type của tệp từ nội dung
def get_mime_type(file_extension):
    mime_types = {
        "pdf": "application/pdf",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }
    
    # Chuyển file_extension về chữ thường để đảm bảo tính đúng đắn
    file_extension = file_extension.lower()
    
    # Trả về MIME type nếu có, nếu không trả về None
    return mime_types.get(file_extension, None)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Lấy danh sách ngôn ngữ từ class Language
    languages = Language.list_languages()

    # Tạo phần HTML cho các lựa chọn ngôn ngữ
    lang_options = "\n".join(
        f'<option value="{code}">{name.capitalize()}</option>' 
        for name, code in languages.items()
    )

    return HTMLResponse(
        f"""
        <html>
            <head>
                <link rel="stylesheet" href="/static/css/style.css">
            </head>
            <body>
                <form action="/translate/" method="post" enctype="multipart/form-data" onsubmit="handleFormSubmit(event)">
                    <h1>Welcome to File Translator</h1>
                
                    <label for="file">Choose a file:</label>
                    <input type="file" name="file" required>
                    <br><br>
                    
                    <label for="src_lang">Source Language:</label>
                    <select name="src_lang" id="src_lang">
                        {lang_options}
                    </select>
                    <br><br>
                    
                    <label for="trg_lang">Target Language:</label>
                    <select name="trg_lang" id="trg_lang">
                        {lang_options}
                    </select>
                    <br><br>
                    
                    <input type="submit" value="Translate">

                    <!-- Loading Spinner -->
                    <div id="spinner" class="spinner"></div>

                    <!-- Thông báo Translating -->
                    <div class="translating-message">Translating...</div>

                    <!-- Thông báo lỗi -->
                    <p id="error-message" style="color: red; display: none;">Source language and target language cannot be the same!</p>
                    
                </form>

                <script src="/static/js/form.js"></script>

            </body>
        </html>
        """
    )

@app.get("/files/", response_class=HTMLResponse)
async def list_translated_files():
    # Danh sách các file đã dịch
    files = os.listdir(TRANSLATED_DIRECTORY)
    files_links = [
        f'<li><a href="/download/{file}" target="_blank">{file}</a></li>' 
        for file in files
    ]
    files_html = "\n".join(files_links)

    # Thêm nút quay lại
    back_button = '<input type="button" value="Back" onclick="window.history.back()" />'
    
    # Tạo trang HTML
    html_content = f"""
    <html>
    <head>
        <title>List of translated files</title>
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body>
        <form>
            <h1>List of translated files</h1>
            <div class="file-list">
                <ul>
                    {files_html}
                </ul>
            </div>
            {back_button}
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/download/{file_name}")
async def download_file(file_name: str):
    file_path = os.path.join(TRANSLATED_DIRECTORY, file_name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=file_name)

@app.post("/translate/")
async def translate_pptx(
    file: UploadFile = File(...),
    src_lang: Language = Form(...),  # Ngôn ngữ nguồn
    trg_lang: Language = Form(...)   # Ngôn ngữ đích
):  
    # Lưu file người dùng tải lên
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    output_path = os.path.join(TRANSLATED_DIRECTORY, f"translated_{src_lang}2{trg_lang}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    # xác định loại file
    file_extension = get_file_extension(file.filename)
    logging.info(f"File extension: {file_extension}") 

    if file_extension == "pptx":
        slides_data = extract_text_with_powerpoint(file_path, config['model_translatation'], src_lang, trg_lang)
        create_translated_pptx(file_path, slides_data, output_path)

    elif file_extension == "xlsx":
        excel_data = extract_text_image_with_excel(file_path, config['model_translatation'], src_lang, trg_lang)
        create_translated_excel(file_path, excel_data, output_path)
        print("no error")

    elif file_extension == "pdf":
        translate_pdf(file_path, output_path, config['model_translatation'], src_lang, trg_lang)

    elif file_extension == "docx":
        # chuyển docx sang pdf
        pdf_file_path = os.path.join(UPLOAD_DIRECTORY, file.filename + ".pdf")
        pdf_output_path = os.path.join(TRANSLATED_DIRECTORY, f"translated_{file.filename}" + ".pdf")
        print(pdf_file_path, pdf_output_path)
        convert(file_path, pdf_file_path)
        # dịch file pdf
        translate_pdf(pdf_file_path, pdf_output_path, config['model_translatation'], src_lang, trg_lang)
        # chuyển pdf sau khi dịch về docx
        pdf_to_docx(pdf_output_path, output_path)
        # Xóa pdf tạm thời
        os.remove(pdf_file_path)
        os.remove(pdf_output_path)

    # Thêm loại file mới ở đây
        
    else:
        print("Unsupported file format")
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    save_file_to_db(file.filename, f"translated_{file.filename}", src_lang, trg_lang, file_path, output_path, None)
    print("đã lưu vào db")

    # Kiểm tra tệp đã được tạo ra và tồn tại hay chưa
    if not os.path.exists(output_path):
        print("Translated file could not be created.")
        raise HTTPException(status_code=500, detail="Translated file could not be created.")
    print(f"Tệp được lưu vào {output_path}")

    # Xác định MIME type của tệp từ nội dung
    mime_type = get_mime_type(file_extension)

    # Trả về file PowerPoint đã dịch
    return RedirectResponse(url="/files/", status_code=302)
    # return FileResponse(
    #     output_path,                 
    #     media_type=mime_type, 
    #     filename=f"translated_{src_lang}2{trg_lang}_{file.filename}"
    # )

import openai
from dotenv import load_dotenv
import os
from openai import OpenAI
import openai

# Load biến môi trường từ tệp .env
load_dotenv()

# Lấy API key từ biến môi trường
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please check your .env file.")

# Đặt API key
client = OpenAI(
    api_key=api_key
)

# Hàm dịch văn bản
def translate(text, src_lang, trg_lang):
    prompt = f"""
    You are a professional translator. Your task is to translate the following text accurately while preserving its original meaning, style, and context. Translate carefully without adding or omitting any information.

    - Source text:  
    "{text}"

    - Source language: "{src_lang}". If the text contains parts in other languages, also translate them into the target language.

    - Target language: "{trg_lang}"
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful translator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
        )
        translation = response.choices[0].message.content
        return translation.strip()
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Ví dụ: Dịch từ Tiếng Việt sang Tiếng Anh
    source_text = "Xin chào, bạn khỏe không?"
    translated_text = translate(source_text, "Vietnamese", "English")
    print("Translated Text:", translated_text)

# def translate(text, src_lang, trg_lang):
#     return text
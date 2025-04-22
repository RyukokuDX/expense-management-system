import os
import google.generativeai as genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def analyze_with_gemini(text):
    """Analyze text using Gemini API."""
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    以下の領収書の内容を分析し、以下の情報を抽出してください：
    1. 日付
    2. 金額
    3. 支払い方法
    4. 商品やサービスの詳細
    5. その他の重要な情報

    領収書の内容：
    {text}
    """
    
    response = model.generate_content(prompt)
    return response.text

def main():
    pdf_path = "若手研究：24K16957/pdf/receipt_7483827074.pdf"
    
    try:
        # Extract text from PDF
        print("PDFからテキストを抽出中...")
        text = extract_text_from_pdf(pdf_path)
        
        # Analyze with Gemini
        print("Gemini APIで分析中...")
        analysis = analyze_with_gemini(text)
        
        # Print results
        print("\n分析結果:")
        print(analysis)
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main() 
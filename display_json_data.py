import os
import json
import requests
from pathlib import Path

def analyze_with_gemini(text):
    """Analyze text using Gemini API."""
    api_key = os.environ['GeminiApiKey']
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash-001:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""
                        以下の領収書の内容を分析し、以下の情報を抽出してください：
                        1. 日付
                        2. 金額
                        3. 支払い方法
                        4. 商品やサービスの詳細
                        5. その他の重要な情報

                        領収書の内容：
                        {text}
                        """
                    }
                ]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()

def display_json_data(json_file_path):
    """Display JSON data from a file."""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        # Convert JSON data to formatted string
        json_text = json.dumps(data, ensure_ascii=False, indent=2)
        
        # Analyze with Gemini
        print("Gemini APIで分析中...")
        analysis = analyze_with_gemini(json_text)
        
        # Print the analysis results
        if 'candidates' in analysis and len(analysis['candidates']) > 0:
            print("\n分析結果:")
            print(analysis['candidates'][0]['content']['parts'][0]['text'])
        else:
            print("\n分析結果の取得に失敗しました。")
            print("APIレスポンス:", json.dumps(analysis, ensure_ascii=False, indent=2))
            
    except FileNotFoundError:
        print(f"エラー: ファイル '{json_file_path}' が見つかりません。")
    except json.JSONDecodeError:
        print(f"エラー: '{json_file_path}' は有効なJSONファイルではありません。")
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

def main():
    # Get the directory of the script
    script_dir = Path(__file__).parent
    
    # Find all JSON files in the directory
    json_files = list(script_dir.glob('*.json'))
    
    if not json_files:
        print("JSONファイルが見つかりません。")
        return
    
    # Display menu
    print("利用可能なJSONファイル:")
    for i, file in enumerate(json_files, 1):
        print(f"{i}. {file.name}")
    
    # Get user input
    while True:
        try:
            choice = int(input("\n表示するファイルの番号を入力してください: "))
            if 1 <= choice <= len(json_files):
                break
            print("無効な番号です。もう一度試してください。")
        except ValueError:
            print("数字を入力してください。")
    
    # Display selected file
    selected_file = json_files[choice - 1]
    print(f"\n{selected_file.name} の内容:")
    display_json_data(selected_file)

if __name__ == "__main__":
    main() 
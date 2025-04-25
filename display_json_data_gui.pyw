import os
import json
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from collections import defaultdict
import webbrowser
import sys
import glob
import google.generativeai as genai
import re
import base64
from PIL import Image
import io
from pdf2image import convert_from_path
from pathlib import Path
import httpx

# スクリプトのディレクトリを取得
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Gemini APIの設定
GEMINI_API_KEY = os.environ.get('GeminiApiKey')
if not GEMINI_API_KEY:
    # 環境変数にAPIキーが設定されていない場合、ここで直接設定
    # 注意: 本番環境では、APIキーをソースコードに直接記述することは避けてください
    GEMINI_API_KEY = "YOUR_API_KEY_HERE"  # ここに実際のAPIキーを入力してください
    print("Warning: Using hardcoded API key. For security reasons, consider using environment variables.")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro-vision')
else:
    print("Warning: GeminiApiKey not set. PDFからのJSON自動生成機能は無効です。")

def extract_json_from_pdf_sync(pdf_path):
    """
    PDFファイルからJSONデータを抽出する同期関数
    """
    try:
        if not GEMINI_API_KEY:
            print("Missing GEMINI API key.")
            return None

        # PDFデータを Base64 に変換
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        pdf_base64 = base64.b64encode(pdf_data).decode("utf-8")

        # Gemini API にリクエスト
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": "領収書または納品書の情報を解析し、購入項目ごとに以下の形式でJSONに構造化してください。ただし、以下の処理を施してください。\n"
                                    "+ 金額の部分はカンマがあれば除いてください\n"
                                    "+ 金額が0の項目は無視してください\n\n"
                                    "{ \"title\": \"領収書タイトル\", \"issuer\": \"発行者情報\", \"receiver_group\": \"受領者所属\", \"receiver_name\": \"受領者氏名(敬称、空白は除く)\", \"total_amount\": \"合計金額\", \"payment_date\": \"支払日\", \"items\": [ { \"product_name\": \"製品名(型番は抜く)\", \"provider\": \"メーカー\", \"model\": \"型番\", \"unite_price\": \"単価\", \"total_price\": \"金額\", \"number\": \"個数\", \"delivery_date\": \"発送日\" } ] }"
                        },
                        {
                            "inlineData": {
                                "mimeType": "application/pdf",
                                "data": pdf_base64
                            }
                        }
                    ]
                }
            ]
        }

        # 同期HTTPリクエスト
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash-001:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json=payload
        )

        json_response = response.json()

        if response.status_code != 200:
            print(f"Gemini API error: {json_response}")
            return None

        # JSON部分の抽出
        extracted_text = json_response.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "{}")
        extracted_json_match = re.search(r"```json\n([\s\S]+?)\n```", extracted_text)

        if extracted_json_match:
            extracted_json = json.loads(extracted_json_match.group(1))
            return extracted_json
        else:
            print("No JSON found in response")
            return None

    except Exception as e:
        print(f"Error extracting JSON from PDF: {e}")
        return None

def check_and_generate_json_for_pdfs():
    """
    PDFファイルに対応するJSONファイルがない場合、Gemini APIを使用してJSONを生成する
    """
    # PDFファイルを検索
    pdf_files = glob.glob(os.path.join(SCRIPT_DIR, "**", "pdf", "*.pdf"), recursive=True)
    
    for pdf_path in pdf_files:
        # 対応するJSONファイルのパスを生成
        json_dir = os.path.dirname(os.path.dirname(pdf_path))
        json_dir = os.path.join(json_dir, "json")
        pdf_filename = os.path.basename(pdf_path)
        json_filename = os.path.splitext(pdf_filename)[0] + ".json"
        json_path = os.path.join(json_dir, json_filename)
        
        # JSONファイルが存在しない場合
        if not os.path.exists(json_path):
            print(f"JSON file not found for PDF: {pdf_path}")
            
            # extract_json_from_pdf_sync関数を使用してJSONを生成
            generated_json = extract_json_from_pdf_sync(pdf_path)
            
            if generated_json:
                # JSONディレクトリが存在しない場合は作成
                os.makedirs(json_dir, exist_ok=True)
                
                # JSONファイルを保存
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(generated_json, f, ensure_ascii=False, indent=2)
                
                print(f"Generated JSON file: {json_path}")
            else:
                print(f"Failed to generate JSON for PDF: {pdf_path}")

def list_json_files(directory):
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        # submissionフィールドが存在しない場合は追加
        if 'submission' not in data:
            data['submission'] = ''
            # 変更を保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        return data

def parse_date(date_str):
    try:
        # Try to parse the date string with different formats
        for fmt in ['%Y/%m/%d', '%Y-%m-%d']:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.month, date_obj.day
            except ValueError:
                continue
        # If none of the formats work, return default values
        print(f"Warning: Could not parse date '{date_str}'. Using default values.")
        return 1, 1
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}. Using default values.")
        return 1, 1

def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    print(f"Copied to clipboard: {text}")

def get_pdf_path_from_json(json_path):
    """
    JSONファイルのパスから対応するPDFファイルのパスを生成します。
    """
    # パスを正規化（区切り文字を統一）
    normalized_path = os.path.normpath(json_path)
    
    # ディレクトリとファイル名に分割
    directory = os.path.dirname(normalized_path)
    filename = os.path.basename(normalized_path)
    
    # jsonディレクトリをpdfディレクトリに置き換え
    if 'json' in directory:
        pdf_directory = directory.replace('json', 'pdf')
    else:
        # jsonディレクトリが見つからない場合は、同じディレクトリ内のpdfディレクトリを探す
        parent_dir = os.path.dirname(directory)
        pdf_directory = os.path.join(parent_dir, 'pdf')
    
    # ファイル名の拡張子を.pdfに変更
    pdf_filename = os.path.splitext(filename)[0] + '.pdf'
    
    # PDFファイルのパスを生成
    pdf_path = os.path.join(pdf_directory, pdf_filename)
    
    print(f"JSON path: {json_path}")
    print(f"PDF path: {pdf_path}")
    print(f"PDF exists: {os.path.exists(pdf_path)}")
    
    return pdf_path

def open_pdf(pdf_path):
    if os.path.exists(pdf_path):
        print(f"Opening PDF: {pdf_path}")
        webbrowser.open(pdf_path)
    else:
        print(f"PDF file not found: {pdf_path}")

def edit_json_file(json_path):
    """
    JSONファイルを編集するための関数
    """
    try:
        # JSONファイルを読み込む
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 編集用のウィンドウを作成
        edit_window = tk.Toplevel()
        edit_window.title(f"JSON Editor - {os.path.basename(json_path)}")
        edit_window.geometry("800x600")
        
        # テキストエリアを作成
        text_area = tk.Text(edit_window, wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 現在のJSONデータを整形して表示
        text_area.insert('1.0', json.dumps(data, ensure_ascii=False, indent=2))
        
        def save_changes():
            try:
                # テキストエリアの内容を取得
                new_content = text_area.get('1.0', tk.END)
                # JSONとして解析
                new_data = json.loads(new_content)
                # ファイルに保存
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=2)
                messagebox.showinfo("成功", "JSONファイルを保存しました")
                edit_window.destroy()
                
                # 現在のタブの内容を更新
                current_tab = notebook.select()
                tab_frame = notebook.children[current_tab.split('.')[-1]]
                folder_name = notebook.tab(current_tab)['text']
                
                # 既存のウィジェットを削除
                for widget in tab_frame.winfo_children():
                    widget.destroy()
                
                # タブの内容を再描画
                create_tab_content(tab_frame, folder_files[folder_name])
                
            except json.JSONDecodeError:
                messagebox.showerror("エラー", "無効なJSON形式です")
            except Exception as e:
                messagebox.showerror("エラー", f"保存中にエラーが発生しました: {str(e)}")
        
        # 保存ボタン
        save_button = ttk.Button(edit_window, text="保存", command=save_changes)
        save_button.pack(pady=10)
        
    except Exception as e:
        messagebox.showerror("エラー", f"JSONファイルを開けませんでした: {str(e)}")

def create_tab_content(tab_frame, files):
    """
    タブの内容を作成する関数
    """
    # スクロール可能なフレームを作成
    canvas = tk.Canvas(tab_frame)
    scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # ヘッダー行を作成
    headers = ['月', '日', '経費種目', '発行元', '品目', '業者', '品番', '個数', '領収書等', '関連処理', '金額', '提出日時', 'JSON', '削除']
    for i, header in enumerate(headers):
        label = ttk.Label(scrollable_frame, text=header, font=('Helvetica', 12, 'bold'), relief="solid", borderwidth=1)
        label.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
    
    # グリッドの列の重みを設定
    for i in range(len(headers)):
        scrollable_frame.grid_columnconfigure(i, weight=1)
    
    # JSONファイルの処理
    row = 1
    
    # 日付でソートするためのデータを収集
    items_data = []
    for json_file in files:
        try:
            json_data = read_json_file(json_file)
            print(f"Processing {json_file}: {json_data}")
            
            # 日付を取得
            date_str = json_data.get('payment_date', '')
            try:
                # 日付を解析
                for fmt in ['%Y/%m/%d', '%Y-%m-%d']:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        break
                    except ValueError:
                        continue
            except Exception:
                # 日付が解析できない場合は現在の日付を使用
                date_obj = datetime.now()
            
            for item in json_data['items']:
                # データを収集
                items_data.append({
                    'date': date_obj,
                    'json_file': json_file,
                    'item': item,
                    'json_data': json_data
                })
        except Exception as e:
            print(f"Error processing {json_file}: {e}")
    
    # 日付の降順（新しい順）にソート
    items_data.sort(key=lambda x: x['date'], reverse=True)
    
    # ソートされたデータを表示
    for data in items_data:
        json_file = data['json_file']
        item = data['item']
        json_data = data['json_data']
        date_obj = data['date']
        
        # 月と日を取得
        month = date_obj.month
        day = date_obj.day
        
        # 金額の処理 - 文字列の場合はそのまま使用、数値の場合はフォーマット
        total_price = item.get('total_price', '0')
        if isinstance(total_price, str):
            # 文字列の場合はそのまま使用
            price_display = f"{total_price}円"
        else:
            # 数値の場合はフォーマット
            price_display = f"{int(total_price):,}円"
        
        # JSONファイルのパスからPDFファイルのパスを生成
        pdf_file_path = get_pdf_path_from_json(json_file)
        pdf_file_name = os.path.basename(pdf_file_path)
        
        # PDFファイルが存在するか確認
        if os.path.exists(pdf_file_path):
            receipt_text = f"{json_data.get('title', '領収書')}: {pdf_file_name}"
        else:
            receipt_text = "PDFファイルが見つかりません"
        
        # 個数を取得
        quantity = item.get('number', '')
        
        # データを表示
        values = [
            month,
            day,
            '物品費',
            json_data.get('issuer', ''),
            item.get('product_name', ''),
            item.get('provider', ''),
            item.get('model', ''),
            quantity,
            receipt_text,
            '',
            price_display,
            json_data.get('submission', ''),  # 提出日時
            f"📝 {os.path.basename(json_file)}",  # JSONボタン
            ""  # 削除ボタン
        ]
        
        # 各列にデータを表示
        for i, value in enumerate(values):
            # セルフレームを作成
            cell_frame = ttk.Frame(scrollable_frame, relief="solid", borderwidth=1)
            cell_frame.grid(row=row, column=i, sticky="nsew", padx=1, pady=1)
            
            # コピーボタンのクリックイベントを作成する関数
            def make_copy_command(val=value, col_index=i):
                def copy_command():
                    # 金額の場合は「円」を除く
                    if col_index == 10:  # 金額の列インデックス
                        copy_value = str(val).replace('円', '').replace(',', '').strip()
                    else:
                        copy_value = str(val)
                    
                    copy_to_clipboard(copy_value)
                    
                    # コピーしたことを示すラベルを表示
                    copy_label = ttk.Label(tab_frame, text=f"{headers[col_index]}: {copy_value} をコピーしました", foreground="green")
                    copy_label.place(relx=0.5, rely=0.95, anchor="center")
                    
                    # 1秒後にラベルを消す
                    root.after(1000, copy_label.destroy)
                
                return copy_command
            
            if i == 11:  # 提出日時列の場合
                def make_submission_command(json_path=json_file, cell_frame=cell_frame):
                    def submission_command():
                        try:
                            # JSONファイルを読み込む
                            with open(json_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            # 現在の日時を設定
                            current_time = datetime.now().strftime('%Y/%m/%d %H:%M')
                            data['submission'] = current_time
                            
                            # JSONファイルを保存
                            with open(json_path, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False, indent=2)
                            
                            # 表示を更新
                            for widget in cell_frame.winfo_children():
                                widget.destroy()
                            
                            # 値のラベル
                            value_label = ttk.Label(cell_frame, text=current_time, wraplength=150)
                            value_label.pack(side="left", fill="both", expand=True, padx=5, pady=5)
                            
                            # 提出ボタン
                            submit_button = ttk.Button(cell_frame, text="📅", width=2)
                            submit_button.pack(side="right", padx=2, pady=2)
                            submit_button.configure(command=submission_command)
                            
                            # コピーボタン
                            copy_button = ttk.Button(cell_frame, text="📋", width=2)
                            copy_button.pack(side="right", padx=2, pady=2)
                            copy_button.configure(command=make_copy_command(current_time))
                            
                            messagebox.showinfo("成功", "提出日時を記録しました")
                        except Exception as e:
                            messagebox.showerror("エラー", f"提出日時の記録中にエラーが発生しました: {str(e)}")
                    return submission_command
                
                # 値のラベル
                value_label = ttk.Label(cell_frame, text=str(value), wraplength=150)
                value_label.pack(side="left", fill="both", expand=True, padx=5, pady=5)
                
                # 提出ボタン
                submit_button = ttk.Button(cell_frame, text="📅", width=2)
                submit_button.pack(side="right", padx=2, pady=2)
                submit_button.configure(command=make_submission_command())
                
                # コピーボタン
                copy_button = ttk.Button(cell_frame, text="📋", width=2)
                copy_button.pack(side="right", padx=2, pady=2)
                copy_button.configure(command=make_copy_command())
            
            elif i == 13:  # 削除列の場合
                def make_delete_command(json_path=json_file):
                    def delete_command():
                        # 削除確認ダイアログを表示
                        if messagebox.askyesno("確認", "このレコードを削除してもよろしいですか？\nこの操作は取り消せません。"):
                            try:
                                # JSONファイルを削除
                                os.remove(json_path)
                                # 対応するPDFファイルも削除（オプション）
                                pdf_path = get_pdf_path_from_json(json_path)
                                if os.path.exists(pdf_path):
                                    if messagebox.askyesno("確認", "対応するPDFファイルも削除しますか？"):
                                        os.remove(pdf_path)
                                # 表示を更新
                                refresh_display()
                                messagebox.showinfo("成功", "レコードを削除しました")
                            except Exception as e:
                                messagebox.showerror("エラー", f"削除中にエラーが発生しました: {str(e)}")
                    return delete_command
                
                delete_button = ttk.Button(cell_frame, text="🗑️", width=2)
                delete_button.pack(expand=True)
                delete_button.configure(command=make_delete_command())
            else:
                # 値のラベル
                value_label = ttk.Label(cell_frame, text=str(value), wraplength=150)
                value_label.pack(side="left", fill="both", expand=True, padx=5, pady=5)
                
                # コピーボタン
                copy_button = ttk.Button(cell_frame, text="📋", width=2)
                copy_button.pack(side="right", padx=2, pady=2)
                copy_button.configure(command=make_copy_command())
                
                # 領収書等の場合は、PDFファイルを開くボタンを追加
                if i == 8 and value and not value.startswith('PDFファイルが見つかりません'):
                    def make_open_pdf_command(pdf_path=pdf_file_path):
                        def open_pdf_command():
                            open_pdf(pdf_path)
                        return open_pdf_command
                    
                    open_button = ttk.Button(cell_frame, text="📄", width=2)
                    open_button.pack(side="right", padx=2, pady=2)
                    open_button.configure(command=make_open_pdf_command())
                
                # JSONボタンの場合は、JSONファイルを開くボタンを追加
                if i == 12:  # JSON列の場合
                    def make_edit_command(json_path=json_file):
                        def edit_command():
                            edit_json_file(json_path)
                        return edit_command
                    
                    edit_button = ttk.Button(cell_frame, text="📝", width=2)
                    edit_button.pack(side="right", padx=2, pady=2)
                    edit_button.configure(command=make_edit_command())
        
        row += 1
    
    # スクロールバーとキャンバスを配置
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def refresh_display():
    """ディレクトリ構造やファイルの変化を検知して表示を更新する"""
    global notebook, folder_files
    directory = SCRIPT_DIR
    
    # PDFファイルに対応するJSONファイルがない場合、Gemini APIを使用してJSONを生成
    check_and_generate_json_for_pdfs()
    
    # JSONファイルを再取得
    json_files = list_json_files(directory)
    folder_files = defaultdict(list)
    for json_file in json_files:
        folder_name = os.path.basename(os.path.dirname(os.path.dirname(json_file)))
        folder_files[folder_name].append(json_file)
    
    # 現在のタブの状態を保存
    current_tab = notebook.select()
    current_folder = notebook.tab(current_tab)['text'] if current_tab else None
    
    # 既存のタブをすべて削除
    for tab in notebook.tabs():
        notebook.forget(tab)
    
    # 各フォルダごとにタブを作成
    for folder_name, files in folder_files.items():
        # タブのフレーム
        tab_frame = ttk.Frame(notebook)
        notebook.add(tab_frame, text=folder_name)
        
        # タブの内容を作成
        create_tab_content(tab_frame, files)
    
    # 以前選択していたタブを復元（存在する場合）
    if current_folder:
        for tab in notebook.tabs():
            if notebook.tab(tab)['text'] == current_folder:
                notebook.select(tab)
                break
    
    # 更新完了メッセージを表示
    message_label = ttk.Label(root, text="表示を更新しました", foreground="green")
    message_label.place(relx=0.5, rely=0.95, anchor="center")
    root.after(1000, message_label.destroy)

def display_json_data_gui():
    global root, notebook, folder_files
    root = tk.Tk()
    root.title('JSON データ表示')
    
    # フォントサイズを大きくする
    default_font = ('Helvetica', 12)
    root.option_add('*Font', default_font)
    
    # タブのスタイルを設定
    style = ttk.Style()
    # ノートブック全体のスタイル
    style.configure('TNotebook', background='#d0d0d0', borderwidth=2)
    # タブのスタイル
    style.configure('TNotebook.Tab', 
                   background='#c0c0c0',
                   padding=[15, 5],
                   borderwidth=1,
                   relief='solid')
    # 選択時のタブのスタイル
    style.map('TNotebook.Tab',
              background=[('selected', '#ffffff')],
              foreground=[('selected', '#000000')],
              relief=[('selected', 'solid')])
    
    # APIキーがない場合の警告メッセージ
    if not GEMINI_API_KEY:
        warning_frame = ttk.Frame(root)
        warning_frame.pack(fill='x', padx=5, pady=5)
        warning_label = ttk.Label(warning_frame, text="⚠️ GeminiApiKey環境変数が設定されていません。PDFからのJSON自動生成機能は無効です。", foreground="red")
        warning_label.pack(side='left')
    
    # メインフレーム
    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True)
    
    # 更新ボタンのフレーム
    refresh_frame = ttk.Frame(main_frame)
    refresh_frame.pack(fill='x', padx=5, pady=5)
    
    # 更新ボタン
    refresh_button = ttk.Button(refresh_frame, text="🔄 更新", command=refresh_display)
    refresh_button.pack(side='right')
    
    # フォルダごとにJSONファイルをグループ化
    directory = SCRIPT_DIR  # スクリプトのディレクトリを使用
    json_files = list_json_files(directory)
    
    # JSON ファイルの一覧を出力
    print(f"Found {len(json_files)} JSON files in {directory}:")
    for json_file in json_files:
        print(f"  - {json_file}")
    
    if not json_files:
        print("No JSON files found. Please check the directory.")
        # メッセージを表示
        message_label = ttk.Label(main_frame, text="JSON ファイルが見つかりません", font=('Helvetica', 14))
        message_label.pack(pady=20)
        root.mainloop()
        return
    
    # フォルダごとにJSONファイルをグループ化
    folder_files = defaultdict(list)
    for json_file in json_files:
        # フォルダ名を取得（実験実習費/json/20250414141658.json から 実験実習費 を取得）
        folder_name = os.path.basename(os.path.dirname(os.path.dirname(json_file)))
        folder_files[folder_name].append(json_file)
    
    # ノートブック（タブ）の作成
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill='both', expand=True, padx=5, pady=5)
    
    # 各フォルダごとにタブを作成
    for folder_name, files in folder_files.items():
        # タブのフレーム
        tab_frame = ttk.Frame(notebook)
        notebook.add(tab_frame, text=folder_name)
        
        # タブの内容を作成
        create_tab_content(tab_frame, files)
    
    root.mainloop()

if __name__ == '__main__':
    display_json_data_gui() 
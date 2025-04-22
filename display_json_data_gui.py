import os
import json
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from collections import defaultdict
import webbrowser

def list_json_files(directory):
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                json_files.append(os.path.join(root, file))
    return json_files

def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

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

def display_json_data_gui():
    global root
    root = tk.Tk()
    root.title('JSON データ表示')
    
    # フォントサイズを大きくする
    default_font = ('Helvetica', 12)
    root.option_add('*Font', default_font)
    
    # メインフレーム
    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True)
    
    # フォルダごとにJSONファイルをグループ化
    directory = '.'  # カレントディレクトリ
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
    notebook.pack(fill='both', expand=True)
    
    # 各フォルダごとにタブを作成
    for folder_name, files in folder_files.items():
        # タブのフレーム
        tab_frame = ttk.Frame(notebook)
        notebook.add(tab_frame, text=folder_name)
        
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
        headers = ['月', '日', '経費種目', '発行元', '品目', '業者', '品番', '個数', '領収書等', '事務処理関連書類', '金額', 'その他']
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
                        'item': item
                    })
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
        
        # 日付の降順（新しい順）にソート
        items_data.sort(key=lambda x: x['date'], reverse=True)
        
        # ソートされたデータを表示
        for data in items_data:
            json_file = data['json_file']
            item = data['item']
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
                receipt_text = f"領収書: {pdf_file_name}"
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
                ''
            ]
            
            # 各列にデータを表示
            for i, value in enumerate(values):
                # セルフレームを作成
                cell_frame = ttk.Frame(scrollable_frame, relief="solid", borderwidth=1)
                cell_frame.grid(row=row, column=i, sticky="nsew", padx=1, pady=1)
                
                # 値のラベル
                value_label = ttk.Label(cell_frame, text=str(value), wraplength=150)
                value_label.pack(side="left", fill="both", expand=True, padx=5, pady=5)
                
                # コピーボタン
                copy_button = ttk.Button(cell_frame, text="📋", width=2)
                copy_button.pack(side="right", padx=2, pady=2)
                
                # コピーボタンのクリックイベント
                def make_copy_command(val=value):
                    def copy_command():
                        # 金額の場合は「円」を除く
                        if i == 11:  # 金額の列インデックス
                            copy_value = str(val).replace('円', '').strip()
                        else:
                            copy_value = str(val)
                        
                        copy_to_clipboard(copy_value)
                        
                        # コピーしたことを示すラベルを表示
                        copy_label = ttk.Label(tab_frame, text=f"{headers[i]}: {copy_value} をコピーしました", foreground="green")
                        copy_label.place(relx=0.5, rely=0.95, anchor="center")
                        
                        # 1秒後にラベルを消す
                        root.after(1000, copy_label.destroy)
                    
                    return copy_command
                
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
            
            row += 1
        
        # スクロールバーとキャンバスを配置
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    root.mainloop()

if __name__ == '__main__':
    display_json_data_gui() 
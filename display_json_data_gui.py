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
        # テーブルにメッセージを表示
        tree = ttk.Treeview(main_frame)
        tree['columns'] = ('月', '日', '経費種目', '品目', '発行元', '品番', '個数', '領収書等', '事務処理関連書類', '金額', 'その他')
        tree['show'] = 'headings'
        
        # カラムの設定
        for column in tree['columns']:
            tree.heading(column, text=column)
            tree.column(column, width=150)  # 幅を広げる
        
        # スクロールバーの追加
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # テーブルとスクロールバーの配置
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        tree.insert('', 'end', values=('', '', '', 'JSON ファイルが見つかりません', '', '', '', '', '', '', ''))
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
        
        # テーブルの作成
        tree = ttk.Treeview(tab_frame)
        tree['columns'] = ('月', '日', '経費種目', '品目', '発行元', '品番', '個数', '領収書等', '事務処理関連書類', '金額', 'その他')
        tree['show'] = 'headings'
        
        # カラムの設定
        for column in tree['columns']:
            tree.heading(column, text=column)
            tree.column(column, width=150)  # 幅を広げる
        
        # 罫線を表示するためのスタイル設定
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)  # 行の高さを設定
        style.configure("Treeview", background="#ffffff", foreground="black", fieldbackground="#ffffff")
        style.configure("Treeview.Heading", font=('Helvetica', 12, 'bold'))
        
        # 罫線を表示するための設定
        style.configure("Treeview", borderwidth=1, relief="solid")
        style.configure("Treeview.Cell", borderwidth=1, relief="solid")
        
        # スクロールバーの追加
        scrollbar = ttk.Scrollbar(tab_frame, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # テーブルとスクロールバーの配置
        tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # セルクリック時のコピー機能を設定
        def on_cell_click(event):
            item = tree.identify_row(event.y)
            if not item:
                return
            
            column = tree.identify_column(event.x)
            if not column:
                return
            
            # カラム名を取得
            col_name = tree['columns'][int(column[1]) - 1]
            
            # アイテムの値を取得
            values = tree.item(item, 'values')
            if not values:
                return
            
            # カラムのインデックスを取得
            col_idx = int(column[1]) - 1
            if col_idx >= len(values):
                return
            
            # 値を取得
            value = values[col_idx]
            if not value:
                return
            
            # 領収書等のカラムの場合は、PDFファイルを開く
            if col_name == '領収書等' and value and not value.startswith('PDFファイルが見つかりません'):
                # JSONファイルのパスからPDFファイルのパスを生成
                json_file_path = tree.item(item, 'tags')[0]  # JSONファイルのパスをタグから取得
                pdf_file_path = get_pdf_path_from_json(json_file_path)
                open_pdf(pdf_file_path)
                return
            
            # クリップボードにコピー
            copy_to_clipboard(value)
            
            # コピーしたことを示すラベルを表示
            copy_label = ttk.Label(tab_frame, text=f"{col_name}: {value} をコピーしました", foreground="green")
            copy_label.place(relx=0.5, rely=0.95, anchor="center")
            
            # 1秒後にラベルを消す
            root.after(1000, copy_label.destroy)
        
        # クリックイベントをバインド
        tree.bind('<ButtonRelease-1>', on_cell_click)
        
        # JSONファイルの処理
        for json_file in files:
            try:
                json_data = read_json_file(json_file)
                print(f"Processing {json_file}: {json_data}")
                for item in json_data['items']:
                    date = json_data.get('payment_date', '')
                    month, day = parse_date(date)
                    
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
                    
                    values = (
                        month,
                        day,
                        '物品費',
                        item.get('product_name', ''),
                        item.get('provider', ''),
                        item.get('model', ''),
                        quantity,
                        receipt_text,
                        '',
                        price_display,
                        ''
                    )
                    
                    # アイテムを挿入し、JSONファイルのパスをタグとして保存
                    item_id = tree.insert('', 'end', values=values, tags=(json_file,))
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
    
    root.mainloop()

if __name__ == '__main__':
    display_json_data_gui() 
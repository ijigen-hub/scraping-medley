import json
import math
from typing import List, Dict, Any
from pprint import pprint
from playwright.sync_api import sync_playwright
import os
import sys
import argparse
from modules.scraper import JobMedleyScraper
from modules.get_ss_data import get_columns_data_from_sheet
from modules.upload_csv_to_gss import transfer_csv_to_sheet
from modules.create_date_string import create_date_string, create_yesterday_yyyymmdd
from modules.write_unhit_to_gss import write_data_to_sheet

def load_json(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(script_dir, filename)
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', help='jobmedley//eference_codes.json')
    args = parser.parse_args()

    file_path = args.data_path or default_path

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {filename} at {file_path}")
        print("Please ensure the file exists or specify the correct path.")
        sys.exit(1)

def get_user_input(prompt, options):
    while True:
        print(prompt)
        pprint(options, indent=2)
        choice = input("選択してください: ").strip()
        
        if isinstance(options, dict):
            if choice in options:
                return choice, options[choice]
            if choice in options.values():
                return next(key for key, value in options.items() if value == choice), choice
                    
        print("無効な選択です。もう一度お試しください。")

# 昨日の日付を取得してフォーマットする
def create_updated_data_string():
    datestring = create_date_string()
    return f"{datestring}-更新データ"

def get_job_type(e_data):
    if "ケアマネ" in e_data:
        return "cm"
    elif "看護助手" in e_data:
        return "na"
    elif "看護" in e_data:
        return "ans"
    elif "介護" in e_data:
        return "hh"
    elif "生活相談員" in e_data:
        return "la"
    elif "サービス提供責任者" in e_data:
        return "km"
    elif "栄養士" in e_data:
        return "nrd"
    elif "調理師" in e_data:
        return "ck"
    elif "児童指導員" in e_data:
        return "apl"
    elif "サービス管理責任者" in e_data:
        return "dcm"
    elif "児童発達支援管理責任者" in e_data:
        return "nm"
    elif "生活支援員" in e_data:
        return "ls"
    elif "保健師" in e_data:
        return "phn"
    elif "歯科衛生士" in e_data:
        return "dh"
    elif "言語聴覚士" in e_data:
        return "st"
    elif "理学療法士" in e_data:
        return "pt"
    elif "作業療法士" in e_data:
        return "ot"
    else:
        return None  # どちらの文字列も含まれていない場合

def main():
    sheet_name = create_updated_data_string()

    try:
        facility_data, job_type_data = get_columns_data_from_sheet(sheet_name)
    except:
            # シートがない場合はエラーログを出力して終了
            print(f"シート '{sheet_name}' はありません。")
            return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        is_all = False
        
        scraper = JobMedleyScraper(page)
        
        is_all = True
        for facility, job_type in zip(facility_data, job_type_data):
            # for code in range(1, 48):
            # pref_name = None
            # for region, prefectures in data['prefectures'].items():
            #     for name, code_value in prefectures.items():
            #         if code_value == code:
            #             pref_name = name
            #             break
            #     if pref_name:
            #         break
            
            job_type_cat = get_job_type(job_type)

            # url = f"https://job-medley.com/{job_type}/pref{code}/"
            url = f"https://job-medley.com/{job_type_cat}/search/?q={facility}"
            page.goto(url)
            
            job_count_element = page.query_selector('.c-search-condition-title__important')
            if job_count_element:
                job_count = int(job_count_element.inner_text())
            else:
                print("求人数の要素が見つかりません。")
                job_count = 0

            total_pages = math.ceil(job_count / 30)

            print(f"{facility}の求人数: {job_count}")
            print(f"総ページ数: {total_pages}")

            try:
                if job_count > 0:
                    scraper.scrape_jobs(job_type=job_type_cat, facility=facility, total_jobs=job_count, is_all=is_all, job_type_origin = job_type)
                    print("スクレイピングが正常に完了しました。")
                else:
                    unhit_facility = {
                                "開拓日": create_yesterday_yyyymmdd(),
                                "施設名": facility,
                                "職種": job_type
                            }
                    write_data_to_sheet([unhit_facility])
            except SystemExit as e:
                if e.code == 0:
                    print("ハローワーク求人が検出されたため、スクレイピングが途中で終了しました。")
                    break
                else:
                    print(f"予期せぬエラーが発生しました: {e}")
            except Exception as e:
                print(f"エラーが発生しました: {e}")

    datestring = create_date_string()
    filepath = f"./output/{datestring}.csv"
    transfer_csv_to_sheet(filepath, datestring)

if __name__ == "__main__":
    main()
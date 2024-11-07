import json
import math
from typing import List, Dict, Any
from pprint import pprint
from playwright.sync_api import sync_playwright
import os
import sys
import argparse
from modules.scraper import JobMedleyScraper


# def load_json(filename):
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     default_path = os.path.join(script_dir, filename)
    
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--data-path', help='jobmedley//eference_codes.json')
#     args = parser.parse_args()

#     file_path = args.data_path or default_path

#     try:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         print(f"Error: Could not find {filename} at {file_path}")
#         print("Please ensure the file exists or specify the correct path.")
#         sys.exit(1)


    #介護
    #介護職/ヘルパー・生活相談員・サービス提供責任者・ケアマネジャー　他14職種
    # if "介護職/ヘルパー" in e_data:
    #     return "hh"
    # elif "生活相談員" in e_data:
    #     return "la"
    # elif "ケアマネジャー" in e_data:
    #     return "cm"
    # elif "介護" in e_data:
    #     return "hh"
    # elif "生活相談員" in e_data:
    #     return "la"
    # elif "管理職（介護）" in e_data:
    #     return "mg"
    # elif "サービス提供責任者" in e_data:
    #     return "km"
    # elif "生活支援員" in e_data:
    #     return "ls"
    # elif "福祉用具専門相談員" in e_data:
    #     return "apl"
    # elif "児童発達支援管理責任者" in e_data:
    #     return "nm"
    # elif "サービス管理責任者" in e_data:
    #     return "dcm"
    # elif "児童指導員/指導員" in e_data:
    #     return "apl"
    # elif "看護師/准看護師" in e_data:
    #     return "ans"
    # elif "管理栄養士/栄養士" in e_data:
    #     return "nrd"
    # elif "調理師/調理スタッフ" in e_data:
    #     return "ck"
    # elif "介護タクシー/ドライバー" in e_data:
    #     return "ctd"
    # elif "医療事務/受付" in e_data:
    #     return "mc"
    # elif "営業/管理部門/その他" in e_data:
    #     return "etc"
    # elif "介護事務" in e_data:
    #     return "cc"
    # elif "相談支援専門員" in e_data:
    #     return "dm"
    # #リハビリ／代替医療
    # #理学療法士・作業療法士・柔道整復師・鍼灸師　他4職種
    # elif "理学療法士" in e_data:
    #     return "pt"
    # elif "言語聴覚士" in e_data:
    #     return "st"
    # elif "作業療法士" in e_data:
    #     return "ot"
    # elif "視能訓練士" in e_data:
    #     return "ort"
    # elif "柔道整復師" in e_data:
    #     return "jdr"
    # elif "あん摩マッサージ指圧師" in e_data:
    #     return "mas"
    # elif "鍼灸師" in e_data:
    #     return "acu"
    # elif "整体師" in e_data:
    #     return "bwt"
    # #歯科
    # #歯科医師・歯科衛生士・歯科助手・歯科技工士
    # elif "歯科医師" in e_data:
    #     return "dds"
    # elif "歯科衛生士" in e_data:
    #     return "dh"
    # elif "歯科技工士" in e_data:
    #     return "dt"
    # elif "歯科助手" in e_data:
    #     return "da"
    # #保育
    # #保育士・幼稚園教諭・児童発達支援管理責任者・保育補助　他5職種
    # elif "保育士" in e_data:
    #     return "cw"
    # elif "幼稚園教諭" in e_data:
    #     return "kt"
    # elif "保育補助" in e_data:
    #     return "acw"
    # elif "児童指導員/指導員" in e_data:
    #     return "apl"
    # elif "児童発達支援管理責任者" in e_data:
    #     return "nm"
    # elif "看護師/准看護師" in e_data:
    #     return "ans"
    # elif "放課後児童支援員/学童指導員" in e_data:
    #     return "asc"
    # #医科
    # # 看護師/准看護師・薬剤師・看護助手・臨床検査技師　他13職種
    # elif "医師" in e_data:
    #     return "dr"
    # elif "薬剤師" in e_data:
    #     return "apo"
    # elif "助産師" in e_data:
    #     return "mn"
    # elif "保健師" in e_data:
    #     return ""
    # elif "看護助手" in e_data:
    #     return "na"
    # elif "診療放射線技師" in e_data:
    #     return "rt"
    # elif "臨床検査技師" in e_data:
    #     return "mt"
    # elif "臨床工学技士" in e_data:
    #     return "ce"
    # elif "公認心理師/臨床心理士" in e_data:
    #     return "cp"
    # elif "医療ソーシャルワーカー" in e_data:
    #     return "csw"
    # elif "登録販売者" in e_data:
    #     return "otc"
    # elif "治験コーディネーター" in e_data:
    #     return "crc"
    # elif "調剤事務" in e_data:
    #     return "pc"
    # else:
    #     return None  # どちらの文字列も含まれていない場合


def main():
        #職種ーアプファベット対応関係
    job_types_connection = {
    "hh": "介護職/ヘルパー",
    "la": "生活相談員",
    "cm": "ケアマネジャー",
    "mg": "管理職（介護）",
    "km": "サービス提供責任者",
    "ls": "生活支援員",
    "apl": "福祉用具専門相談員 / 児童指導員/指導員",
    "nm": "児童発達支援管理責任者",
    "dcm": "サービス管理責任者",
    "ans": "看護師/准看護師",
    "nrd": "管理栄養士/栄養士",
    "ck": "調理師/調理スタッフ",
    "ctd": "介護タクシー/ドライバー",
    "mc": "医療事務/受付",
    "etc": "営業/管理部門/その他",
    "cc": "介護事務",
    "dm": "相談支援専門員",
    "pt": "理学療法士",
    "st": "言語聴覚士",
    "ot": "作業療法士",
    "ort": "視能訓練士",
    "jdr": "柔道整復師",
    "mas": "あん摩マッサージ指圧師",
    "acu": "鍼灸師",
    "bwt": "整体師",
    "dds": "歯科医師",
    "dh": "歯科衛生士",
    "dt": "歯科技工士",
    "da": "歯科助手",
    "cw": "保育士",
    "kt": "幼稚園教諭",
    "acw": "保育補助",
    "asc": "放課後児童支援員/学童指導員",
    "dr": "医師",
    "apo": "薬剤師",
    "mn": "助産師",
    "phn": "保健師",
    "na": "看護助手",
    "rt": "診療放射線技師",
    "mt": "臨床検査技師",
    "ce": "臨床工学技士",
    "cp": "公認心理師/臨床心理士",
    "csw": "医療ソーシャルワーカー",
    "otc": "登録販売者",
    "crc": "治験コーディネーター",
    "pc": "調剤事務"
}
    #職種のコード
    job_type_data = ["hh", "la", "cm", "mg", "km", "ls", "apl", "nm", "dcm", "ans", "nrd", "ck", "ctd", "mc", "etc", "cc", "dm", "pt", "st", "ot", "ort", "jdr", "mas", "acu", "bwt", "dds", "dh", "dt", "da", "cw", "kt", "acw", "asc", "dr", "apo", "mn", "phn", "na", "rt", "mt", "ce", "cp", "csw", "otc", "crc", "pc"]

    #都道府県ー数字の対応
    prefecture_connection = {"13":"東京都",
                         "14":"神奈川県",
                         "11":"埼玉県",
                         "12":"千葉県",
                         "8":"茨城県",
                         "9":"栃木県",
                         "10":"群馬県",
                         "27":"大阪府",
                         "28":"兵庫県",
                         "26":"京都府",
                         "25":"滋賀県",
                         "29":"奈良県",
                         "30":"和歌山県",
                         "23":"愛知県",
                         "22":"静岡県",
                         "21":"岐阜県",
                         "24":"三重県",
                         "1":"北海道",
                         "2":"青森県",
                         "3":"岩手県",
                         "4":"宮城県",
                         "5":"秋田県",
                         "6":"山形県",
                         "7":"福島県",
                         "19":"山梨県",
                         "20":"長野県",
                         "15":"新潟県",
                         "16":"富山県",
                         "17":"石川県",
                         "18":"福井県",
                         "31":"鳥取県",
                         "32":"島根県",
                         "33":"岡山県",
                         "34":"広島県",
                         "35":"山口県",
                         "36":"徳島県",
                         "37":"香川県",
                         "38":"愛媛県",
                         "39":"高知県",
                         "40":"福岡県",
                         "41":"佐賀県",
                         "42":"長崎県",
                         "43":"熊本県",
                         "44":"大分県",
                         "45":"宮崎県",
                         "46":"鹿児島県", 
                         "47":"沖縄県" 
}
    #都道府県のコード
    prefecture_data = ["13", "14", "11", "12", "8", "9", "10", "27", "28", "26", "25", "29", "30", "23", "22", "21", "24", "1", "2", "3", "4", "5", "6", "7", "19", "20", "15", "16", "17", "18", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47"]


    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        is_all = False
        
        scraper = JobMedleyScraper(page)
        
        is_all = True

        job_type_data = []
        prefecture_data = []

        for job_type in job_type_data:
            for prefecture in prefecture_data:
            
                #2重循環で、職種・都道府県を全部回す
                url = f"https://job-medley.com/{job_type}/pref{prefecture}/" 
            
                page.goto(url)
            
                job_count_element = page.query_selector('.c-search-condition-title__corresponding:has-text("該当件数")+ strong')
                if job_count_element:
                    job_count = int(job_count_element.inner_text())
                else:
                    print("求人数の要素が見つかりません。")
                    job_count = 0

                total_pages = math.ceil(job_count / 30)

                print(f"{prefecture}の求人数: {job_count}")
                print(f"総ページ数: {total_pages}")

                try:
                    if job_count > 0:
                        scraper.scrape_jobs(job_type_code=job_type, prefecture_code=prefecture, total_jobs=job_count, is_all=is_all)
                        print("スクレイピングが正常に完了しました。")
                    else:
                        print('求人がありません')

                except SystemExit as e:
                    if e.code == 0:
                        print("e.code=0のエラーが発生しました。")
                        break
                    else:
                        print(f"予期せぬエラーが発生しました: {e}")
                except Exception as e:
                    print(f"エラーが発生しました: {e}")

            


if __name__ == "__main__":
    main()
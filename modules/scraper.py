import csv
import re
import os
from typing import List, Dict, Any
import sys
import json
from datetime import datetime
import unicodedata


class JobMedleyScraper:
    def __init__(self, page):
        self.page = page
        self.data_list = []  # データリストの初期化を追加

    # 1. CSVの列名を定義
    CSV_COLUMNS = [
    "管理id",
    "取得元テーブル名",
    "取得元求人url",
    "登録日時",
    "アクション",
    "公開_非公開",
    "公開予定日",
    "非公開予定日",
    "削除予定日",
    "求人イメージ",
    "求人タイトル",
    "求人サブタイトル",
    "応募受付電話番号",
    "電話応募",
    "職種",
    "職種_google_for_jobs用",
    "職種_求人box用",
    "職種_stanby用",
    "職種_検索用",
    "職種_indeed検索用",
    "業務内容",
    "業務内容_画像1_url",
    "業務内容_画像1_説明文",
    "業務内容_画像2_url",
    "業務内容_画像2_説明文",
    "業務内容_画像3_url",
    "業務内容_画像3_説明文",
    "応募資格",
    "応募資格_画像1_url",
    "応募資格_画像1_説明文",
    "応募資格_画像2_url",
    "応募資格_画像2_説明文",
    "応募資格_画像3_url",
    "応募資格_画像3_説明文",
    "求める人物像",
    "求める人物像_画像1_url",
    "求める人物像_画像1_説明文",
    "求める人物像_画像2_url",
    "求める人物像_画像2_説明文",
    "求める人物像_画像3_url",
    "求める人物像_画像3_説明文",
    "雇用形態",
    "勤務体系",
    "採用フロー",
    "採用担当",
    "応募フォーム",
    "年齢",
    "就業時間",
    "休憩時間",
    "時間外",
    "賃金",
    "賃金区分",
    "最低給与金額",
    "最大給与金額",
    "基本給",
    "勤務時間",
    "固定残業の有無",
    "固定残業時間",
    "固定残業時間_法定内",
    "固定残業代",
    "試用期間",
    "試用期間の有無",
    "試用期間中の条件",
    "試用期間中の賃金区分",
    "試用期間中の最低給与金額",
    "試用期間中の最大給与金額",
    "試用期間中の基本給",
    "試用期間中の勤務時間",
    "試用期間中の固定残業の有無",
    "試用期間中の固定残業時間",
    "試用期間中の固定残業時間_法定内",
    "試用期間中の固定残業代",
    "給与の補足",
    "待遇",
    "休日",
    "年間休日数",
    "育児休業取得実績",
    "郵便番号",
    "都道府県",
    "市区町村",
    "町丁目番地",
    "ビル_建物名",
    "リモートワーク制度",
    "沿線_最寄駅",
    "転勤",
    "従業員数",
    "加入保険等",
    "加入保険等_indeed_api用",
    "定年齢",
    "再雇用",
    "通勤手当",
    "採用人数",
    "採用人数_indeed_api用",
    "学歴",
    "選考方法",
    "選考結果通知",
    "応募書類等",
    "選考日時",
    "勤務先会社名",
    "勤務先会社本社所在地",
    "勤務先会社ウェブサイトurl",
    "勤務先事業内容",
    "受動喫煙防止措置",
    "求人pr",
    "カテゴリ_indeed用",
    "カテゴリ_stanby用",
    "カテゴリ_求人ボックス用",
    "indeed検索用",
    "応募通知メール受信設定",
    "メールテンプレート名",
    "問い合わせ先メールアドレス",
    "メモ",
    "タグ",
    "非公開の選考条件",
    "急募",
    "オープニング",
    "未経験歓迎",
    "学歴不問",
    "駅から5分以内",
    "髪型_髪色自由",
    "土日祝休み",
    "残業なし",
    "社員登用あり",
    "交通費支給",
    "リモート_在宅ok",
    "車通勤ok",
    "バイク通勤ok",
    "寮_社宅あり",
    "即日勤務ok",
    "シニア応援",
    "無資格ok",
    "扶養内勤務ok",
    "主婦_主夫歓迎",
    "副業_wワークok",
    "留学生歓迎",
    "ブランクok",
    "服装自由",
    "履歴書不要",
    "資格優遇",
    "昇給_昇格あり",
    "賞与あり",
    "資格取得支援制度",
    "正社員",
    "週休2日",
    "シフト自由_選べる",
    "週1日からok",
    "週2_3日からok",
    "高収入_高時給",
    "web面談可",
    "管理タグ"
]

    def scrape_jobs(self, job_type_code: str, prefecture_code:str, start_page:int, end_page:int, total_jobs: int, is_all: bool) -> None:
        count = 0 #スクレイピングした求人のカウント
        for i in range(start_page, end_page + 1):
            print("is_all: " + str(is_all))
            url = f"https://job-medley.com/{job_type_code}/pref{prefecture_code}/?page={i}"

            self.page.goto(url, wait_until="networkidle", timeout=60000)

            links = self.page.query_selector_all('a:has-text("求人を見る")')

            jobs = [link.get_attribute('href') for link in links]
            found = False
            
            for job in jobs:
                try:
                    data = self.scrape_job_details(job)
                    if data != "":
                        self.data_list.append(data)
                        count += 1
                        print(f"Scraped page, job {job}")
                        found = True
                except SystemExit:
                    print(f"ハローワーク求人を検出したため、スクレイピングを終了します: {job}")
                    # self.write_to_csv(job_types_connection[job_type_code], total_jobs, is_all)  # 終了前に保存
                    return
                # # ヒットデータ：10件ごとにCSVに書き込む
                if len(self.data_list) >= 10:
                    self.write_to_csv(self.data_list, is_all)
                    print(f"計{count}ページの情報が取れました。")
            # # ヒットデータ：残りのデータがあれば書き込む
            if self.data_list:
                self.write_to_csv(self.data_list, is_all)

        
    def scrape_job_details(self, job_url: str) -> Dict[str, str]:
        self.page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_())
        self.page.goto(job_url)
        # ハローワーク求人のより正確なチェック

        hello_work_elements = self.page.query_selector_all('span.c-tag:has-text("ハローワーク求人"), p.c-heading:has-text("この求人はハローワーク求人です")')
        if hello_work_elements:
            for element in hello_work_elements:
                print(f"検出された要素: {element.inner_text()}")
            raise SystemExit(0)  # SystemExitを発生させる
        
        # サイトからデータを各変数として取得
        data = {
    "管理id": "",
    "取得元テーブル名": "",
    "取得元求人url": f"{job_url}",
    "登録日時": "",
    "アクション": "",
    "公開_非公開": "",
    "公開予定日": "",
    "非公開予定日": "",
    "削除予定日": "",
    "求人イメージ": "",
    "求人タイトル": "",
    '求人サブタイトル': self.get_text('h2.font-semibold.text-jm-brown'),
    "応募受付電話番号": "",
    "電話応募":'可',
    '職種': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("募集職種") + div div'),
    "職種_google_for_jobs用": "",
    "職種_求人box用": "",
    "職種_stanby用": "",
    "職種_検索用": "",
    "職種_indeed検索用": "",
    '業務内容': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("仕事内容") + div p'),
    "業務内容_画像1_url": "",
    "業務内容_画像1_説明文": "",
    "業務内容_画像2_url": "",
    "業務内容_画像2_説明文": "",
    "業務内容_画像3_url": "",
    "業務内容_画像3_説明文": "",
    '応募資格': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("応募要件") + div p'),
    "応募資格_画像1_url": "",
    "応募資格_画像1_説明文": "",
    "応募資格_画像2_url": "",
    "応募資格_画像2_説明文": "",
    "応募資格_画像3_url": "",
    "応募資格_画像3_説明文": "",
    '求める人物像': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("応募要件") + div p'),
    "求める人物像_画像1_url": "",
    "求める人物像_画像1_説明文": "",
    "求める人物像_画像2_url": "",
    "求める人物像_画像2_説明文": "",
    "求める人物像_画像3_url": "",
    "求める人物像_画像3_説明文": "",
    '雇用形態': self.get_job_forms(), 
    '勤務体系': self.get_work_style(), 
    "採用フロー": "",
    "採用担当": "",
    "応募フォーム": "",
    '年齢': self.get_age_info(), 
    '就業時間': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("勤務時間") + div p'), 
    '休憩時間': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("勤務時間") + div p'), 
    "時間外": "",
    '賃金': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与") + div p'), 
    '賃金区分': self.get_wage_classification(), 
    '最低給与金額': self.get_salary_range()[0], 
    '最大給与金額': self.get_salary_range()[1], 
    '基本給': self.get_basic_salary(),
    '勤務時間': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("勤務時間") + div p'), 
    '固定残業の有無': 'なし',
    "固定残業時間": "",
    "固定残業時間_法定内": "",
    "固定残業代": "",
    '試用期間': self.get_trial_period()[1], 
    '試用期間の有無': self.get_trial_period()[0],
    "試用期間中の条件": "",
    "試用期間中の賃金区分": "",
    "試用期間中の最低給与金額": "",
    "試用期間中の最大給与金額": "",
    "試用期間中の基本給": "",
    "試用期間中の勤務時間": "",
    "試用期間中の固定残業の有無": "",
    "試用期間中の固定残業時間": "",
    "試用期間中の固定残業時間_法定内": "",
    "試用期間中の固定残業代": "",
    '給与の補足': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与の備考") + div p'),
    '待遇': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("待遇") + div p'), 
    '休日': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("休日") + div p'), 
    '年間休日数': self.get_annual_holidays(),
    "育児休業取得実績": "",
    '都道府県': self.split_address()[0], 
    '市区町村': self.split_address()[1], 
    '町丁目番地': self.split_address()[2], 
    "ビル_建物名": self.split_address()[3],
    "リモートワーク制度": "",
    '沿線_最寄駅': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("アクセス") + div div p.whitespace-pre-wrap'), 
    "転勤": "",
    '従業員数': self.get_staff_total(), 
    '加入保険等': '健康保険,厚生年金,雇用保険,労災保険', 
    '加入保険等(Indeed api用)': '健康保険,厚生年金,雇用保険,労災保険',
    "定年齢": "",
    "再雇用": "",
    "通勤手当": "",
    '採用人数': '1',
    "採用人数_indeed_api用": "",
    "学歴": self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("応募要件") + div div div a:has-text("学歴")'), 
    "選考方法": self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("選考プロセス") + div div p'),
    "選考結果通知": "",
    "応募書類等": "",
    "選考日時": "",
    "勤務先会社名": self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("法人・施設名") + div a'), 
    "勤務先会社本社所在地": self.convert_f_h(self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("アクセス") + div div p:nth-of-type(1)')), 
    "勤務先会社ウェブサイトurl": "",
    "勤務先事業内容": "",
    "受動喫煙防止措置": "",
    "求人pr": self.get_appeal_points(),
    "カテゴリ_indeed用": "",
    "カテゴリ_stanby用": "",
    "カテゴリ_求人ボックス用": "",
    "indeed検索用": "",
    "応募通知メール受信設定": "",
    "メールテンプレート名": "",
    "問い合わせ先メールアドレス": "",
    "メモ": "",
    "タグ": "",
    "非公開の選考条件": "",
    "急募": "",
    #以下は、該当項目はアピールポイントにあるか否かで判断する。アピールポイントはタグの集まりのため。
    "オープニング": "",
    "未経験歓迎": "1" if '未経験可' in self.get_appeal_points() else'0',
    '学歴不問': "1" if '学歴不問' in self.get_appeal_points() else'0',
    "駅から5分以内": "1" if '駅から(5分以内)' in self.get_appeal_points() else'0',
    "髪型_髪色自由": "",
    "土日祝休み": "1" if '土日祝休み' in self.get_appeal_points() else'0',
    "残業なし": "",
    "社員登用あり": "",
    "交通費支給": "1" if '交通費支給' in self.get_appeal_points() else'0',
    "リモート_在宅ok": "",
    "車通勤ok": "1" if '車通勤可' in self.get_appeal_points() else '0',
    "バイク通勤ok": "",
    "寮_社宅あり": "1" if '寮あり・社宅あり' in self.get_appeal_points() else '0',
    "即日勤務ok": "1" if '即日勤務OK' in self.get_appeal_points() else '0',
    "シニア応援": "",
    "無資格ok": "1" if '無資格可' in self.get_appeal_points() else '0',
    "扶養内勤務ok": "",
    "主婦_主夫歓迎": "1" if '主夫・主婦OK' in self.get_appeal_points() else '0',
    "副業_wワークok": "1" if '副業OK' in self.get_appeal_points() else '0',
    "留学生歓迎": "1" if '外国人材・留学生活躍中' in self.get_appeal_points() else '0',
    "ブランクok": "1" if 'ブランク可' in self.get_appeal_points() else '0',
    "服装自由": "",
    "履歴書不要": "",
    "資格優遇": "",
    "昇給_昇格あり": "",
    '賞与あり': "1" if 'ボーナス・賞与あり' in self.get_appeal_points() else '0', 
    '資格取得支援制度': "1" if '資格取得支援' in self.get_appeal_points() else '0',
    '正社員': "1" if self.get_job_forms() == "正社員" else "0",
    "週休2日": "1" if '週2日からOK' in self.get_appeal_points() else '0',
    "シフト自由_選べる": "",
    "週1日からok": "1" if '週1日からOK' in self.get_appeal_points() else '0',
    "週2_3日からok": "",
    "高収入_高時給": "",
    "web面談可": "1" if 'WEB面接可' in self.get_appeal_points() else '0',
    "管理タグ": ""
}

        return data

    def write_to_csv(self, data_list: Dict[str, Any], is_all: bool) -> None:
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f'{output_dir}/job_medley全職種求人.csv'
        
        if is_all:
            file_exists = os.path.isfile(filename)
            try:
                with open(filename, 'a', newline='', encoding='utf-8-sig') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=self.CSV_COLUMNS)
                    if not file_exists:
                        writer.writeheader()
                    for row in self.data_list:
                        csv_row = {col: row.get(col, '') for col in self.CSV_COLUMNS}
                        writer.writerow(csv_row)
                print(f"データをCSVファイルに追加しました: {filename}")
            except IOError as e:
                print(f"CSVファイルへの書き込み中にエラーが発生しました {filename}: {e}")

        # データリストをクリア
        self.data_list = []

    def get_text(self, selector: str) -> str:
        """
        指定されたセレクタの要素からテキストを取得します。

        :param selector: CSSセレクタ
        :return: 取得されたテキスト
        """
        element = self.page.query_selector(selector)
        return element.inner_text() if element else ''


    def get_appeal_points(self) -> str:
        """
        求人のアピールポイントを取得します。


        :return: アピールポイントのリスト（カンマ区切り）
        """
        tags = self.page.query_selector_all('div.flex.flex-wrap.gap-1 a')
        appeal_points = ','.join([tag.inner_text() for tag in tags])
        return f"✅アピールポイント\n{appeal_points}"

    def get_job_forms(self) -> str:
        """
        雇用形態を取得します。


        :return: 【正職員】or【契約職員】or【パート・バイト】or【業務委託】
        """ 
        kyuyo = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与") + div')
        forms = ['正職員', '契約職員', 'パート・バイト', '業務委託']
        for form in forms:
            
            if form in kyuyo:
                if form == '正職員' : return '正社員'
                else: return form

    def get_work_style(self) -> str:
        """
        勤務体系を取得します。


        :return: シフト制or固定時間制
        """ 
        work_hours = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("勤務時間") + div p')
        holiday = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("休日") + div p')
        attributes = [work_hours, holiday]

        for attribute in attributes:
            if 'シフト' in attribute:
                return 'シフト制'
            elif '固定時間' in attributes:
                return '固定時間制'
        return ''

    def get_age_info(self) -> str:
        """
        CSSセレクタ '.font-semibold.text-jm-sm.break-keep + div p' から情報を取得し、
        その中にある年齢情報（「～XX歳」という形式）を抽出します。

        :return: 年齢情報または空文字列
        """
        # 1. 応募要件を取得
        requirements = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("応募要件") + div p')
        
        # 2. 年齢のパターンを正規表現で検索（例: "～XX歳"or"XX歳以下" 形式）
        age_pattern1 = r'～\d+歳'
        age_match1 = re.search(age_pattern1, requirements)
        age_pattern2 = r'\d+歳以下'
        age_match2 = re.search(age_pattern2, requirements)
        # 3. パターンが見つかった場合はその文字列を、見つからない場合は空文字列を返す
        if age_match1: 
            return age_match1.group(0)
        elif age_match2: 
            return age_match2.group(0)  
        else: return''

    def get_requirements(self) -> str:
        """
        求人の応募要件を取得します。


        :return: 応募要件と歓迎要件
        """
        apply = self.get_text('.c-table__th:has-text("応募要件") + td p')
        welcome = self.get_text('.c-table__th:has-text("歓迎要件") + td p')
        return f"{apply}\n\n{welcome}" if welcome else apply
    
    def get_holidays(self) -> str:
        """
        休日・休暇情報を取得します。


        :return: 休日と長期休暇の情報
        """
        dayoff = self.get_text('.c-table__th:has-text("休日") + td p')
        vacation = self.get_text('.c-table__th:has-text("長期休暇・特別休暇") + td p')
        return f"✅休日\n{dayoff}\n\n✅長期休暇・特別休暇\n{vacation}" if vacation else f"✅休日\n{dayoff}"

    def get_wage_classification(self) -> str:
        """
        賃金区分
        """
        salary_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与") + div')
        wage_classification = ["月給", "時給", "年収"]
        for classification in wage_classification:
            if classification in salary_text: return classification
        else: return ''

    def get_salary_range(self) -> list:
        """
        CSSセレクタ '.font-semibold.text-jm-sm.break-keep + div div' から給与情報を取得し、
        最低給与金額と最高給与金額をリストにして返します。

        :return: [最低給与金額, 最高給与金額]
        """
        # 給与を取得
        salary_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与") + div div')
        
        wage_classification = ["月給", "時給", "年収"]
        for classification in wage_classification:
            if classification in salary_text:
                min_salary_pattern = r'{}(\d+,\d+)円'.format(classification)
                max_salary_pattern = r'{}\d+,\d+円〜(\d+,\d+)円'.format(classification)

                # 最低給与金額を検索
                min_salary_match = re.search(min_salary_pattern, salary_text)
                min_salary = min_salary_match.group(1) if min_salary_match else ''
                #　’,’をなくす
                if ',' in min_salary:
                    min_salary = min_salary.replace(',', '')
                    min_salary = min_salary.strip()
                # 最高給与金額を検索
                max_salary_match = re.search(max_salary_pattern, salary_text)
                max_salary = max_salary_match.group(1) if max_salary_match else ''
                #　’,’をなくす
                if ',' in max_salary:
                    max_salary = max_salary.replace(',', '')
                    max_salary = max_salary.strip()

                return [min_salary, max_salary]

    def get_basic_salary(self) -> str:
        """
        CSSセレクタ '.font-semibold.text-jm-sm.break-keep + div p' から情報を取得し、
        「基本給」に関する給与情報を抽出して整形します。

        :return: 基本給情報（例: '150,000円' または '150,000円〜199,000円'）
        """
        #指定したセレクタのテキストを取得
        info_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与の備考") + div p')
    
        #基本給のパターンを検索
        basic_salary_pattern = r'基本給.*?(\d{1,3}(?:,\d{3})*|\d+)円(?:[〜\-](\d{1,3}(?:,\d{3})*|\d+)円)?'
        salary_match = re.search(basic_salary_pattern, info_text)

        if salary_match:
            #基本給情報を取得
            salary_info = salary_match.group(1)
            if ',' in salary_info:
                salary_info = salary_info.replace(',', '').strip()
            #そのままの情報を返す
            return salary_info
    
        # 「基本給」に関する情報が見つからなければ空文字列を返す
        return ''

    def get_trial_period(self) -> list:
        """
        試用期間の有無と期間（月数）をリスト形式で取得します。

        :return: [試用期間の有無 ('あり'または 'なし'), 試用期間の月数 (存在する場合の数値文字列)]
        """
        # 指定したセレクタから情報を取得
        info_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与の備考") + div p')
        
        # 「試用期間」が含まれているかを確認
        if '試用期間' not in info_text:
            return ['', '']  # 試用期間がない場合
        if '試用期間なし' in info_text:
            return ['なし', '']

        # 「試用期間」がある場合のリスト初期化
        result = ['あり']

        #試用期間の月数を抽出する正規表現パターン1
        sentence_match = re.search(r'[^。]*試用期間[^。]*[。．]?', info_text)
        #試用期間の月数を抽出する正規表現パターン2
        month_pattern = r'試用期間.*?(\d+)(ヶ月|か月|カ月|ヵ月)' 
        month_match = re.search(month_pattern, info_text)

        if  month_match:
            result.append(month_match.group(1)+ "ヶ月")  # 月数（例: '3ヶ月'）をリストに追加

        elif sentence_match:
            sentence = sentence_match.group(0)
            duration_match = re.search(r'([0-9０-９]+)(か月|ヶ月|カ月|ヵ月)', sentence)

            if duration_match:
                duration = duration_match.group(1)
                duration = self.convert_f_h(duration)#半角化する
                result.append(duration + "ヶ月")  # 月数（例: '3ヶ月'）をリストに追加
                return result
            else:
                result.append('')

        else:
            result.append('')

        return result

    def get_annual_holidays(self) -> str:
        """
        「年間休日」に関する情報を取得し、年間休日の日数を抽出します。

        :return: 年間休日の日数（文字列）または空白文字列
        """
        # 1. 指定したセレクタからテキスト情報を取得
        holiday_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("休日") + div p')
        
        # 2. 「年間休日」の文字列があるか確認
        if '年間休日' or '年休' or '年間休暇' or '年間公休'in holiday_text:
        
            # 3. 「年間休日」に続く1〜3桁の数字を抽出する正規表現パターン
            holiday_pattern = r'(年間休日|年休|年間休暇|年間公休).*?(\d{1,3})'# 対応パターン：“年間休日 120日”、“年休：100日”、“年間休日は 110日”
            holiday_match = re.search(holiday_pattern, holiday_text)
        
            # 4. 数字が見つかった場合はその数字を文字列として返す
            return holiday_match.group(2) if holiday_match else ''
        else: return ''

    def split_address(self) -> list:
        """
        住所情報を「都道府県」「市区町村」「町丁目番号」「建物」の4つの部分に分割してリストに格納します。

        :return: [都道府県, 市区町村, 町丁目番号, 建物]
        """
        # 指定したセレクタからテキスト情報を取得
        address_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("アクセス") + div div p:nth-of-type(1)')
        
        #リストを初期設定する
        result = ["", "", "", ""]

        # 都道府県を検出して抽出（都道府県は1～4文字の漢字であると仮定）
        prefecture_pattern = r'([一-龥]{1,4}県|[一-龥]{1,4}都|[一-龥]{1,4}府|[一-龥]{1,4}道)'
        prefecture_match = re.search(prefecture_pattern, address_text)
        
        #  都道府県の情報をリストに追加
        if prefecture_match:
            prefecture = prefecture_match.group(0)
            result[0] =  prefecture # 都道府県部分を[0]に入れる

        #　住所情報から都道府県の部分を削除する
        address_text = address_text.replace(prefecture, '').strip()

        # 3. 市区町村を検出して抽出（市区町村は1～4文字の漢字であると仮定）、市、区、町、村に優先度を付けて検出する
        city_pattern1 = r'([一-龥]{1,4}(市|区))'
        city_pattern2 = r'([一-龥]{1,4}(町))'
        city_pattern3 = r'([一-龥]{1,4}(村))'
        city_match1 = re.search(city_pattern1, address_text)
        city_match2 = re.search(city_pattern2, address_text)
        city_match3 = re.search(city_pattern3, address_text)
        if city_match1: 
            city = city_match1.group(0)
            result[1] = city
        elif city_match2:
            city = city_match2.group(0)
            result[1] = city
        elif city_match3:
            city = city_match3.group(0)
            result[1] = city
        
        #　更に、市区町村の部分を削除する
        address_text = address_text.replace(city, '').strip()
        
        #　先に、「スペースを検出する」ことで建物の情報を検出する、なければ空白を戻す
        space_index = address_text.find(" ") 
        if space_index != -1:
            building = address_text[space_index + 1:]
        else:
            building = ''

        #　町丁目番号の情報は、一番最初の住所情報から、都道府県＋市区町村＋建物の情報を抜けて残った情報になる。
        town = address_text.replace(building, '').strip()
        result[2] = self.convert_f_h(town)#半角化する

        result[3] = self.convert_f_h(building)#半角化する

        return result

    def get_staff_total(self) -> str:
        # スタッフ構成の情報を取得
        selector = '.font-semibold.text-jm-sm.break-keep:has-text("スタッフ構成") + div div'
        text = self.get_text(selector)

        # 情報がなければ空文字を返す
        if not text:
            return ''

        # すべての数字を抽出
        all_numbers = re.findall(r'\d+', text)
        # 括弧内の数字を抽出（全角括弧を考慮して調整）
        numbers_in_brackets = re.findall(r'（\D*(\d+)\D*）', text)

        # すべての数字の合計
        total_sum = sum(int(num) for num in all_numbers)
        if total_sum == 0: return ''#中に数字が入っていなければ、空白を戻す。（最後に0人というデータを戻すのを避けるため、）
        # 括弧内の数字の合計
        brackets_sum = sum(int(num) for num in numbers_in_brackets)

        # 合計から括弧内の数字を引いた結果
        final_count = total_sum - brackets_sum

        # 結果を文字列として返す
        return final_count

    def check_bonus(self) -> str:
        """
        「ボーナス・賞与あり」というリンクが存在するか確認し、
        存在する場合は「あり」を返します。

        :return: 「あり」または空白
        """
        # 指定のCSSセレクタを使用してリンクがあるかを確認
        bonus_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("待遇") + div div div a:has-text("ボーナス・賞与あり")')
    
        # 情報が存在する場合は「あり」、存在しない場合は空白を返す
        return 'あり' if bonus_text else ''
    
    def check_eligibility_support(self) -> str:
        """
        「資格取得支援」というリンクが存在するか確認し、
        存在する場合は「あり」を返します。

        :return: 「あり」または空白
        """
        # 指定のCSSセレクタを使用してリンクがあるかを確認
        bonus_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("教育体制・研修") + div div div a:has-text("資格取得支援")')
    
        # 情報が存在する場合は「あり」、存在しない場合は空白を返す
        return 'あり' if bonus_text else ''


    @staticmethod
    def extract_text_in_brackets(input_str: str) -> str:
        """
        入力文字列から【】で囲まれたテキストを抽出します。


        :param input_str: 入力文字列
        :return: 抽出されたテキスト
        """
        print("===input_str: " + input_str)
        if input_str is None:
            return ''
        match = re.search(r'【(.*?)】', input_str)
        if match:
            text = match.group(1)
            return '正社員' if text == '正職員' else text
        return ''

    @staticmethod
    def convert_f_h(text: str) -> str:
        # 将全角字符转换为半角字符
        return unicodedata.normalize('NFKC', text)

    @staticmethod
    def extract_payment_type(input_str: str) -> str:
        """
        給与形態（月給、時給、日給）を抽出します。


        :param input_str: 入力文字列
        :return: 抽出された給与形態
        """
        if input_str is None:
            return ''
        match = re.search(r'(月給|時給|日給)', input_str)
        return match.group(1) if match else ''


    @staticmethod
    def extract_min_salary(input_str: str) -> str:
        """
        最低給与額を抽出します。


        :param input_str: 入力文字列
        :return: 抽出された最低給与額
        """
        if input_str is None:
            return ''
        match = re.search(r'(\d{1,3},\d{3})', input_str)
        return match.group(1) if match else ''


    @staticmethod
    def extract_max_salary(input_str: str) -> str:
        """
        最高給与額を抽出します。


        :param input_str: 入力文字列
        :return: 抽出された最高給与額
        """
        if input_str is None:
            return ''
        match = re.search(r'〜\s*(\d{1,3},\d{3})', input_str)
        return match.group(1) if match else ''

    
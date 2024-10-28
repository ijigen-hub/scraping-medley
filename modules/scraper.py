import csv
import re
import os
from typing import List, Dict, Any
import sys
import json
from modules.create_date_string import create_date_string, create_yesterday_yyyymmdd
from modules.write_unhit_to_gss import write_data_to_sheet

class JobMedleyScraper:
    def __init__(self, page):
        self.page = page
        self.data_list = []  # データリストの初期化を追加

    # 1. CSVの列名を定義
    CSV_COLUMNS = [
        '都道府県', '施設形態', 'kbx仕事内容（勤務地）', '市区郡', '町村番地', '町村', '地名タグ',
        '元データ_仕事内容（アクセス）', '駅名', '整形後_仕事内容（アクセス）', 'kbx職種名_地名',
        'kbx職種名_地名+レコメンドタグ', 'kbx給与（最低額）', 'kbx給与（最高額）', '元データ_仕事内容（給与）',
        '職種', '求人URL', '法人名', 'ステータス', '会社名', '職種名', '求人キャッチコピー',
        '勤務地（郵便番号）', '勤務地（都道府県・市区町村・町域）', '勤務地（丁目・番地・号）',
        '勤務地（建物名・階数）', '雇用形態', '有料職業紹介に該当', '給与形態', '給与（最低額）',
        '給与（最高額）', '給与（表示形式）', '固定残業代の有無', '固定残業代（最低額）', '固定残業代（最高額）',
        '固定残業代（支払い単位）', '固定残業代（時間）', '固定残業代（超過分の追加支払への同意）',
        '勤務形態', '平均所定労働時間', '社会保険', '社会保険（適用されない理由）', '試用期間の有無',
        '試用期間（期間）', '試用期間（期間の単位）', '試用期間（試用期間中の労働条件）',
        '試用期間中の給与形態', '試用期間中の給与（最低額）', '試用期間中の給与（最高額）',
        '試用期間中の給与（表示形式）', '試用期間中の固定残業代の有無', '試用期間中の固定残業代（最低額）',
        '試用期間中の固定残業代（最高額）', '試用期間中の固定残業代（支払い単位）',
        '試用期間中の固定残業代（時間）', '試用期間中の固定残業代（超過分の追加支払への同意）',
        '試用期間中の平均所定労働時間', '試用期間中のその他の条件', '仕事内容（仕事内容）',
        '仕事内容（アピールポイント）', '仕事内容（求める人材）', '仕事内容（勤務時間・曜日）',
        '仕事内容（休暇・休日）', '仕事内容（勤務地）', '仕事内容（アクセス）', '仕事内容（給与）',
        '仕事内容（待遇・福利厚生）', '仕事内容（その他）', '掲載画像', 'タグ',
        '採用予定人数', '採用までの希望日数', '履歴書の有無', '応募者に関する情報',
        '応募用メールアドレス', '電話番号（半角）', '審査用の質問'
    ]

    # 2. 常に定数である列の変数を宣言
    CONSTANT_VALUES = {
        'ステータス': '募集中',
        '平均所定労働時間': '160',
        '有料職業紹介に該当': 'はい',
        '社会保険': '健康保険,厚生年金,雇用保険,労災保険',
        '固定残業代の有無': 'なし',
        '試用期間の有無': 'なし',
        'タグ': '昇給・昇格あり、交通費支給、急募',
        '採用予定人数': 1,
        '採用までの希望日数': '1～2週間',
        '履歴書の有無': '任意',
        '応募者に関する情報': '電話番号、性別、生年月日',
    }

    def scrape_jobs(self, job_type: str, facility: str, total_jobs: int, is_all: bool, job_type_origin: str) -> None:
        # for i in range(start_page, end_page + 1):
        print("is_all: " + str(is_all))
        # self.page.goto(f"https://job-medley.com/{job_type}/pref{prefecture_code}/?page={i}")
        self.page.goto(f"https://job-medley.com/{job_type}/search/?q={facility}")
        links = self.page.query_selector_all('a:has-text("求人を見る")')
        jobs = [link.get_attribute('href') for link in links]
        found = False
        for job in jobs:
            try:
                data = self.scrape_job_details(job, facility)
                if data != "":
                    self.data_list.append(data)
                    print(f"Scraped page, job {job}")
                    found = True
            except SystemExit:
                print(f"ハローワーク求人を検出したため、スクレイピングを終了します: {job}")
                self.write_to_csv(job_type, total_jobs, is_all)  # 終了前に保存
                return
        # ヒットデータ：10件ごとにCSVに書き込む
        if len(self.data_list) >= 10:
            self.write_to_csv(job_type, total_jobs, is_all)
        # ヒットデータ：残りのデータがあれば書き込む
        if self.data_list:
            self.write_to_csv(job_type, total_jobs, is_all)
        # 検索ヒットがなかった施設をGSSに転記
        if found == False:
            unhit_facility = {
                                "開拓日": create_yesterday_yyyymmdd(),
                                "施設名": facility,
                                "職種": job_type_origin
                            }
            write_data_to_sheet([unhit_facility])
        print(f" {facility}:{found}")

        
    def scrape_job_details(self, job_url: str, facility: str) -> Dict[str, str]:
        self.page.goto(job_url)
        # ハローワーク求人のより正確なチェック
        hello_work_elements = self.page.query_selector_all('span.c-tag:has-text("ハローワーク求人"), p.c-heading:has-text("この求人はハローワーク求人です")')
        if hello_work_elements:
            for element in hello_work_elements:
                print(f"検出された要素: {element.inner_text()}")
            raise SystemExit(0)  # SystemExitを発生させる
        # 3. サイトからデータを各変数として取得
        data = {
            '求人URL': job_url,
            '会社名' : re.sub(r'[（）【】]', '', self.get_text('.c-table__th:has-text("法人・施設名") + td a.c-text-link')).replace('　', ' '),
            '職種': self.get_text('.c-table__th:has-text("募集職種") + td p'),
            '求人キャッチコピー': self.get_text('h2.o-article__title').replace('\n', ' '),
            '仕事内容（給与）': self.get_text('.c-table__th:has-text("給与の備考") + td'),
            '仕事内容（勤務時間・曜日）': self.get_text('.c-table__th:has-text("勤務時間") + td p'),
            '仕事内容（仕事内容）': self.get_job_description(),
            '仕事内容（アピールポイント）': self.get_appeal_points(),
            '仕事内容（求める人材）': self.get_requirements(),
            '仕事内容（休暇・休日）': self.get_holidays(),
            '仕事内容（勤務地）': self.get_text('.c-table__th:has-text("アクセス") + td p:first-child'),
            '仕事内容（アクセス）': self.get_text('.c-table__th:has-text("アクセス") + td > div:nth-child(5)') or self.get_text('.c-table__th:has-text("アクセス") + td > div:nth-child(4)'),
            '仕事内容（待遇・福利厚生）': self.get_text('.c-table__th:has-text("待遇") + td p'),
            '施設形態': self.get_text('.c-table__th:has-text("施設形態") + td a.c-text-link') or self.get_text('.c-table__th:has-text("施設・サービス形態") + td a.c-text-link')
        }
        # 給与データの加工部分を修正
        salary_text = self.get_text('.c-table__th:has-text("給与") + td')
        data['雇用形態'] = self.extract_text_in_brackets(salary_text)
        data['給与形態'] = self.extract_payment_type(salary_text)
        data['給与（最低額）'] = self.extract_min_salary(salary_text)
        data['kbx給与（最低額）'] = self.extract_min_salary(salary_text)
        data['給与（最高額）'] = self.extract_max_salary(salary_text)
        data['kbx給与（最高額）'] = self.extract_min_salary(salary_text)
        data['給与（表示形式）'] = '最低額を表示' if not data['給与（最高額）'] else '範囲で表示'

        # データを整形
        # 職種の調整
        if "看護師" in data['職種']:
            if "准看護師" in data['職種']:
                data['職種'] = "正看護師・准看護師"
            else:
                data['職種'] = "正看護師"
        ## 職種名の作成
        data['職種名'] = f"{data['職種']}の{data['施設形態']}" if data['施設形態'] else data['職種']
        ## 施設形態の書き替え
        if data['施設形態'] == '診療所':
            data['施設形態'] = 'クリニック・診療所'
        elif data['施設形態'] == 'その他（企業・学校等）':
            data['施設形態'] = '企業や学校'
        elif data['施設形態'] == '訪問看護ステーション':
            data['施設形態'] = '訪問看護'
        elif data['施設形態'] == '介護・福祉事業所':
            data['施設形態'] = '介護施設'

        # 不要なデータを整形or削除

        ## 正社員じゃない求人
        if data['雇用形態'] != "正社員":
            print(f"雇用形態：{data['雇用形態']} 正社員ではないので保存をパス")
            return ""
        
        ## 住所不正
        if "未定" in data['仕事内容（勤務地）'] :
            print('正しい住所がないので保存をパス')
            return ""

        ## 欲しい施設の求人ではない
        if facility.replace(" ","") in data['会社名'].replace(" ",""):
            pass
        elif data['会社名'].replace(" ","") in facility.replace(" ",""):
            pass
        else:
            print(f"シート上の施設名：{facility}")
            print(f"サイト上の施設名：{data['会社名']}")
            print("施設名が一致しないので保存をパス")
            return ""

        # 4. 定数値を追加
        data.update(self.CONSTANT_VALUES)


        return data

    def get_text(self, selector: str) -> str:
        """
        指定されたセレクタの要素からテキストを取得します。

        :param selector: CSSセレクタ
        :return: 取得されたテキスト
        """
        element = self.page.query_selector(selector)
        return element.inner_text() if element else ''

    def get_job_description(self) -> str:
        """
        求人の仕事内容を取得します。


        :return: 仕事内容の説明
        """
        former = self.get_text('.s-job-offer-appeal-content')
        latter = self.get_text('.c-table__th:has-text("仕事内容") + td p')
        return f"✅仕事内容\n{latter}\n\n✅施設詳細\n{former}"


    def get_appeal_points(self) -> str:
        """
        求人のアピールポイントを取得します。


        :return: アピールポイントのリスト（カンマ区切り）
        """
        tags = self.page.query_selector_all('a.c-tag')
        appeal_points = ','.join([tag.inner_text() for tag in tags])
        return f"✅アピールポイント\n{appeal_points}"


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

    def write_to_csv(self, job_type: str, total_jobs: int, is_all: bool) -> None:
        output_dir = 'output'
        os.makedirs(output_dir, exist_ok=True)
        datestring = create_date_string()
        
        filename = f'{output_dir}/{datestring}.csv'
        
        while is_all:
            file_exists = os.path.isfile(filename)
            try:
                with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
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
            break
        
        if not is_all:
            file_exists = os.path.isfile(filename)
            try:
                with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
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
        
        # データリストをクリア
        self.data_list = []
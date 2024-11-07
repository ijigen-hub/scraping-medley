import csv
import re
import os
from typing import List, Dict, Any
import sys
import json
from datetime import datetime
from job_medley_scraper_daily_scheduled import job_types_connection

def create_date_string():
    # 获取当前日期，并格式化为 'YYYY-MM-DD'
    return datetime.now().strftime("%Y-%m-%d")

class JobMedleyScraper:
    def __init__(self, page):
        self.page = page
        self.data_list = []  # データリストの初期化を追加

    # 1. CSVの列名を定義
    CSV_COLUMNS = [
        '求人サブタイトル', '応募受付電話番号','電話応募', '職種','業務内容', '応募資格', '求める人物像',
        '雇用形態', '勤務体系', '年齢', '就業時間', '休憩時間', '賃金', '賃金区分', '最低給与金額', 
        '最大給与金額', '基本給','勤務時間', '固定残業の有無', '固定残業時間', '固定残業代', '試用期間', 
        '試用期間の有無', '試用期間中の条件', '試用期間中の賃金区分', '試用期間中の最低給与金額',
        '試用期間中の最大給与金額', '試用期間中の勤務時間','試用期間中の固定残業の有無', '試用期間中の固定残業時間', 
        '給与の補足', '待遇', '休日', '年間休日数','郵便番号','都道府県', '市区町村', '町丁目番地', 
        'ビル・建物名', '沿線・最寄駅', '従業員数', '加入保険等', '加入保険等(Indeed api用)','採用人数', 
        'Indeed api用 採用人数', '学歴', '選考方法', '勤務先会社名', '勤務先会社本社所在地', '勤務先事業内容', 
        '受動喫煙防止措置','求人PR', '学歴不問', '履歴書不要', '賞与あり', '資格取得支援制度', '正社員'
    ]

    # 2. 常に定数である列の変数を宣言
    CONSTANT_VALUES = {
        '電話応募': '可',
        '固定残業の有無':'なし',
        '加入保険等': '健康保険,厚生年金,雇用保険,労災保険', 
        '加入保険等(Indeed api用)': '健康保険,厚生年金,雇用保険,労災保険',
        '採用人数': '1', 
    }

    def scrape_jobs(self, job_type_code: str, prefecture_code:str, start_page:int, end_page:int, total_jobs: int, is_all: bool) -> None:
        for i in range(start_page, end_page + 1):
            print("is_all: " + str(is_all))
            if i==1:  url = f"https://job-medley.com/{job_type_code}/pref{prefecture_code}/"
            else: url = f"https://job-medley.com/{job_type_code}/pref{prefecture_code}/?page={i}"

            self.page.goto(url)

            links = self.page.query_selector_all('a:has-text("求人を見る")')

            jobs = [link.get_attribute('href') for link in links]
            found = False
            for job in jobs:
                try:
                    data = self.scrape_job_details(job)
                    if data != "":
                        self.data_list.append(data)
                        print(f"Scraped page, job {job}")
                        found = True
                except SystemExit:
                    print(f"ハローワーク求人を検出したため、スクレイピングを終了します: {job}")
                    self.write_to_csv(job_type, total_jobs, is_all)  # 終了前に保存
                    return
        # # ヒットデータ：10件ごとにCSVに書き込む
        if len(self.data_list) >= 10:
            self.write_to_csv(job_type, total_jobs, is_all)
        # # ヒットデータ：残りのデータがあれば書き込む
        if self.data_list:
            self.write_to_csv(job_type, total_jobs, is_all)

        
    def scrape_job_details(self, job_url: str) -> Dict[str, str]:
        self.page.goto(job_url)
        # ハローワーク求人のより正確なチェック
        #?????????????????
        hello_work_elements = self.page.query_selector_all('span.c-tag:has-text("ハローワーク求人"), p.c-heading:has-text("この求人はハローワーク求人です")')
        if hello_work_elements:
            for element in hello_work_elements:
                print(f"検出された要素: {element.inner_text()}")
            raise SystemExit(0)  # SystemExitを発生させる
        # 3. サイトからデータを各変数として取得
        data = {
            '求人サブタイトル': self.get_text('h2.font-semibold'),#これはだめ、、
            '応募受付電話番号': '',
            '職種': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("募集職種") + div div'),
            '業務内容': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("仕事内容") + div p'),
            '応募資格': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("応募要件") + div p'), 
            '求める人物像': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("仕事内容") + div p'),
            '雇用形態': self.get_job_forms(), 
            '勤務体系': self.get_work_style(), 
            '年齢': self.get_age_info(), 
            '就業時間': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("勤務時間") + div p'), 
            '休憩時間': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("勤務時間") + div p'), 
            '賃金': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与") + div p'), 
            '賃金区分': self.get_wage_classification(), 
            '最低給与金額': self.get_salary_range()[0], 
            '最大給与金額': self.get_salary_range()[1], 
            '基本給': self.get_basic_salary(),
            '勤務時間': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("勤務時間") + div p'), 
            '固定残業時間': '', 
            '固定残業代': '', 
            '試用期間': self.get_trial_period()[1], 
            '試用期間の有無': self.get_trial_period()[0], 
            '試用期間中の条件': '', 
            '試用期間中の賃金区分': '', 
            '試用期間中の最低給与金額': '',
            '試用期間中の最大給与金額': '', 
            '試用期間中の勤務時間': '',
            '試用期間中の固定残業の有無': '', 
            '試用期間中の固定残業時間': '', 
            '給与の補足': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与の備考") + div p'), 
            '待遇': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("待遇") + div p'), 
            '休日': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("休日") + div p'), 
            '年間休日数': self.get_annual_hoildays(),
            '郵便番号': '',
            '都道府県': self.split_address()[0], 
            '市区町村': self.split_address()[1], 
            '町丁目番地': self.split_address()[2], 
            'ビル・建物名': '', 
            '沿線・最寄駅': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("アクセス") + div div p:nth-of-type(2)'), 
            '従業員数': self.get_staff_total(), 
            'Indeed api用 採用人数': '', 
            '学歴': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("応募要件") + div div div a:has-text("学歴")'), 
            '選考方法': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("選考プロセス") + div div p'),  #だめっぽい、、、
            '勤務先会社名': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("法人・施設名") + div a'), 
            '勤務先会社本社所在地': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("アクセス") + div div p:nth-of-type(1)'), 
            '勤務先事業内容': '', 
            '受動喫煙防止措置': '',
            # '求人PR': , 
            '学歴不問': self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("応募要件") + div div div a:has-text("学歴")'),
            '履歴書不要': '', 
            '賞与あり': self.check_bonus(), 
            '資格取得支援制度': self.check_eligibility_support(), 
            '正社員': self.get_job_forms()
        }

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


    # def get_appeal_points(self) -> str:
        """
        求人のアピールポイントを取得します。


        :return: アピールポイントのリスト（カンマ区切り）
        """
        tags = self.page.query_selector_all('a.c-tag')
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
                return form

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
        kyuyo = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与") + div')
        if '月給' in kyuyo: return '月給'
        else: return ''

    def get_salary_range(self) -> list:
        """
        CSSセレクタ '.font-semibold.text-jm-sm.break-keep + div div' から給与情報を取得し、
        最低給与金額と最高給与金額をリストにして返します。

        :return: [最低給与金額, 最高給与金額]
        """
        # 1. 給与を取得
        salary_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与") + div div')
        
        # 2. 給与の範囲（最低・最高）を抽出するための正規表現
        min_salary_pattern = r'月給(\d+,\d+)円'
        max_salary_pattern = r'月給\d+,\d+円〜(\d+,\d+)円'
        
        # 3. 最低給与金額を検索
        min_salary_match = re.search(min_salary_pattern, salary_text)
        min_salary = min_salary_match.group(1) if min_salary_match else ''
        
        # 4. 最高給与金額を検索
        max_salary_match = re.search(max_salary_pattern, salary_text)
        max_salary = max_salary_match.group(1) if max_salary_match else ''
        
        # 5. 最低給与金額と最高給与金額をリストにして返す、最低額はself.get_salary_range()[0]、最高額はself.get_salary_range[1]
        return [min_salary, max_salary]

    def get_basic_salary(self) -> str:
        """
        CSSセレクタ '.font-semibold.text-jm-sm.break-keep + div p' から情報を取得し、
        「基本給」に関する給与情報を抽出して整形します。

        :return: 基本給情報（例: '150,000円' または '150,000円〜199,000円'）
        """
        # 1. 指定したセレクタのテキストを取得
        info_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与の備考") + div p')
        
        # 2. 基本給のパターンを検索
        basic_salary_pattern = r'基本給.*?(\d{1,3}(?:,\d{3})*円(?:〜\d{1,3}(?:,\d{3})*円)?)'
        salary_match = re.search(basic_salary_pattern, info_text)
        
        # 3. 「基本給」に関する情報が見つからなければ空文字列を返す
        if not salary_match:
            return ''
        
        # 4. 基本給情報を取得
        salary_info = salary_match.group(1)
        
        # 5. 「〜」が含まれていない場合は単一の基本給金額、含まれている場合は範囲
        if '〜' in salary_info:
            # 範囲が指定されている場合はそのまま返す（例: '150,000円〜199,000円'）
            return salary_info
        else:
            # 単一の金額のみの場合、その金額を返す（例: '150,000円'）
            return salary_info

    def get_trial_period(self) -> list:
        """
        試用期間の有無と期間（月数）をリスト形式で取得します。

        :return: [試用期間の有無 ('あり'または 'なし'), 試用期間の月数 (存在する場合の数値文字列)]
        """
        # 1. 指定したセレクタから情報を取得
        info_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与の備考") + div p')
        
        # 2. 「試用期間」が含まれているかを確認
        if '試用期間' not in info_text:
            return ['なし', '']  # 試用期間がない場合
        
        # 3. 「試用期間」がある場合のリスト初期化
        result = ['あり']
        
        # 4. 試用期間の月数を抽出する正規表現パターン
        month_pattern = r'試用期間.*?(\d+)(ヶ月|か月)'
        month_match = re.search(month_pattern, info_text)
        
        # 5. 月数が見つかった場合はリストに追加、見つからない場合はなし
        if month_match:
            result.append(month_match.group(1))  # 月数（例: '3'）をリストに追加
        
        return result

    def get_annual_holidays(self) -> str:
        """
        「年間休日」に関する情報を取得し、年間休日の日数を抽出します。

        :return: 年間休日の日数（文字列）または空白文字列
        """
        # 1. 指定したセレクタからテキスト情報を取得
        holiday_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("休日") + div p')
        
        # 2. 「年間休日」の文字列があるか確認
        if '年間休日' not in holiday_text:
            return ''  # 「年間休日」がない場合は空白を返す
        
        # 3. 「年間休日」に続く1〜3桁の数字を抽出する正規表現パターン
        holiday_pattern = r'年間休日\s*(\d{1,3})'
        holiday_match = re.search(holiday_pattern, holiday_text)
        
        # 4. 数字が見つかった場合はその数字を文字列として返す
        return holiday_match.group(1) if holiday_match else ''

    def split_address(self) -> list:
        """
        住所情報を「都道府県」「市区町村」「その他」の3つの部分に分割してリストに格納します。

        :return: [都道府県, 市区町村, その他]
        """
        # 1. 指定したセレクタからテキスト情報を取得
        address_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("アクセス") + div div p:nth-of-type(1)')
        
        # 2. 都道府県を検出して抽出（都道府県は1～4文字の漢字であると仮定）
        prefecture_pattern = r'([一-龥]{1,4}県|[一-龥]{1,4}都|[一-龥]{1,4}府|[一-龥]{1,4}道)'
        prefecture_match = re.search(prefecture_pattern, address_text)
        
        # 3. 市区町村を検出して抽出（市区町村は1～4文字の漢字であると仮定）
        city_pattern = r'([一-龥]{1,4}(市|区|町|村))'
        city_match = re.search(city_pattern, address_text)
        
        # 4. リストの初期化
        result = ["", "", ""]

        # 5. 都道府県と市区町村の情報をリストに追加
        if prefecture_match:
            result[0] = prefecture_match.group(0)  # 都道府県部分を[0]に入れる
        
        if city_match:
            # 市区町村部分を[1]に入れる
            city_start = city_match.start()
            result[1] = address_text[prefecture_match.end():city_start].strip() + city_match.group(0)
            
            # 残りの部分を[2]に入れる
            result[2] = address_text[city_match.end():].strip()
        
        return result

    def get_staff_total(self) -> str:
        """
        「スタッフ構成」に関する情報を取得し、情報中に含まれるすべての数字を合計します。

        :return: 合計されたスタッフ数の文字列、または空白文字列
        """
        # 1. 指定したセレクタからテキスト情報を取得
        staff_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("スタッフ構成") + div div')
        
        # 2. 情報が存在しない場合は空白を返す
        if not staff_text:
            return ''
        
        # 3. テキスト内のすべての数字を抽出
        numbers = re.findall(r'\d+', staff_text)
        
        # 4. 数字のリストが空の場合は空白を返す
        if not numbers:
            return ''
        
        # 5. 数字を整数に変換して合計を計算
        total = sum(int(num) for num in numbers)
        
        # 6. 合計を文字列として返す
        return str(total)

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
        
        # filename = f'{output_dir}/{job_types_connection[job_type]}.csv'
        filename = f'{output_dir}/job_medley全職種求人.csv'
        
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
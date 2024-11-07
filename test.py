from playwright.sync_api import sync_playwright
import re

class JobMedleyScraper:
    def __init__(self, url):
        self.url = url
        self.page = None

    def start(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # 使用 headless=False 来查看页面加载过程
            self.page = browser.new_page()
            self.page.goto(self.url)

            # print(self.get_work_style())
            
            print(self.get_appeal_points())
            browser.close()

    def get_appeal_points(self) -> str:
        """
        求人のアピールポイントを取得します。


        :return: アピールポイントのリスト（カンマ区切り）
        """
        tags = self.page.query_selector_all('div.gap-1 a.text-jm-brown')
        appeal_points = ','.join([tag.inner_text() for tag in tags])
        return f"✅アピールポイント\n{appeal_points}"
    
    def get_text(self, selector: str) -> str:
        """
        从指定的选择器获取文本内容
        """
        element = self.page.query_selector(selector)
        if element:
            return element.inner_text()
        else:
            print("未找到元素:", selector)  # 添加调试信息
            return ''

    def get_age_info(self) -> str:
        """
        CSSセレクタ '.font-semibold.text-jm-sm.break-keep + div p' から情報を取得し、
        その中にある年齢情報（「～XX歳」という形式）を抽出します。

        :return: 年齢情報または空文字列
        """
        # 1. 応募要件を取得
        requirements = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("応募要件") + div p')
        
        # 2. 年齢のパターンを正規表現で検索（例: "～XX歳" 形式）
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

    def get_wage_classification(self) -> str:
        """
        賃金区分
        """
        kyuyo = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与") + div')
        if '月給' in kyuyo: return '月給'
        else: return ''

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
# 使用示例
url = f"https://job-medley.com/hh/1143681/" 
scraper = JobMedleyScraper(url)
scraper.start()
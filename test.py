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
            
            print(self.get_appeal_points())


    def get_appeal_points(self) -> str:
        """
        求人のアピールポイントを取得します。


        :return: アピールポイントのリスト（カンマ区切り）
        """
        tags = self.page.query_selector_all('div.flex.flex-wrap.gap-1 a')
        appeal_points = ','.join([tag.inner_text() for tag in tags])
        return f"✅アピールポイント\n{appeal_points}"

    def get_text(self, selector: str) -> str:
        """
        指定されたセレクタの要素からテキストを取得します。

        :param selector: CSSセレクタ
        :return: 取得されたテキスト
        """
        element = self.page.query_selector(selector)
        return element.inner_text() if element else ''
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
url = f"https://job-medley.com/hh/376152/" 
scraper = JobMedleyScraper(url)
scraper.start()



            
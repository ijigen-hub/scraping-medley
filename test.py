from playwright.sync_api import sync_playwright
import re
import unicodedata



class JobMedleyScraper:
    def __init__(self, url):
        self.url = url
        self.page = None

    def start(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # 使用 headless=False 来查看页面加载过程
            self.page = browser.new_page()
            self.page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font"] else route.continue_())
            self.page.goto(self.url)

            print(self.get_basic_salary())

            # print(self.split_address()[0])
            # print(self.split_address()[1])
            # print(self.split_address()[2])
            # print(self.split_address()[3])

    def split_address(self) -> list:
        """
        住所情報を「都道府県」「市区町村」「その他」の3つの部分に分割してリストに格納します。

        :return: [都道府県, 市区町村, その他]
        """
        # 1. 指定したセレクタからテキスト情報を取得
        address_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("アクセス") + div div p:nth-of-type(1)')
        
        result = ["", "", "", ""]

        # 2. 都道府県を検出して抽出（都道府県は1～4文字の漢字であると仮定）
        prefecture_pattern = r'([一-龥]{1,4}県|[一-龥]{1,4}都|[一-龥]{1,4}府|[一-龥]{1,4}道)'
        prefecture_match = re.search(prefecture_pattern, address_text)
        
        # 5. 都道府県と市区町村の情報をリストに追加
        if prefecture_match:
            prefecture = prefecture_match.group(0)
            result[0] =  prefecture # 都道府県部分を[0]に入れる

        address_text = address_text.replace(prefecture, '').strip()

        # 3. 市区町村を検出して抽出（市区町村は1～4文字の漢字であると仮定）
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
        
        address_text = address_text.replace(city, '').strip()
        
        space_index = address_text.find(" ") 
        if space_index != -1:
            building = address_text[space_index + 1:]

        else:
            building = ''

        town = address_text.replace(building, '').strip()
        result[2] = self.convert_f_h(town)

        result[3] = self.convert_f_h(building)

        return result
    def get_annual_holidays(self) -> str:
        """
        「年間休日」に関する情報を取得し、年間休日の日数を抽出します。

        :return: 年間休日の日数（文字列）または空白文字列
        """
        # 1. 指定したセレクタからテキスト情報を取得
        holiday_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("休日") + div p')
        
        # 2. 「年間休日」の文字列があるか確認
        if '年間休日' or '年休' in holiday_text:
        
            # 3. 「年間休日」に続く1〜3桁の数字を抽出する正規表現パターン
            holiday_pattern = r'(年間休日|年休).*?(\d{1,3})'
            holiday_match = re.search(holiday_pattern, holiday_text)
        
            # 4. 数字が見つかった場合はその数字を文字列として返す
            return holiday_match.group(2) if holiday_match else ''
        else: return ''

    def get_trial_period(self) -> list:
        """
        試用期間の有無と期間（月数）をリスト形式で取得します。

        :return: [試用期間の有無 ('あり'または 'なし'), 試用期間の月数 (存在する場合の数値文字列)]
        """
        # 1. 指定したセレクタから情報を取得
        info_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与の備考") + div p')
        
        # 2. 「試用期間」が含まれているかを確認
        if '試用期間' not in info_text:
            return ['', '']  # 試用期間がない場合
        if '試用期間なし' in info_text:
            return ['なし', '']

        # 3. 「試用期間」がある場合のリスト初期化
        result = ['あり']

        #試用期間の月数を抽出する正規表現パターン1
        sentence_match = re.search(r'[^。]*試用期間[^。]*[。．]?', info_text)
        #試用期間の月数を抽出する正規表現パターン2
        month_pattern = r'試用期間.*?(\d+)(ヶ月|か月|カ月|ヵ月)' 
        month_match = re.search(month_pattern, info_text)

        if  month_match:
            result.append(month_match.group(1)+ "ヶ月")  # 月数（例: '3'）をリストに追加

        elif sentence_match:
            sentence = sentence_match.group(0)
            print(sentence)
            duration_match = re.search(r'([0-9０-９]+)(か月|ヶ月|カ月|ヵ月)', sentence)

            if duration_match:
                duration = duration_match.group(1)
                result.append(duration + "ヶ月")  # 月数（例: '3ヶ月'）をリストに追加
                return result
            else:
                result.append('')

        else:
            result.append('')

        return result

    def get_salary_range(self) -> list:
        """
        CSSセレクタ '.font-semibold.text-jm-sm.break-keep + div div' から給与情報を取得し、
        最低給与金額と最高給与金額をリストにして返します。

        :return: [最低給与金額, 最高給与金額]
        """
        # 1. 給与を取得
        salary_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与") + div div')
        
        wage_classification = ["月給", "時給", "年収"]
        for classification in wage_classification:
            if classification in salary_text:
                min_salary_pattern = r'{}(\d+,\d+)円'.format(classification)
                max_salary_pattern = r'{}\d+,\d+円〜(\d+,\d+)円'.format(classification)

                min_salary_match = re.search(min_salary_pattern, salary_text)
                min_salary = min_salary_match.group(1) if min_salary_match else ''
                
                # 4. 最高給与金額を検索
                max_salary_match = re.search(max_salary_pattern, salary_text)
                max_salary = max_salary_match.group(1) if max_salary_match else ''

                return [min_salary, max_salary]    

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
        salary_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与") + div')
        wage_classification = ["月給", "時給", "年収"]
        for classification in wage_classification:
            if classification in salary_text: return classification
        else: return ''

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

    def get_basic_salary(self) -> str:
        """
        CSSセレクタ '.font-semibold.text-jm-sm.break-keep + div p' から情報を取得し、
        「基本給」に関する給与情報を抽出して整形します。

        :return: 基本給情報（例: '150,000円' または '150,000円〜199,000円'）
        """
        # 1. 指定したセレクタのテキストを取得
        info_text = self.get_text('.font-semibold.text-jm-sm.break-keep:has-text("給与の備考") + div p')
    
        # 2. 基本給のパターンを検索
        # basic_salary_pattern1 = r'基本給.*?(\d{1,3}(?:,\d{3})*円(?:〜\d{1,3}(?:,\d{3})*円)?)'
        basic_salary_pattern = r'基本給.*?(\d{1,3}(?:,\d{3})*|\d+)円(?:[〜\-](\d{1,3}(?:,\d{3})*|\d+)円)?'

        # 3. パターン1を試し、見つからなければパターン2を試す
        salary_match = re.search(basic_salary_pattern, info_text)

        if salary_match:
            # 4. 基本給情報を取得
            salary_info = salary_match.group(1)
        
            # 5. そのままの情報を返す
            return salary_info
    
        # 「基本給」に関する情報が見つからなければ空文字列を返す
        return ''

    @staticmethod
    def convert_f_h(text: str) -> str:
        # 将全角字符转换为半角字符
        return unicodedata.normalize('NFKC', text)

# 使用示例
url = f"https://job-medley.com/hh/1132927/"#https://job-medley.com/hh/1000614/ 
#https://job-medley.com/hh/1143681/
#https://job-medley.com/hh/1132927/

scraper = JobMedleyScraper(url)
scraper.start()



            
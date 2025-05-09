# pip install selenium pandas webdriver-manager
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd
from .utils import *

# Chrome 드라이버 옵션 설정
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')

# 드라이버 실행
driver = webdriver.Chrome(options=options)

# 검색 키워드와 연도
keyword = "탄핵"
years = [2022, 2023, 2024, 2025]
results = []

for year in years:
    start_date = f"{year}.01.01"
    end_date = f"{year}.12.31"
    url = (
        f"https://search.naver.com/search.naver?ssc=tab.news.all&query={keyword}&sm=tab_opt&pd=3&ds={start_date}&de={end_date}&office_type=0&office_section_code=0"
    )

    driver.get(url)
    time.sleep(2)

    try:
        articles = driver.find_elements(By.CSS_SELECTOR, ".wkoGSxciodT_CpdKvH30 .dZQQMujvOqnxG1bUQsg6") # 실행시 안될 경우 변경 필요
        if articles:
            for article in articles[:3]:  # 최대 3개만 반복
                try:
                    title_span = article.find_element(By.CSS_SELECTOR, ".sds-comps-text.sds-comps-text-type-headline1")
                    title = title_span.text
                    link_a = article.find_element(By.CSS_SELECTOR, ".sds-comps-vertical-layout .sds-comps-full-layout > a")
                    link = link_a.get_attribute("href")
                    date_elem = article.find_elements(By.CSS_SELECTOR, "div.sds-comps-profile-info > span:nth-child(3) > span")[0]
                    date = date_elem.text
                    results.append({"year": year, "title": title, "link": link, "date": date})
                except Exception as inner_e:
                    results.append({"year": year, "title": "부분 오류 발생", "link": "", "date": str(inner_e)})
        else:
            results.append({"year": year, "title": "기사 없음", "link": "", "date": ""})
    except Exception as e:
        results.append({"year": year, "title": "전체 오류 발생", "link": "", "date": str(e)})

driver.quit()

# 결과 출력
df = pd.DataFrame(results)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_colwidth', None)

if(results):
    for item in results:
        get_news(item.get("link"))
        print()

    print()
    print("전체 리스트")
    print(df)
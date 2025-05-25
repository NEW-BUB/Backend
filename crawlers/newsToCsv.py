# pip install feedparser requests beautifulsoup4
import feedparser
import requests
from bs4 import BeautifulSoup, NavigableString
import csv

# 연합뉴스 RSS 카테고리 및 URL 정보
news_source = {
    "연합뉴스": {
        "rss_url": "https://www.yna.co.kr/rss/",
        "categories": {
            "politics.xml": "정치",
            "economy.xml": "경제",
            "market.xml": "경제",
            "industry.xml": "산업",
            "society.xml": "사회",
            "local.xml": "지역",
            "international.xml": "국제",
            "culture.xml": "문화·라이프",
            "health.xml": "건강",
            "entertainment.xml": "문화·라이프",
            "sports.xml": "스포츠",
        },
        "csv_file": "연합뉴스 데이터.csv",
    },
    "경향신문": {
        "rss_url": "https://www.khan.co.kr/rss/rssdata/",
        "categories": {
            "politic_news.xml": "정치",
            "economy_news.xml": "경제",
            "society_news.xml": "사회",
            "local_news.xml": "지역",
            "kh_world.xml": "국제",
            "culture_news.xml": "문화·라이프",
            "kh_sports.xml": "스포츠",
            "science_news.xml": "과학",
            "life_news.xml": "문화·라이프",
        },
        "csv_file": "경향신문 데이터.csv",
    },
    "조선일보": {
        "rss_url": "https://www.chosun.com/arc/outboundfeeds/rss/category/",
        "categories": {
            "politics/?outputType=xml": "정치",
            "economy/?outputType=xml": "경제",
            "national/?outputType=xml": "사회",
            "international/?outputType=xml": "국제",
            "culture-life/?outputType=xml": "문화·라이프",
            "sports/?outputType=xml": "스포츠",
            "entertainments/?outputType=xml": "문화·라이프",
        },
        "csv_file": "조선일보 데이터.csv",
    },
    "동아일보": {
        "rss_url": "https://rss.donga.com/",
        "categories": {
            "politics.xml": "정치",
            "national.xml": "사회",
            "economy.xml": "경제",
            "international.xml": "국제",
            "science.xml": "과학",
            "culture.xml": "문화·라이프",
            "sports.xml": "스포츠",
            "health.xml": "건강",
        },
        "csv_file": "동아일보 데이터.csv",
    },
    "한겨레": {
        "rss_url": "https://www.hani.co.kr/rss/",
        "categories": {
            "politics/": "정치",
            "economy/": "경제",
            "society/": "사회",
            "international/": "국제",
            "culture/": "문화·라이프",
            "sports/": "스포츠",
            "science/": "과학",
            "local_news.xml": "지역",
            "life_news.xml": "문화·라이프",
        },
        "csv_file": "한겨레 데이터.csv",
    }
}

fieldnames = ["categories", "title", "link", "description", "pubDate", "img_src", "text"]
    
def crawl_news(key):
    data = news_source.get(key)
    csv_file = data["csv_file"]
    rss_url = data["rss_url"]
    categories = data["categories"]

    # 기존 데이터 읽기
    try:
        with open(csv_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            existing_data = {row["link"]: row for row in reader}
    except FileNotFoundError:
        existing_data = {}
    
    for url, category in categories.items():
        print(f"[{category}] 크롤링 시작")
        feed = feedparser.parse(rss_url + url)
        if key == "조선일보":
            crawl_chosun_news(feed.entries, existing_data, category)
        else:
            for entry in feed.entries:
                if key == "연합뉴스":
                    crawl_yonhap_news(entry, existing_data, category)
                elif key == "경향신문":
                    crawl_kyunghyang_news(entry, existing_data, category)
                elif key == "동아일보":
                    crawl_donga_news(entry, existing_data, category)
                elif key == "한겨레":
                    crawl_hani_news(entry, existing_data, category)
    
    # 모든 데이터를 저장
    with open(csv_file, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_data.values())

    print("모든 카테고리 크롤링 완료!")


def crawl_yonhap_news(entry, existing_data, category):
    link = entry.link
    if link in existing_data:
        current_categories = existing_data[link]["categories"].split(", ")
        if category not in current_categories:
            current_categories.append(category)
            existing_data[link]["categories"] = ", ".join(current_categories)
        print(f"업데이트 완료: {entry.title} [{category}]")
    else:
        try:
            response = requests.get(link, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            div = soup.find("div", class_="story-news article")
            paragraphs = div.find_all("p")[:-2] if div else []
            text = " ".join(p.get_text(strip=True) for p in paragraphs)
            
            if hasattr(entry, "media_content"):
                for media in entry.media_content:
                    if media.get("type", "").startswith("image/"):
                        img_src = media.get("url")
                        break
            else:
                img_src = None
            
            article_data = {
                "categories": category,
                "title": entry.title,
                "link": link,
                "description": entry.description,
                "pubDate": entry.published,
                "img_src": img_src,
                "text": text or "본문 없음",
            }
            existing_data[link] = article_data
            
            print(f"저장 완료: {entry.title} [{category}]")
        except Exception as e:
            print(f"크롤링 실패: {link} ({e})")

def crawl_kyunghyang_news(entry, existing_data, category):
    link = entry.link
    if link in existing_data:
        current_categories = existing_data[link]["categories"].split(", ")
        if category not in current_categories:
            current_categories.append(category)
            existing_data[link]["categories"] = ", ".join(current_categories)
        print(f"업데이트 완료: {entry.title} [{category}]")
    else:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Referer": "https://www.khan.co.kr/",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        try:
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            div = soup.find("div", class_="art_photo")
            img_src = div.find("img")["src"] if div and div.find("img") else None
            
            div = soup.find("div", class_="art_body")
            paragraphs = div.find_all("p") if div else []
            text = " ".join(p.get_text(strip=True) for p in paragraphs)
            
            article_data = {
                "categories": category,
                "title": entry.title,
                "link": link,
                "description": entry.description,
                "pubDate": entry.updated,
                "img_src": img_src,
                "text": text or "본문 없음",
            }
            existing_data[link] = article_data
            
            print(f"저장 완료: {entry.title} [{category}]")
        except Exception as e:
            print(f"크롤링 실패: {link} ({e})")

from playwright.sync_api import sync_playwright
# pip install playwright
# playwright install

def crawl_chosun_news(entries, existing_data, category):
    with sync_playwright() as p:  # Playwright 컨텍스트 열기
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 2. 리소스 차단 함수 등록 (이미지, CSS, 폰트 차단)
        def block_resources(route):
            if route.request.resource_type in ["image", "stylesheet", "font"]:
                route.abort()
            else:
                route.continue_()
        page.route("**/*", block_resources)
    
        try:
            for entry in entries:
                link = entry.link
                if link in existing_data:
                    current_categories = existing_data[link]["categories"].split(", ")
                    current_text = existing_data[link]["text"]
                    if category not in current_categories:
                        current_categories.append(category)
                        existing_data[link]["categories"] = ", ".join(current_categories)
                    elif current_text == "본문 없음":
                        page = browser.new_page()  # 새 브라우저 페이지 생성
                        page.goto(link, timeout=30000)  # 60초 타임아웃으로 페이지 열기
                        page.wait_for_selector("section.article-body", timeout=15000)  # 본문 로딩 기다림
                        
                        # 본문 선택
                        content_elements = page.query_selector_all("section.article-body p")
                        text = " ".join(element.inner_text().strip() for element in content_elements)
                        print(text)
                        
                        existing_data[link]["text"] = text
                    print(f"업데이트 완료: {entry.title} [{category}]")
                else:
                    response = requests.get(link, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    if hasattr(entry, "media_content"):
                        for media in entry.media_content:
                            if media.get("type", "").startswith("image/"):
                                img_src = media.get("url")
                                break
                    else:
                        img_src = None
                        
                    page = browser.new_page()  # 새 브라우저 페이지 생성
                    page.goto(link, timeout=30000)  # 60초 타임아웃으로 페이지 열기
                    page.wait_for_selector("section.article-body", timeout=15000)  # 본문 로딩 기다림
                    
                    # 본문 선택
                    content_elements = page.query_selector_all("section.article-body p")
                    text = " ".join(element.inner_text().strip() for element in content_elements)
                    print(text)
                    
                    existing_data[link]["text"] = text
                    
                    article_data = {
                        "categories": category,
                        "title": entry.title,
                        "link": link,
                        "description": entry.description,
                        "pubDate": entry.updated,
                        "img_src": img_src,
                        "text": text or "본문 없음",
                    }
                    existing_data[link] = article_data
                    
                    print(f"저장 완료: {entry.title} [{category}]")
        except Exception as e:
            print(f"크롤링 실패: {link} ({e})")
        finally:
            browser.close()

def crawl_donga_news(entry, existing_data, category):
    link = entry.link
    if link in existing_data:
        current_categories = existing_data[link]["categories"].split(", ")
        if category not in current_categories:
            current_categories.append(category)
            existing_data[link]["categories"] = ", ".join(current_categories)
        print(f"업데이트 완료: {entry.title} [{category}]")
    else:
        try:
            response = requests.get(link, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            if hasattr(entry, "media_content"):
                for media in entry.media_content:
                    if media.get("type", "").startswith("image/"):
                        img_src = media.get("url")
                        break
            else:
                img_src = None
    
            # 본문 영역 찾기
            article_div = soup.find('section', class_='news_view')
            if not article_div:
                text = ''

            texts = []
            for element in article_div.descendants:
                if isinstance(element, NavigableString):
                    parent = element.parent
                    # 불필요한 태그를 제외
                    if parent.name not in ['script', 'style', 'p', 'br', 'div', 'body', 'html']:
                        text = element.strip()
                        if text:
                            texts.append(text)
            text = ' '.join(texts)
            text = text.replace("BYLINE", "").replace("//BYLINE", "").replace("//", "").strip()
            
            article_data = {
                "categories": category,
                "title": entry.title,
                "link": link,
                "description": entry.description,
                "pubDate": entry.updated,
                "img_src": img_src,
                "text": text or "본문 없음",
            }
            existing_data[link] = article_data
            
            print(f"저장 완료: {entry.title} [{category}]")
        except Exception as e:
            print(f"크롤링 실패: {link} ({e})")

def crawl_hani_news(entry, existing_data, category):
    link = entry.link
    if link in existing_data:
        current_categories = existing_data[link]["categories"].split(", ")
        if category not in current_categories:
            current_categories.append(category)
            existing_data[link]["categories"] = ", ".join(current_categories)
        print(f"업데이트 완료: {entry.title} [{category}]")
    else:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Referer": "https://www.khan.co.kr/",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        try:
            response = requests.get(link, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            video_div = soup.find("div", class_="video-wrap")  # 비디오 있는지 확인

            if video_div is None:  # 비디오가 없으면 이미지 찾기
                img_div = soup.find("div", class_="ArticleDetailContent_imageWrap__o8GzH")
                img_src = img_div.find("img")["src"] if img_div and img_div.find("img") else None
            else:
                img_src = None  # 비디오 있을 땐 이미지 무시
            
            div = soup.find("div", class_="article-text")
            paragraphs = div.find_all("p")[:-1] if div else []
            text = " ".join(p.get_text(strip=True) for p in paragraphs)
            
            div = soup.find("div", class_="ArticleDetailView_articleDetail__IT2fh")
            time = div.find("li", class_="ArticleDetailView_dateListItem__mRc3d").find("span").get_text()
            
            article_data = {
                "categories": category,
                "title": entry.title,
                "link": link,
                "description": None,
                "pubDate": time,
                "img_src": img_src,
                "text": text or "본문 없음",
            }
            existing_data[link] = article_data
            
            print(f"저장 완료: {entry.title} [{category}]")
        except Exception as e:
            print(f"크롤링 실패: {link} ({e})")
    

if __name__ == "__main__":
    crawl_news("연합뉴스")
    crawl_news("경향신문")
    crawl_news("조선일보")
    crawl_news("동아일보")
    crawl_news("한겨레")

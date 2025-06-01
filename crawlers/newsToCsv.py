# pip install feedparser requests beautifulsoup4
import feedparser
import requests
from bs4 import BeautifulSoup, NavigableString
import csv
import traceback
import asyncio
from playwright.async_api import async_playwright
import ast
import re

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
            "sports.xml": "스포츠"
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
            "life_news.xml": "문화·라이프"
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
            "entertainments/?outputType=xml": "문화·라이프"
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
            "health.xml": "건강"
        },
        "csv_file": "동아일보 데이터.csv",
    },
    "한겨레": {
        "rss_url": "https://www.hani.co.kr/rss/",
        "categories": {
            "politics": "정치",
            "economy": "경제",
            "society": "사회",
            "international": "국제",
            "culture": "문화·라이프",
            "sports": "스포츠",
            "science": "과학"
        },
        "csv_file": "한겨레 데이터.csv",
    },
    "jtbc": {
        "rss_url": "https://news-ex.jtbc.co.kr/v1/get/rss/section/",
        "categories": {
            "10": "정치",
            "20": "경제",
            "30": "사회",
            "40": "국제",
            "50": "문화·라이프",
            "60": "문화·라이프",
            "70": "스포츠"
        },
        "csv_file": "jtbc 데이터.csv",
    }
}
        
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Referer": "https://www.khan.co.kr/",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
}

import signal
import sys

def handle_sigint(sig, frame):
    print("\n🛑 사용자 중단 (Ctrl+C)")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_sigint)

# 비동기 Playwright 크롤러
async def crawl_news(key, existing_data):
    data = news_source.get(key)
    rss_url = data["rss_url"]
    categories = data["categories"]

    try:
        print(f"\n=={key} 뉴스 크롤링 시작==\n")
        for url, category in categories.items():
            print(f"\n[{category}] 카테고리 시작")
            feed = feedparser.parse(rss_url + url)

            if key in ["jtbc"]:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True)

                    try:
                        for entry in feed.entries:
                            link = entry.link

                            if link in existing_data:
                                update_category(existing_data, link, category)
                            else:
                                try:
                                    article_data = await crawl_playwright_news(key, entry, link, browser)
                                    if article_data is None:
                                        continue

                                    article_data["categories"] = [category]
                                    existing_data[link] = article_data

                                    title = article_data["title"]
                                    
                                    print(f"저장 완료: {title} [{category}]")
                                except Exception as e:
                                    print(f"크롤링 실패: {link} ({e})")
                                    print(traceback.format_exc())
                    finally:
                        if browser:
                            for context in browser.contexts:
                                await context.close()
                            await browser.close()
            else:
                for entry in feed.entries:
                    link = entry.link

                    if link in existing_data:
                        update_category(existing_data, link, category)
                    else:
                        try:
                            article_data = crawl_static_news(key, entry, link)
                            if article_data is None:
                                continue
                            article_data["categories"] = [category]
                            existing_data[link] = article_data
                            print(f"저장 완료: {entry.title} [{category}]")
                        except Exception as e:
                            print(f"크롤링 실패: {link} ({e})")
                            print(traceback.format_exc())

    except Exception as e:
        print(f"전체 실패: {e}")


def update_category(existing_data, link, category):
    raw_value = existing_data[link].get("categories", "[]")
    current_categories = ast.literal_eval(raw_value) if isinstance(raw_value, str) else raw_value

    if category not in current_categories:
        current_categories.append(category)
        existing_data[link]["categories"] = current_categories

    title = existing_data[link].get("title", "제목 없음")
    print(f"업데이트 완료: {title} [{category}]")


def crawl_static_news(key, entry, link):
    if key == "연합뉴스":
        return crawl_yonhap_news(entry, link)
    elif key == "경향신문":
        return crawl_kyunghyang_news(entry, link)
    elif key == "동아일보":
        return crawl_donga_news(entry, link)
    elif key == "한겨레":
        return crawl_hani_news(entry, link)
    return {}


async def crawl_playwright_news(key, entry, link, browser):
    if key == "jtbc":
        return await crawl_jtbc_news(entry, link, browser)
    return {}


def crawl_yonhap_news(entry, link):
    response = requests.get(link, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text,"html.parser")
    
    div = soup.find("div", class_="story-news article")
    paragraphs = div.find_all("p")[:-1] if div else []
    text = "\\n".join(p.get_text(strip=True) for p in paragraphs)
    
    if not text or text == "[]" or text == "\n\n" or text == "\n":
        print(link + " 본문 없음")
        return None
    
    if hasattr(entry, "media_content"):
        for media in entry.media_content:
            if media.get("type", "").startswith("image/"):
                img_src = media.get("url")
                break
    else:
        img_src = None
    
    div = soup.find("div", class_="writer-zone01")
    if div:
        a_tags = div.find(class_="tit-name").find_all("a")
        author = [a.get_text(strip=True) for a in a_tags]
    else:
        author = []
    
    article_data = {
        "title": entry.title,
        "link": link,
        "pubDate": entry.published,
        "img_src": img_src,
        "text": text,
        "author": author,
    }
    
    return article_data

def crawl_kyunghyang_news(entry, link):
    response = requests.get(link, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    div = soup.find("div", class_="art_body")
    paragraphs = div.find_all("p") if div else []
    text = "\\n".join(p.get_text(strip=True) for p in paragraphs)
    
    if not text or text == "[]" or text == "\n\n" or text == "\n":
        print(link + " 본문 없음")
        return None
    
    div = soup.find("div", class_="art_photo")
    img_src = div.find("img")["src"] if div and div.find("img") else None
    
    ul = soup.find("ul", class_="bottom")
    if ul:
        a_tags = ul.find("li", class_="editor").find_all("a")
        author = [a.get_text(strip=True) for a in a_tags]
    else:
        author = []
    
    article_data = {
        "title": entry.title,
        "link": link,
        "pubDate": entry.updated,
        "img_src": img_src,
        "text": text,
        "author": author
    }
    
    return article_data
                    
def crawl_donga_news(entry, link):
    response = requests.get(link, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    if hasattr(entry, "media_content"):
        for media in entry.media_content:
            if media.get("type", "").startswith("image/"):
                img_src = media.get("url")
                break
    else:
        img_src = None

    article_div = soup.find('section', class_='news_view')
    if not article_div:
        print(link + " 본문 없음")
        return None

    texts = []
    for element in article_div.descendants:
        if isinstance(element, NavigableString):
            parent = element.parent
            # 불필요한 태그를 제외
            if parent.name not in ['script', 'style', 'p', 'br', 'div', 'body', 'html']:
                text = element.strip()
                if text:
                    texts.append(text)
    text = '\\n'.join(texts)
    text = text.replace("BYLINE", "").replace("//BYLINE", "").replace("//", "").strip()
    
    if not text or text == "[]" or text == "\n\n" or text == "\n":
        print(link + " 본문 없음")
        return None
    
    byline_div = soup.find("div", class_="byline")
    if byline_div:
        byline_text = byline_div.get_text(separator="\n")
        author = re.findall(r"([\uac00-\ud7a3]{2,4}) 기자", byline_text)
    else:
        author = []
        
    article_data = {
        "title": entry.title,
        "link": link,
        "pubDate": entry.updated,
        "img_src": img_src,
        "text": text,
        "author": author,
    }
    return article_data

def crawl_hani_news(entry, link):
    response = requests.get(link, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    div = soup.find("div", class_="article-text")
    paragraphs = div.find_all("p")[:] if div else []
    text = "\\n".join(p.get_text(strip=True) for p in paragraphs)

    if not text or text == "[]" or text == "\n\n" or text == "\n":
        print(link + " 본문 없음")
        return None
    
    video_div = soup.find("div", class_="video-wrap")  # 비디오 있는지 확인

    if video_div is None:  # 비디오가 없으면 이미지 찾기
        img_div = soup.find("div", class_="ArticleDetailContent_imageWrap__o8GzH")
        img_src = img_div.find("img")["src"] if img_div and img_div.find("img") else None
    else:
        img_src = None  # 비디오 있을 땐 이미지 무시
    
    div = soup.find("div", class_="ArticleDetailView_articleDetail__IT2fh")
    time = div.find("li", class_="ArticleDetailView_dateListItem__mRc3d").find("span").get_text()
    
    div = soup.find("div", class_="ArticleDetailView_reporterList__waOKp")
    if div:
        a_tags = div.find_all("a")
        author = [a.get_text(strip=True) for a in a_tags]
    else:
        author = []
    
    article_data = {"title": entry.title,
        "link": link,
        "pubDate": time,
        "img_src": img_src,
        "text": text,
        "author": author,
    }
    return article_data

async def crawl_jtbc_news(entry, link, browser):
    response = requests.get(link, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    meta_tag = soup.find("meta", property="og:image")

    # content 속성 값 추출
    if meta_tag:
        img_src = meta_tag.get("content", "")
    else:
        img_src = None
    
    meta_tag = soup.find("meta", attrs={"name": "Author"})

    if meta_tag:
        content = meta_tag.get("content", "")
        author = [name.strip() for name in content.split(",")]
    else:
        author = []

    page = await browser.new_page()
    try:
        await page.goto(link, timeout=40000)
        await page.wait_for_selector("div.my-9iwogb", timeout=15000)
        html = await page.content()

        soup = BeautifulSoup(html, "html.parser")
        
        content_div = soup.select_one("div.my-9iwogb")

        for br in content_div.find_all("br"):
            br.replace_with("\\n")

        texts = [el.get_text(strip=True) for el in content_div.find_all(["span", "strong"])]
        text = "\\n".join(dict.fromkeys(texts))

        if not text or text == "[]" or text == "\n\n" or text == "\n":
            print(link + " 본문 없음")
            return None
        
        article_data = {
            "title": entry.title,
            "link": link,
            "pubDate": entry.updated,
            "img_src": img_src,
            "text": text,
            "author": author,
        }
        return article_data
    finally:
        await page.close()

# pip install feedparser requests beautifulsoup4
import feedparser
import requests
from bs4 import BeautifulSoup
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
    }
}

fieldnames = ["categories", "title", "link", "description", "pubDate", "img_src", "text"]

def crawl_yonhap_news(data):
    csv_file = data.get("csv_file")
    rss_url = data.get("rss_url")
    categories = data.get("categories")

    # 기존 데이터를 읽어와 중복 확인용 링크-데이터 매핑 생성
    try:
        with open(csv_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            existing_data = {row["link"]: row for row in reader}
    except FileNotFoundError:
        existing_data = {}

    new_data = []

    # RSS 피드 크롤링
    for url, category in categories.items():
        print(f"[{category}] 크롤링 시작")
        feed = feedparser.parse(rss_url + url)

        for entry in feed.entries:
            link = entry.link

            # 중복 확인 및 카테고리 업데이트
            if link in existing_data:
                current_categories = existing_data[link]["categories"].split(", ")
                if category not in current_categories:
                    current_categories.append(category)
                    existing_data[link]["categories"] = ", ".join(current_categories)
                print(f"업데이트 완료: {entry.title} [{category}] (기존 데이터)")
            else:
                # 새 데이터 크롤링
                try:
                    response = requests.get(link, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")

                    # 이미지 URL 추출
                    div = soup.find("div", class_="comp-box photo-group")
                    img_src = div.find("img")["src"] if div and div.find("img") else None

                    # 본문 추출
                    div = soup.find("div", class_="story-news article")
                    if div:
                        paragraphs = div.find_all("p")[:-2]  # 마지막 두 문단 제외
                        text = " ".join(p.get_text(strip=True) for p in paragraphs)
                    else:
                        text = "본문 없음"

                    # 새 데이터 추가
                    new_entry = {
                        "categories": category,
                        "title": entry.title,
                        "link": link,
                        "description": entry.description,
                        "pubDate": entry.published,
                        "img_src": img_src,
                        "text": text,
                    }
                    new_data.append(new_entry)
                    print(f"저장 완료: {entry.title} [{category}] (새 데이터)")
                except Exception as e:
                    print(f"크롤링 실패: {link} ({e})")

        print(f"[{category}] 크롤링 완료\n")

    # 기존 데이터와 새 데이터를 합쳐서 저장
    with open(csv_file, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        # 기존 데이터 저장
        for entry in existing_data.values():
            writer.writerow(entry)

        # 새로운 데이터 저장
        for entry in new_data:
            writer.writerow(entry)

    print("모든 카테고리 크롤링 완료!")
    
crawl_yonhap_news

if __name__ == "__main__":
    crawl_yonhap_news(news_source["연합뉴스"])

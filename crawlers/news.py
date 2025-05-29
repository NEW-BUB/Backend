from .keyword_ai import *
import csv
import traceback

from .newsToCsv import *

def news_crawling(keys):
    for key in keys:
        data = news_source.get(key)
        csv_file = data["csv_file"]
        
        try:
            with open(csv_file, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                existing_data = {row["link"]: row for row in reader}
        except FileNotFoundError:
            existing_data = {}
            
        try:
            asyncio.run(crawl_news(key, existing_data))
        except Exception as e:
            print(traceback.format_exc())
        finally:
            with open(csv_file, mode="w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(existing_data.values())

            print("\n모든 카테고리 크롤링 완료!")

def get_news_keywords(csv_file, start, end):
    try:
        with open(csv_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            existing_data = {row["link"]: row for row in reader}
            link_list = [row for row in existing_data.keys()]
    except FileNotFoundError:
        existing_data = {}
    
    # 뉴스 키워드 추출 
    try:
        for link in link_list[start:end]:
            print(existing_data[link]["title"])
            
            text = existing_data[link]["text"]
            print(text)
            
            keywords = existing_data[link]["keywords"]
            if keywords != "" and keywords != "[]":
                print(f"exist keywords:{keywords}")
            else:
                keywords = extract_keywords(text)
                if keywords == []:
                    break
                print(keywords)
                
                existing_data[link]["keywords"] = keywords
                
                time.sleep(4.5) # 1분당 15개의 데이터 키워드
            print()
    except Exception as e:
        print(traceback.format_exc())
    finally:
        fieldnames = ["categories", "keywords", "title", "link", "author", "pubDate", "img_src", "text"]
        with open(csv_file, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_data.values())

if __name__ == "__main__":
    keys = ["연합뉴스", "경향신문", "조선일보", "동아일보", "한겨레", "jtbc"]
    news_crawling(keys)
    
    news_files = ["연합뉴스 데이터.csv", "경향신문 데이터.csv", "조선일보 데이터.csv", "동아일보 데이터.csv", "한겨레 데이터.csv"]
    csv_file = news_files[0]
    start = 0
    end = start + 2
    get_news_keywords(csv_file, start, end)
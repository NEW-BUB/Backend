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

if __name__ == "__main__":
    keys = ["연합뉴스", "경향신문", "조선일보", "동아일보", "한겨레", "jtbc"]
    news_crawling(keys)
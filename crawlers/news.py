import csv
import traceback
import time

import pandas as pd
import ast
import os
import json
from collections import defaultdict
from enum import Enum

from .keyword_ai import *
from .newsToCsv import *

fieldnames = ["categories", "keywords", "title", "link", "author", "pubDate", "img_src", "text"]

def keyword_count(csv_files):
    def summarize_keywords_across_files(csv_files):
        keyword_summary = defaultdict(lambda: {"count": 0})

        for file in csv_files:
            # 언론사 이름 추출
            media_name = os.path.basename(file).replace(" 데이터.csv", "").replace(".csv", "")
            
            df = pd.read_csv(file)

            for idx, row in df.iterrows():
                keywords_raw = row["keywords"]
                title = row["title"]

                if pd.isna(keywords_raw) or pd.isna(title):
                    continue

                try:
                    keywords = ast.literal_eval(keywords_raw)
                    for kw in keywords:
                        keyword_summary[kw]["count"] += 1
                        if media_name not in keyword_summary[kw]:
                            keyword_summary[kw][media_name] = []
                        keyword_summary[kw][media_name].append(title)
                except Exception as e:
                    print(f"Error parsing keywords at row {idx} in {file}: {e}")

        return keyword_summary

    Type = Enum("Type", "SUMMARY LITTLE")
    def save_summary_to_json(summary, json_file, type: Type):
        if type == "SUMMARY":
            summary_dict = {kw: dict(data) for kw, data in summary.items()}
            # 정렬된 리스트
            sorted_summary = dict(
                sorted(summary_dict.items(), key=lambda x: x[1]["count"], reverse=True)
            )
        elif type == "LITTLE":
            sorted_summary = [kw for kw in summary.keys() if summary[kw]["count"] <= 2]
        else:
            sorted_summary = []
        
        # 저장
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(sorted_summary, f, ensure_ascii=False, indent=2)
        
        
    result = summarize_keywords_across_files(csv_files)

    # JSON으로 저장
    save_summary_to_json(result, "keyword_summary.json", "SUMMARY")
    save_summary_to_json(result, "little_keyword.json", "LITTLE")

    count1 = 0 # 3개 이상인 키워드
    count2 = 0 # 2개 이하인 키워드드
    for key in result.keys():
        if(result[key]["count"]>2):
            count1+=1
        else:
            count2+=1
        
    print(f"3개 이상인 키워드 개수 : {count1}")
    print(f"2개 이하인 키워드 개수 : {count2}")

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

def get_news_keywords(csv_file):
    try:
        with open(csv_file, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            existing_data = {row["link"]: row for row in reader}
            link_list = [row for row in existing_data.keys()]
    except FileNotFoundError:
        existing_data = {}
    
    # 뉴스 키워드 추출 
    try:
        for link in link_list:
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
                
                time.sleep(5) # 1분당 15개의 데이터 키워드
            print()
    except Exception as e:
        print(traceback.format_exc())
    finally:
        with open(csv_file, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_data.values())

if __name__ == "__main__":
    keys = ["연합뉴스", "경향신문", "동아일보", "한겨레", "jtbc"]
    news_files = ["연합뉴스 데이터.csv", "경향신문 데이터.csv", "동아일보 데이터.csv", "한겨레 데이터.csv", "jtbc 데이터.csv"]
    
    # 뉴스 크롤링
    # news_crawling(keys)
    
    # 뉴스 키워드 추출
    csv_file = news_files[2] # 현재 추출할 키워드 csv
    # get_news_keywords(csv_file)
    
    # 뉴스 키워드 카운팅팅
    keyword_count(news_files)
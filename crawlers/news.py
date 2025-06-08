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

def keyword_count(csv_files, count):
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
        
    result = summarize_keywords_across_files(csv_files)

    count1 = 0 # 3개 이상인 키워드
    count2 = 0 # 2개 이하인 키워드드
    for key in result.keys():
        if(result[key]["count"]>count):
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

# CSV에서 키워드 로드
import pandas as pd
import ast

def load_keywords_from_csv(file_list, json_data=[]):
    keywords = set()  # 키워드를 저장할 set
    news = list()  # 뉴스 내용을 저장할 list
    keyword_to_category = {}  # 키워드와 카테고리 매핑을 위한 딕셔너리

    for file in file_list:
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            keyword = row["keywords"]
            categories = [] if pd.isna(row.get("categories", None)) else ast.literal_eval(row["categories"])

            # 카테고리 정보를 함께 저장
            if pd.isna(keyword):
                continue
            try:
                kw_list = ast.literal_eval(keyword)
                keywords.update(kw for kw in kw_list if kw not in json_data)

                for kw in kw_list:
                    if kw not in keyword_to_category:
                        keyword_to_category[kw] = []
                    for category in categories:
                        if category not in keyword_to_category[kw]:
                            keyword_to_category[kw].append(category)

                news.append(keyword)
            except Exception as e:
                print(f"Error parsing keywords in {file}: {e}")

    # {"키워드": ["카테고리1", "카테고리2"], "키워드2": []} 형식으로 반환
    return (list(keywords), news, keyword_to_category)


Type = Enum("Type", "LITTLE")
def save_to_json(data, json_file, count=2, type: Type = ""):
    if type == "LITTLE":
        new_data = [kw for kw in data.keys() if data[kw]["count"] <= count]
    else:
        new_data = data
    
    # 저장
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

def delNoImgData(news_files):
    for csv_file in news_files:
        try:
            with open(csv_file, mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                existing_data = {row["link"]: row for row in reader}
                link_list = [link for link in existing_data.keys()]
        except FileNotFoundError:
            existing_data = {}
            
        for link in link_list:
            print(existing_data[link]["img_src"])
            if(existing_data[link]["img_src"] == ""):
                del existing_data[link]
            
        with open(csv_file, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_data.values())

if __name__ == "__main__":
    keys = ["연합뉴스", "경향신문", "동아일보", "한겨레", "jtbc"]
    news_files = ["연합뉴스 데이터.csv", "경향신문 데이터.csv", "동아일보 데이터.csv", "한겨레 데이터.csv", "jtbc 데이터.csv"]
    laws_file = ["bill_data.csv"]
    
    # 뉴스 크롤링
    # news_crawling(keys)
    
    # img 없는 데이터 삭제
    # delNoImgData(news_files)
    
    # 뉴스 키워드 추출
    # csv_file = news_files[2] # 현재 추출할 키워드 csv
    # get_news_keywords(csv_file)
    
    # 뉴스 키워드 카운팅
    result = keyword_count([news_files[0]], 2)
    # save_to_json(result, "keyword.json", 2, "LITTLE")

    # 키워드 로드
    news_keywords, news, keyword_category = load_keywords_from_csv([news_files[0], laws_file[0]])
    print(keyword_category)
    # print(f"\n===== 총 뉴스 {len(news)}개, 총 뉴스 키워드 {len(news_keywords)}개")
    # save_to_json(news_keywords, "news_keywords.json")
    save_to_json(keyword_category, "keyword_category.json")
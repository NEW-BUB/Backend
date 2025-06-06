import ast
import csv
import traceback
import json

csv_files = [
    "연합뉴스 데이터.csv",
    "경향신문 데이터.csv",
    "jtbc 데이터.csv",
    "동아일보 데이터.csv",
    "한겨레 데이터.csv"
]

fieldnames = ["categories", "keywords", "title", "link", "author", "pubDate", "img_src", "text"]

with open("keyword_clean.json", "r", encoding="utf-8") as f:
    keyword_mapping = json.load(f)

# 정규화 함수
def normalize_keyword(kw):
    kw_clean = kw.strip()
    return keyword_mapping.get(kw_clean, kw_clean)

def flatten_keywords(keywords):
    flat_list = []
    for item in keywords:
        if isinstance(item, list):
            flat_list.extend(flatten_keywords(item))  # 재귀 호출
        else:
            flat_list.append(item)
    return flat_list

for csv_file in csv_files:
    # 언론사 이름 추출
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
            keywords = existing_data[link]["keywords"]
            
            keywords = ast.literal_eval(keywords)
            
            keywords = [kw.replace(" ", "") for kw in keywords]
            
            # keywords = [normalize_keyword(kw) for kw in keywords]
            
            # keywords = flatten_keywords(keywords)
            
            existing_data[link]["keywords"] = list(set(keywords))
    except Exception as e:
        print(traceback.format_exc())
    finally:
        print("done!")
        with open(csv_file, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(existing_data.values())
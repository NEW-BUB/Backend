import pandas as pd
import json
import os
import ast

# CSV에서 키워드 로드
def load_keywords_from_csv(file_list, json_data=[]):
    keywords = set()
    news = list()
    for file in file_list:
        df = pd.read_csv(file)
        for keyword in df["keywords"]:
            news.append(keyword)
            if pd.isna(keyword):
                continue
            try:
                kw_list = ast.literal_eval(keyword)
                keywords.update(kw for kw in kw_list if kw not in json_data)
            except Exception as e:
                print(f"Error parsing keywords in {file}: {e}")
    return (list(keywords), news)

# JSON 파일 로드
def load_json(json_file):
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "news_keywords": [],
        "laws_keywords": [],
        "news_laws_matching": {},
        "chunk_progress": {} 
    }

# JSON 저장
def save_json(json_file, json_data):
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

# 메인 실행
if __name__ == "__main__":
    # CSV 파일 경로
    news_files = ["연합뉴스 데이터.csv"]
    laws_file = ["bill_data.csv"]
    json_file = "news_keywords.json"

    # 키워드 로드
    news_keywords, news = load_keywords_from_csv(news_files)
    
    print(f"\n===== 총 뉴스 {len(news)}개, 총 뉴스 키워드 {len(news_keywords)}개")
    
    save_json(json_file, news_keywords)

import pandas as pd
import json
import time
import google.generativeai as genai
import os
import re
import traceback
from app.core.config import settings

GEMINI_API_KEY = settings.GEMINI_API_KEY

# 리스트 분할 함수
def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]

# 키워드 매칭 함수
def gemini_match_keywords(news_keywords: str, laws_keywords: list) -> list:
    if news_keywords is None or laws_keywords is None:
        return []

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    뉴스 키워드: '{news_keywords}'
    
    아래 법안 키워드 리스트 중 뉴스 키워드와 의미상 가장 관련 있는 것 3~5개를 추출해 주세요.
    
    법안 키워드 리스트: {json.dumps(chunk, ensure_ascii=False)}
    
    출력은 반드시 파이썬 리스트 형식으로 주세요.
    예시: ['키워드1', '키워드2', '키워드3']
    다른 문장은 출력하지 마세요.
    """

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()

        # 마크다운 제거
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1].strip()

        # 리스트 부분만 추출
        match = re.search(r"\[.*?\]", result_text, re.DOTALL)
        if not match:
            print("[파싱 실패] 리스트 형식이 아님")
            return []

        list_str = match.group(0)
        keywords = eval(list_str)

        if not isinstance(keywords, list):
            print("[파싱 실패] 리스트 형식이 아님")
            return []

        return keywords
    except Exception as e:
        print(traceback.format_exc())
        return []

import ast

# CSV에서 키워드 로드
def load_keywords_from_csv(file_list, json_data):
    keywords = set()
    for file in file_list:
        df = pd.read_csv(file)
        for item in df["keywords"]:
            if pd.isna(item):
                continue
            try:
                kw_list = ast.literal_eval(item)
                keywords.update(kw for kw in kw_list if kw not in json_data)
            except Exception as e:
                print(f"Error parsing keywords in {file}: {e}")
    return list(keywords)

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
    news_files = [
        "연합뉴스 데이터.csv", "경향신문 데이터.csv",
        "조선일보 데이터.csv", "동아일보 데이터.csv", "한겨레 데이터.csv"
    ]
    laws_file = ["bill_data.csv"]
    json_file = "keyword_mapping.json"

    # 기존 JSON 데이터 로딩
    json_data = load_json(json_file)

    # 키워드 로드
    news_keywords = load_keywords_from_csv(news_files, json_data["news_keywords"])
    # laws_keywords = load_keywords_from_csv(laws_file, json_data["laws_keywords"])
    # news_keywords = [] # 새로운 데이터 로드 안함
    laws_keywords = [] # 새로운 데이터 로드 안함


    # 법안 키워드 병합 및 저장
    existing_laws = json_data.get("laws_keywords", [])
    combined_laws_keywords = existing_laws + laws_keywords
    json_data["laws_keywords"] = combined_laws_keywords
    
    # print(combined_laws_keywords)

    # 뉴스 키워드 병합 및 저장
    existing_news = json_data.get("news_keywords", [])
    combined_news_keywords = existing_news + news_keywords
    json_data["news_keywords"] = combined_news_keywords
    
    # print(combined_news_keywords)

    print(f"\n===== 총 뉴스 키워드 {len(combined_news_keywords)}개 / 총 법안 키워드 {len(combined_laws_keywords)}개 =====\n")

    match_source = combined_laws_keywords
    chunck_list = list(chunk_list(match_source, 1000))
    chunck_size = len(chunck_list)
    check = 0

    # Gemini 매칭
    for news_kw in combined_news_keywords:
        if json_data.get("chunk_progress", {}).get(news_kw, 0) >= chunck_size:
            print(f"[SKIP] 이미 처리된 뉴스 키워드: {news_kw}")
            continue

        if not match_source:
            print(f"[SKIP] {news_kw} → 매칭할 법안 키워드 없음")
            continue

        # 현재 뉴스 키워드 chunk 진행 상태 가져오기
        current_chunk_idx = json_data.get("chunk_progress", {}).get(news_kw, 0)

        for idx, chunk in enumerate(chunck_list):
            if idx < current_chunk_idx:
                print(f"[SKIP] {news_kw} chunk {idx} (이미 처리됨)")
                continue

            print(f"[PROCESS] {news_kw} chunk {idx} / 법안 키워드 {len(chunk)}개")

            try:
                chunk_result = gemini_match_keywords(news_kw, chunk)
                print(f"{news_kw} chunk {idx} result: {chunk_result}")

                if not chunk_result:
                    print(f"[WARNING] {news_kw} chunk {idx} → 응답 없음")
                    check = 1
                    break

                # 결과 저장
                existing = set(json_data["news_laws_matching"].get(news_kw, []))
                json_data["news_laws_matching"][news_kw] = list(existing | set(chunk_result))

                # 현재 chunk index 업데이트
                json_data.setdefault("chunk_progress", {})[news_kw] = idx + 1

                # 중간 저장
                save_json(json_file, json_data)
                print(f"[SAVED] {news_kw} chunk {idx} 저장 완료 🚀\n")

                time.sleep(10)

            except Exception as e:
                print(f"[ERROR] '{news_kw}' chunk {idx} 실패: {e}")
                save_json(json_file, json_data)
        
        print("")
        
        if check == 1:
            break

    print("\n===== 전체 작업 완료! =====")

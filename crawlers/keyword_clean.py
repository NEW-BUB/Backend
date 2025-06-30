import ast
import csv
import traceback
import json

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

def keyword_clean(csv_files, fieldnames):
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

def load_law_keyword(file):
    existing_data = set()
    try:
        with open(file, mode="r", encoding="utf-8") as file_obj:
            reader = csv.DictReader(file_obj)
            for row in reader:
                # row["keywords"] 는 문자열로 저장돼 있을 것 (예: "['법안', '정치']")
                keywords = ast.literal_eval(row["keywords"])
                existing_data.update(keywords)
    except FileNotFoundError:
        existing_data = set()
    return list(existing_data)

def load_news_keyword(files):
    existing_data = set()
    try:
        for file in files:
            with open(file, mode="r", encoding="utf-8") as file_obj:
                reader = csv.DictReader(file_obj)
                for row in reader:
                    # row["keywords"] 는 문자열로 저장돼 있을 것 (예: "['법안', '정치']")
                    keywords = ast.literal_eval(row["keywords"])
                    existing_data.update(keywords)
    except FileNotFoundError:
        existing_data = set()
    return list(existing_data)


def load_data(files):
    try:
        for file in files:
            with open(file, mode="r", encoding="utf-8") as file_obj:
                reader = csv.DictReader(file_obj)
                existing_data = {row["link"]:row for row in reader}
    except FileNotFoundError:
        existing_data = {}
    return existing_data

def keyword_clean1(bill_file, news_files, fieldnames, file):
    law_keywords = load_law_keyword(bill_file)
    print(law_keywords)
    print(len(law_keywords))

    news_keywords = load_news_keyword(news_files)
    print(news_keywords)
    print(len(news_keywords))

    intersection = set(news_keywords) & set(law_keywords)
    print(intersection)
    print(len(intersection))

    news_data = load_data(news_files)
    bill_data = load_data(bill_file)

    count1 = 0
    count2 = 0
    count3 = []

    intersection = set(intersection)  # set 으로 바꿔야 lookup 속도 빠름

    new_news_data = {}

    for key in news_data.keys():
        keywords = ast.literal_eval(news_data[key]["keywords"])
        
        new_keywords = []

        count4 = 0
        for keyword in keywords:
            if keyword in intersection:
                count4 += 1
                new_keywords.append(keyword)

        if count4 > 0:
            count3.append(count4)
            count1 += 1
            new_news_data[key] = news_data[key]
            new_news_data[key]["keywords"] = list(new_keywords)
        else:
            count2 += 1

        

    print(f"키워드가 있는 데이터: {count1}, 키워드가 없는 데이터: {count2}")
    print(f"{count3}")
    for i in range(1, 10):
        print(f"{i}: {count3.count(i)}")
        
    with open(file, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(new_news_data.values())
    
    # count1 = 0
    # count2 = 0
    # for key in bill_data.keys():
    #     keywords = ast.literal_eval(bill_data[key]["keywords"])
    #     if(keywords in list(intersection)):
    #         count1 += 1
    #     else:
    #         count2 += 2
    
    # print(f"키워드가 있는 데이터: {count1}, 키워드가 없는 데이터: {count2}")

# import re
# import google.generativeai as genai

# from app.core.config import settings

# GEMINI_API_KEY = settings.GEMINI_API_KEY

# def extract_keywords(sentence: str) -> list:
#     if sentence is 'X':
#         return []

#     # Gemini API 설정
#     genai.configure(api_key=GEMINI_API_KEY)  # <- 본인의 API 키 입력

#     # 모델 선택
#     model = genai.GenerativeModel("gemini-1.5-flash")
    
#     print(sentence)

#     prompt = f"""
#     다음 키워드 리스트에 있는 키워드 각각의 관련된 카테고리를 1~3개 추출해 주세요. 
#     카테고리는 반드시 아래의 카테고리 리스트에서만 추출해야합니다. **다른 카테고리를 넣지 마세요**
    
#     카테고리 리스트 : ['경제', '스포츠', '지역', '사회', '정치', '문화·라이프', '산업', '건강', '국제']

#     키워드 리스트: "{sentence}"

#     출력 형식은 파이썬 리스트 형태로 주세요. 예: [['카테고리1', '카테고리2'],['카테고리3']]
#     출력은 각 키워드의 카테고리 리스트가 리스트 형식으로 반환됩니다
#     다른 값은 반환하지 마세요
#     출력은 **반드시 키워드 순으로** 주세요.
#     """
    
#     try:
#         response = model.generate_content(prompt)
#         result_text = response.text.strip()

#         print(result_text)

#         # 마크다운 제거
#         if result_text.startswith("```"):
#             result_text = result_text.split("```")[1].strip()

#         # "keywords = ..." 또는 유사한 불필요한 코드 제거
#         match = re.search(r"\[.*?\]", result_text, re.DOTALL)
#         if not match:
#             return ["[파싱 실패] 리스트 형식이 아님"]

#         list_str = match.group(0)
#         keywords = eval(list_str)  # 여기에만 eval 적용

#         return keywords if isinstance(keywords, list) else ["[파싱 오류] 리스트 아님"]

#     except Exception as e:
#         import traceback
#         print(traceback.format_exc())
#         return []

# import time

if __name__ == "__main__":
    # news_files = [
    #     "연합뉴스 데이터.csv",
    #     "경향신문 데이터.csv",
    #     "jtbc 데이터.csv",
    #     "동아일보 데이터.csv",
    #     "한겨레 데이터.csv"
    # ]
    
    # bill_files = [
    #     "bill_data.csv"
    # ]

    # fieldnames1 = ["categories", "keywords", "title", "link", "author", "pubDate", "img_src", "text"]
    # fieldnames2 = ["number","name","date","proponents",'parties',"link","processing_status","processing_result","summary","keywords"]

    # with open("keyword_clean.json", "r", encoding="utf-8") as f:
    #     keyword_mapping = json.load(f)
    
    # keyword_clean(news_files, fieldnames1);
    # keyword_clean(bill_files, fieldnames2);
    
    # keyword_clean1(bill_files[0], [news_files[0]], fieldnames1, "new_news_data.csv");
    
    with open("keyword1.json", "r", encoding="utf-8") as f:
        keywords = json.load(f)
    
    
    id_list = []
    
    for row in keywords:
        if(row["id"] in id_list):
            keywords.remove(row)
        else:
            id_list.append(row["id"])
    
    print(len(id_list))
    
    with open("keyword1.json", "w", encoding="utf-8") as f:
        json.dump(keywords, f, ensure_ascii=False, indent=2)
    
    # new_keyword["category"] = []
    
    
    # for i in range(0, len(new_keyword["name"]), 500):
    #     category = extract_keywords(new_keyword["name"][i:i+500])
    #     print(category)
    #     keywords["category"].append(*category)
    
    # new_keywords = []
    # for i in range(len(new_keyword["id"])):
    #     dic = {}
    #     dic["id"] = new_keyword["id"][i]
    #     dic["name"] = new_keyword["name"][i]
    #     dic["category"] = new_keyword["category"][i]
    #     new_keywords.append(dic)
    #     time.sleep(5)
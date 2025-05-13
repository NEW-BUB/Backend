from msilib.schema import Billboard

import requests
import xml.etree.ElementTree as ET

from app.core.config import settings

BILL_INFO_API_KEY = settings.BILL_INFO_API_KEY
INTEGRATED_BILL_INFO_API_KEY = settings.INTEGRATED_BILL_INFO_API_KEY

def fetch_bill_nums():
    url = "http://apis.data.go.kr/9710000/BillInfoService2/getBillInfoList"
    page = 1
    per_page = 1000  # 최대 1000까지 가능
    total_pages = None

    bill_nums = []
    bill_contents = []

    # while True:
    params = {
        "serviceKey": BILL_INFO_API_KEY,
        "numOfRows": per_page,
        "pageNo": page
    }

    response = requests.get(url, params=params)
    response.encoding = "utf-8"

    root = ET.fromstring(response.text)

    # totalCount 정보 가져오기
    if total_pages is None:
        total_count = int(root.findtext("body/totalCount"))
        total_pages = (total_count + per_page - 1) // per_page
        print(f"전체 건수: {total_count}, 총 페이지 수: {total_pages}")

    # item 반복
    items = root.findall(".//item")
    # if not items:
    #     break  # 더 이상 없으면 종료

    for item in items:
        number = item.findtext("billNo", default="(번호 없음)")
        bill_nums.append(number)
        contents = item.findtext("summary", default = "X")
        bill_contents.append(contents)

    page += 1
    # if page > total_pages:
    #     break

    print(bill_nums)

    return bill_nums, bill_contents


def fetch_bill_xml(bill_nums):
    url = "https://open.assembly.go.kr/portal/openapi/ALLBILL"

    size = 100

    for i in bill_nums:
        page = 1  # 각 BILL_NO마다 page 초기화
        while True:
            params = {
                "KEY": INTEGRATED_BILL_INFO_API_KEY,
                "Type": "xml",
                "pIndex": page,
                "pSize": size,
                "BILL_NO": i
            }

            response = requests.get(url, params=params)
            response.encoding = "utf-8"

            root = ET.fromstring(response.text)
            rows = root.findall(".//row")

            if not rows:
                break  # 이 BILL_NO에 대해 더 이상 데이터 없음

            for item in rows:
                name = item.findtext("BILL_NM", default="")
                bill_url = item.findtext("LINK_URL", default="")
                # print(f'의안명: {name}')
                # print(f'url: {bill_url}')
                # print("-" * 40)

            page += 1  # 다음 페이지로 이동




# 실행
if __name__ == "__main__":
    bill_nums, bill_contents = fetch_bill_nums()
    # fetch_bill_xml(bill_nums)

    # 의안 키워드 추출
    from crawlers import keywords

    for i in range(2, 50):
        text = bill_contents[i]

        print(text)

        print("\n=== 외부 라이브러리 없이 키워드 추출 ===")
        try:
            result_df = keywords.get_keyword(text)
            print(result_df)
        except Exception as e:
            print(f"그냥 키워드 실행 오류: {e}")

        print("\n=== kiwi를 이용한 키워드 추출 ===")
        try:
            keywords2 = keywords.extract_keywords_with_kiwi(text, top_n=10)
            for keyword, count in keywords2:
                print(f"{keyword}: {count}회")
        except Exception as e:
            print(f"kiwi 실행 오류: {e}")
            print("pip install kiwipiepy로 kiwi를 설치해보세요.")

        print("\n=== KKMA 키워드 추출 ===")
        try:
            keywords4 = keywords.extract_keywords_with_kkma(text, top_n=10)
            for keyword, count in keywords4:
                print(f"{keyword}: {count}회")
        except Exception as e:
            print(f"KKMA 실행 오류: {e}")

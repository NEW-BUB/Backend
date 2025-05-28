from msilib.schema import Billboard

import os
import csv
import time
import requests
import xml.etree.ElementTree as ET

from .keyword_ai import *

from app.core.config import settings

BILL_INFO_API_KEY = settings.BILL_INFO_API_KEY
INTEGRATED_BILL_INFO_API_KEY = settings.INTEGRATED_BILL_INFO_API_KEY

def fetch_bill(page):
    url = "http://apis.data.go.kr/9710000/BillInfoService2/getBillInfoList"
    per_page = 500  # 최대 19000까지 가능
    total_pages = None


    # while True:
    params = {
        "serviceKey": BILL_INFO_API_KEY,
        "numOfRows": per_page,
        "pageNo": page
    }

    response = requests.get(url, params=params)
    response.encoding = "utf-8"

    root = ET.fromstring(response.text)

    total_count = int(root.findtext("body/totalCount"))
    total_pages = (total_count + per_page - 1) // per_page
    print(f"전체 건수: {total_count}, 총 페이지 수: {total_pages}")

    # item 반복
    items = root.findall(".//item")
    # if not items:
    #     break  # 더 이상 없으면 종료

    csv_number = []

    with open('bill_data.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            csv_number.append(row["number"])

    try:
        with open('bill_data.csv', 'a', encoding='utf-8') as csvfile:
            header = [ 'number', 'name', 'proponent', 'date', 'link', 'processing_status', 'processing_result', 'contents', 'keywords' ]
            csv_writer = csv.writer(csvfile)
            if os.stat('bill_data.csv').st_size > 0:
                pass
            else:
                csv_writer.writerow(header)

            # while True:
            #
            #     if page > total_pages:
            #         break

            for item in items:
                bill_info = []

                number = item.findtext("billNo", default="")

                if number in csv_number:
                    continue

                bill_info.append(number)

                fetch_bill_xml(number, bill_info)

                contents = item.findtext("summary", default = "")
                if contents is "":
                    continue

                bill_info.append(contents)

                keywords = extract_keywords(contents)
                bill_info.append(keywords)

                csv_writer.writerow(bill_info)

                if keywords is not []:
                    time.sleep(4.1)


                # page += 1

    except FileNotFoundError:
        print('csv_writter is not open')




def fetch_bill_xml(bill_num, bill_info):
    """

    Args:
        bill_num
    의안번호를 통해 의안정보통합 api에서
    의안명, 대표발의자, 발의일자, 처리상태, 처리결과, 링크를 불러와
    bill_data.csv에 저장

    """

    url = "https://open.assembly.go.kr/portal/openapi/ALLBILL"

    page = 1
    size = 100

    while True:
        params = {
            "KEY": INTEGRATED_BILL_INFO_API_KEY,
            "Type": "xml",
            "pIndex": page,
            "pSize": size,
            "BILL_NO": bill_num
        }

        response = requests.get(url, params=params)
        response.encoding = "utf-8"

        root = ET.fromstring(response.text)
        rows = root.findall(".//row")

        if not rows:
            break  # 이 BILL_NO에 대해 더 이상 데이터 없음

        for item in rows:
            name = item.findtext("BILL_NM", default="")
            bill_info.append(name)

            proponent = item.findtext("PPSR_NM", default="")
            bill_info.append(proponent)

            date = item.findtext("PPSL_DT", default="")
            bill_info.append(date)

            link_url = item.findtext("LINK_URL", default="")
            bill_info.append(link_url)

            processing_date = [
                date,
                item.findtext("JRCMIT_PROC_DT", default=""),
                item.findtext("LAW_PROC_DT", default=""),
                item.findtext("RGS_RSLN_DT", default=""),
                item.findtext("PROM_DT", default="")
            ]
            processing_status = 5 - processing_date.count("")
            bill_info.append(processing_status)

            processing_variable = { 2:"JRCMIT_PROC_RSLT", 3:"LAW_PROC_RSLT", 4:"RGS_CONF_RSLT" }
            processing_result = item.findtext(processing_variable.get(processing_status, ""), default="")
            bill_info.append(processing_result)

        page += 1  # 다음 페이지로 이동




# 실행
if __name__ == "__main__":
    # 인수로 페이지 수(1~38)  넘겨줘야 됨.
    fetch_bill(2)

    # # 페이지당 의안번호 확인
    # url = "http://apis.data.go.kr/9710000/BillInfoService2/getBillInfoList"
    # page = 2
    # per_page = 500  # 최대 19000까지 가능
    # total_pages = None
    #
    # # while True:
    # params = {
    #     "serviceKey": BILL_INFO_API_KEY,
    #     "numOfRows": per_page,
    #     "pageNo": page
    # }
    #
    # response = requests.get(url, params=params)
    # response.encoding = "utf-8"
    #
    # root = ET.fromstring(response.text)
    #
    # total_count = int(root.findtext("body/totalCount"))
    # total_pages = (total_count + per_page - 1) // per_page
    # print(f"전체 건수: {total_count}, 총 페이지 수: {total_pages}")
    #
    # # item 반복
    # items = root.findall(".//item")
    #
    # bill_numbers = []
    # for item in items:
    #     bill_numbers.append(item.findtext("billNo", default=""))
    #
    # print(bill_numbers)

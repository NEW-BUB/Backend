import json
import os
import csv
import time
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

from .keyword_ai import *

from app.core.config import settings

BILL_INFO_API_KEY = settings.BILL_INFO_API_KEY
INTEGRATED_BILL_INFO_API_KEY = settings.INTEGRATED_BILL_INFO_API_KEY


def fetch_bill_ppsr(bill_id):
    """

        Args:
            bill_id, bill_info

        의안 제안자정보 api
        Return:
            제안자명, 제안자 정당명을 반환

    """

    lawmakers_22nd = [ '강경숙', '강대식', '강득구', '강명구', '강민국', '강선영', '강선우', '강승규', '강유정', '강준현', '강훈식',
                       '고동진', '고민정', '곽규택', '곽상언', '구자근', '권성동', '권영세', '권영진', '권칠승', '권향엽', '김건',
                       '김교흥', '김기웅', '김기표', '김기현', '김남근', '김남희', '김대식', '김도읍', '김동아', '김문수', '김미애',
                       '김민석', '김민전', '김병기', '김병주', '김상욱', '김상훈', '김석기', '김선교', '김선민', '김성원', '김성환',
                       '김성회', '김소희', '김승수', '김승원', '김영배', '김영진', '김영호', '김영환', '김예지', '김용만', '김용민',
                       '김용태', '김우영', '김원이', '김위상', '김윤', '김윤덕', '김은혜', '김장겸', '김재섭', '김재원', '김정재',
                       '김정호', '김종민', '김종양', '김주영', '김준혁', '김준형', '김태년', '김태선', '김태호', '김한규', '김현',
                       '김현정', '김형동', '김희정', '나경원', '남인순', '노종면', '맹성규', '모경종', '문금주', '문대림', '문정복',
                       '문진석', '민병덕', '민형배', '민홍철', '박균택', '박대출', '박덕흠', '박민규', '박범계', '박상웅', '박상혁',
                       '박선원', '박성민', '박성준', '박성훈', '박수민', '박수영', '박수현', '박용갑', '박은정', '박정', '박정하',
                       '박정현', '박정훈', '박주민', '박준태', '박지원', '박지혜', '박찬대', '박충권', '박해철', '박형수', '박홍근',
                       '박홍배', '박희승', '배준영', '배현진', '백선희', '백승아', '백종헌', '백혜련', '복기왕', '부승찬', '서명옥',
                       '서미화', '서범수', '서삼석', '서영교', '서영석', '서왕진', '서일준', '서지영', '서천호', '성일종', '소병훈',
                       '손명수', '송기헌', '송석준', '송언석', '송옥주', '송재봉', '신동욱', '신성범', '신영대', '신장식', '신정훈',
                       '안규백', '안도걸', '안상훈', '안철수', '안태준', '안호영', '양문석', '양부남', '어기구', '엄태영', '염태영',
                       '오기형', '오세희', '용혜인', '우원식', '우재준', '위성곤', '위성락', '유동수', '유상범', '유영하', '유용원',
                       '윤건영', '윤상현', '윤영석', '윤재옥', '윤종군', '윤종오', '윤준병', '윤한홍', '윤호중', '윤후덕', '이강일',
                       '이개호', '이건태', '이광희', '이기헌', '이달희', '이만희', '이병진', '이상식', '이상휘', '이성권', '이성윤',
                       '이소영', '이수진', '이양수', '이언주', '이연희', '이용선', '이용우', '이원택', '이인선', '이인영', '이재강',
                       '이재관', '이재명', '이재정', '이정문', '이정헌', '이종배', '이종욱', '이주영', '이준석', '이철규', '이춘석',
                       '이학영', '이해민', '이해식', '이헌승', '이훈기', '인요한', '임광현', '임미애', '임오경', '임이자', '임종득',
                       '임호선', '장경태', '장동혁', '장종태', '장철민', '전용기', '전재수', '전종덕', '전진숙', '전현희', '정동만',
                       '정동영', '정성국', '정성호', '정연욱', '정을호', '정일영', '정점식', '정준호', '정진욱', '정청래', '정춘생',
                       '정태호', '정혜경', '정희용', '조경태', '조계원', '조배숙', '조승래', '조승환', '조은희', '조인철', '조정식',
                       '조정훈', '조지연', '주진우', '주철현', '주호영', '진선미', '진성준', '진종오', '차규근', '차지호', '채현일',
                       '천준호', '천하람', '최기상', '최민희', '최보윤', '최수진', '최은석', '최형두', '추경호', '추미애', '한기호',
                       '한민수', '한병도', '한정애', '한준호', '한지아', '한창민', '허성무', '허영', '허종식', '홍기원', '황명선',
                       '황운하', '황정아', '황희'
                       ]

    url = "https://open.assembly.go.kr/portal/openapi/BILLINFOPPSR"
    page = 1
    per_page = 500  # 최대 5000까지 가능

    proponent = []
    party = []

    while True:
        params = {
            "KEY": INTEGRATED_BILL_INFO_API_KEY,
            "Type": "xml",
            "pIndex": page,
            "pSize": per_page,
            "BILL_ID": bill_id
        }

        response = requests.get(url, params=params)
        response.encoding = "utf-8"

        root = ET.fromstring(response.text)
        rows = root.findall(".//row")

        if not rows:
            break  # 이 BILL_NO에 대해 더 이상 데이터 없음

        for item in rows:
            ppsr_nm = item.findtext("PPSR_NM", default="")
            if ppsr_nm not in lawmakers_22nd: continue

            proponent.append(ppsr_nm)

            ppsr_poly_nm = fetch_bill_ppsr_plpt(ppsr_nm)
            party.append(ppsr_poly_nm)

        page += 1  # 다음 페이지로 이동

    return proponent, party


def find_party_by_name_from_file(name, party_data):
    for party, members in party_data.items():
        if name in members:
            return party
    return "소속 정당 없음"

def fetch_bill_ppsr_plpt(name):
    # JSON 파일 읽기
    try:
        with open('a.json', 'r', encoding='utf-8') as jsonfile:
            party_data = json.load(jsonfile)
        print(f"JSON 파일에서 {len(party_data)}개의 정당 정보를 읽었습니다.")
    except FileNotFoundError:
        print("a.json 파일을 찾을 수 없습니다.")
        exit()

    party = find_party_by_name_from_file(name, party_data)
    if party == "소속 정당 없음": return

    return party




def fetch_bill():
    """

    의안정보 통합 api
    의안 정보를 csv에 저장

    """

    url = "https://open.assembly.go.kr/portal/openapi/ALLBILL"
    size = 100
    number = 2210604

    csv_number = []

    with open('bill_data.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            csv_number.append(row["number"])

    try:
        with open('bill_data.csv', 'a', encoding='utf-8') as csvfile:

            header = ['number', 'name', 'date', 'link', 'processing_status', 'processing_result', 'summary',
                      'keywords', 'proponent', 'party']
            csv_writer = csv.writer(csvfile)
            if os.stat('bill_data.csv').st_size > 0:
                pass
            else:
                csv_writer.writerow(header)

        while True:
            page = 1
            while True:
                params = {
                    "KEY": INTEGRATED_BILL_INFO_API_KEY,
                    "Type": "xml",
                    "pIndex": page,
                    "pSize": size,
                    "BILL_NO": number
                }

                response = requests.get(url, params=params)
                response.encoding = "utf-8"

                root = ET.fromstring(response.text)
                rows = root.findall(".//row")

                if not rows:
                    break  # 이 BILL_NO에 대해 더 이상 데이터 없음

                for item in rows:
                    bill_no = item.findtext("BILL_NO", default="")
                    if number in csv_number:
                        continue
                    bill_nm = item.findtext("BILL_NM", default="")
                    date = item.findtext("PPSL_DT", default="")

                    link_url = item.findtext("LINK_URL", default="")

                    processing_date = [
                        date,
                        item.findtext("JRCMIT_PROC_DT", default=""),
                        item.findtext("LAW_PROC_DT", default=""),
                        item.findtext("RGS_RSLN_DT", default=""),
                        item.findtext("PROM_DT", default="")
                    ]
                    processing_status = 5 - processing_date.count("")

                    processing_variable = {2: "JRCMIT_PROC_RSLT", 3: "LAW_PROC_RSLT", 4: "RGS_CONF_RSLT"}
                    processing_result = item.findtext(processing_variable.get(processing_status, ""), default="")

                    summary = crawl_bill_summary(link_url)

                    bill_id = item.findtext("BILL_ID", default="")
                    proponent, party = fetch_bill_ppsr(bill_id)

                    if proponent == []:
                        continue

                    # 키워드 추출 수정 필요
                    keywords = extract_keywords(bill_nm + "\n" + summary)

                    bill_info = [bill_no, bill_nm, date, link_url, processing_status, processing_result, summary, keywords, proponent, party]

                    # csv_writer.writerow(bill_info)
                    # time.sleep(4.1)

                page += 1  # 다음 페이지로 이동

            number -= 1

    except FileNotFoundError:
        print('csv_writter is not open')


def crawl_bill_summary(url):
    """

    Args:
        url: 의안 정보 시스템의 링크 url

    Returns: 제안이유 및 주요내용을 크롤링하여 반환

    """

    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    summary_text = ""
    div = soup.select_one('div#summaryHiddenContentDiv')
    if div:
        # <br>을 \n으로 변환하여 텍스트 추출
        text = div.get_text(separator='\\n', strip=True)
        return text
    else:
        print("해당 요소가 없습니다.")

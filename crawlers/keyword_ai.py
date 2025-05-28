import re
import google.generativeai as genai

from app.core.config import settings

GEMINI_API_KEY = settings.GEMINI_API_KEY

# 키워드 추출 함수
def extract_keywords(sentence: str) -> list:
    if sentence is 'X':
        return []

    # Gemini API 설정
    genai.configure(api_key=GEMINI_API_KEY)  # <- 본인의 API 키 입력

    # 모델 선택
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
    다음 문장에서 핵심 키워드를 5~10개 추출해 주세요. 
    키워드는 가능한 한 명사 중심으로, 주제나 정책의 핵심 요소를 반영해야 합니다.

    문장: "{sentence}"

    출력 형식은 파이썬 리스트 형태로 주세요. 예: ['키워드1', '키워드2', '키워드3']
    """

    response = model.generate_content(prompt)

    # 결과에서 리스트 추출 (단순 문자열 파싱)
    # 예: ['청년', '주거 지원', '정책'] 형태의 문자열로 응답이 옴
    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()

        # 마크다운 제거
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1].strip()

        # "keywords = ..." 또는 유사한 불필요한 코드 제거
        match = re.search(r"\[.*?\]", result_text, re.DOTALL)
        if not match:
            return ["[파싱 실패] 리스트 형식이 아님"]

        list_str = match.group(0)
        keywords = eval(list_str)  # 여기에만 eval 적용

        return keywords if isinstance(keywords, list) else ["[파싱 오류] 리스트 아님"]

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return []

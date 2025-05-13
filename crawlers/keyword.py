import re
from collections import Counter
from soynlp.word import WordExtractor
from soynlp.noun import LRNounExtractor

def extract_keywords(text, top_n=10):
    """
    한국어 텍스트에서 명사 키워드를 추출하는 함수 (soynlp 사용)

    Args:
        text (str): 키워드를 추출할 텍스트
        top_n (int): 반환할 상위 키워드 개수

    Returns:
        list: (키워드, 빈도수) 튜플의 리스트
    """
    # 텍스트 전처리
    text = text.lower()  # 소문자 변환
    text = re.sub(r'[^\w\s]', ' ', text)  # 특수문자 제거

    # 한국어 불용어 목록 (필요에 따라 확장 가능)
    stopwords = [
        '이', '그', '저', '것', '이것', '그것', '저것',
        '나', '너', '우리', '당신', '그들', '저희', '자기',
        '이런', '그런', '저런', '이렇게', '그렇게', '저렇게',
        '및', '에', '의', '을', '를', '이', '가', '은', '는',
        '로', '으로', '에서', '에게', '한테', '께', '와', '과',
        '이나', '나', '랑', '하고', '까지', '부터', '도', '만',
        '데', '같은', '같이', '처럼', '보다', '라고', '하다', '임',
        '있다', '없다', '되다', '하다', '때문', '때', '내', '그냥'
    ]

    # 명사 추출기 학습 (문서가 충분히 크다면 사용)
    if len(text) > 500:  # 텍스트가 충분히 긴 경우에만 학습
        noun_extractor = LRNounExtractor()
        nouns = noun_extractor.extract([text])
        nouns = nouns.keys()
    else:
        # 텍스트가 짧은 경우 WordExtractor 사용
        word_extractor = WordExtractor()
        words = word_extractor.extract([text]).keys()

        # 명사 후보 필터링 (간단한 휴리스틱)
        nouns = []
        for word in words:
            if len(word) > 1 and not any(char.isdigit() for char in word):
                nouns.append(word)

    # 단일 글자 명사와 불용어 제거
    filtered_nouns = [noun for noun in nouns if noun not in stopwords and len(noun) > 1]

    # 빈도수 계산
    noun_counter = Counter(filtered_nouns)

    # 상위 키워드 추출
    top_keywords = noun_counter.most_common(top_n)

    return top_keywords


def get_keyword(texts, stopwords=None):
    from krwordrank.word import summarize_with_keywords
    import pandas as pd
    import re

    if stopwords is None:
        stopwords = []

    # 🔸 기본 불용어 설정
    stopwords += [
        '있다', '한다', '위해', '대한', '통해', '및', '등', '제', '의', '있는',
        '하며', '하고', '에서', '으로', '그리고', '그', '위한', '도내', '이전',
        '지난', '내년', '있음을', '그는', '하는', '그의', '이후', '했다', '그녀',
        '저', '이런', '최근', '때문', '관련', '다른', '한', '이다', '하다', '을',
        '를', '이', '가', '들', '와', '과', '특히', '출시', '국내', '최신', '함께',
        '같이', '하지만', '그러나', '따라서', '게다가', '또는', '뿐만 아니라',
        '이라면', '이라서', '였으며', '했던', '때문에', '등을', '의해', '으로써',
        '매우', '굉장히', '아주', '잘', '조금', '좀', '같은', '정말', '많은', '모든',
        '서로', '오늘', '내일', '어제', '지금', '현재', '다가오는', '앞으로', '지난번',
        '올해', '우리', '너희', '너', '저희', '자신', '누구', '각자', '모든 사람',
        '사람들', '그것', '어떻게', '무엇', '왜', '다시', '거기', '저기', '여기', '거의',
        '대부분', '당시', '그날', '다음', '그때', '이번', '언제나', '항상', '자주',
        '가끔', '종종', '한번', '정도', '약간', '대략', '완전히', '전혀', '더불어',
        '심지어', '더구나', '확실히', '분명히', '있다고', '가운데', '오후', '이라며',
        '이라', '경우', '결과', '이달', '있어', '대해', '기존', '향후', '비롯'
    ]

    # ✅ 텍스트 전처리
    texts = texts.lower()  # 모든 문자를 소문자로 변환
    texts = re.sub(r'[^가-힣a-z\s]', ' ', texts)  # 한글, 영문, 공백만 남김

    # ✅ 문장 분리 및 정리
    sentences = re.split(r'[.\n]', texts)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    # ✅ 키워드 추출
    keywords = summarize_with_keywords(
        sentences,
        min_count=2,
        max_length=10,
        beta=0.85,
        max_iter=20
    )

    filtered_keywords = {
        k: v for k, v in keywords.items()
        if not re.match(r'.*(다|이다|있다|한다|했다|하다|보다|한|를|될|을|이|가|의|은|는|로|까지|에|게|적|고|며|면|서|부터)$', k)  # 조사/어미로 끝나는 키워드 제거
    }

    # 🔸 DataFrame 변환
    df = pd.DataFrame(
        sorted(filtered_keywords.items(), key=lambda x: -x[1]),
        columns=['Keyword', 'Score']
    )

    # 불용어 제거: 'Keyword' 컬럼에서 불용어를 제외한 새로운 리스트 생성
    df['Keyword'] = df['Keyword'].apply(lambda x: ' '.join([word for word in x.split() if word not in stopwords]))

    # 불용어를 제외한 키워드만 남기기 (불용어가 포함된 키워드는 제거됨)
    df = df[df['Keyword'].str.strip() != '']

    return df.head(20)


# Kiwi
def extract_keywords_with_kiwi(text, top_n=10):
    """
    한국어 텍스트에서 명사 키워드를 추출하는 함수 (kiwipiepy 사용)

    Args:
        text (str): 키워드를 추출할 텍스트
        top_n (int): 반환할 상위 키워드 개수

    Returns:
        list: (키워드, 빈도수) 튜플의 리스트
    """
    try:
        from kiwipiepy import Kiwi

        # 텍스트 전처리
        text = text.lower()  # 소문자 변환
        text = re.sub(r'[^\w\s]', ' ', text)  # 특수문자 제거

        # 불용어 목록은 위와 동일
        stopwords = [
            '이', '그', '저', '것', '이것', '그것', '저것',
            '나', '너', '우리', '당신', '그들', '저희', '자기',
            '이런', '그런', '저런', '이렇게', '그렇게', '저렇게',
            '및', '에', '의', '을', '를', '이', '가', '은', '는',
            '로', '으로', '에서', '에게', '한테', '께', '와', '과',
            '이나', '나', '랑', '하고', '까지', '부터', '도', '만',
            '데', '같은', '같이', '처럼', '보다', '라고', '하다', '임',
            '있다', '없다', '되다', '하다', '때문', '때', '내', '그냥'
        ]

        # Kiwi 형태소 분석기 초기화
        kiwi = Kiwi()

        # 텍스트 분석 및 명사 추출
        result = kiwi.analyze(text)
        nouns = []

        for token in result[0][0]:
            if token.tag in ['NNG', 'NNP']:  # 일반 명사와 고유 명사만 추출
                nouns.append(token.form)

        # 단일 글자 명사와 불용어 제거
        filtered_nouns = [noun for noun in nouns if noun not in stopwords and len(noun) > 1]

        # 빈도수 계산
        noun_counter = Counter(filtered_nouns)

        # 상위 키워드 추출
        top_keywords = noun_counter.most_common(top_n)

        return top_keywords

    except ImportError:
        print("kiwipiepy 라이브러리가 설치되어 있지 않습니다. pip install kiwipiepy로 설치해주세요.")
        return []


# KKMA
def extract_keywords_with_kkma(text, top_n=10):
    """
    KKMA 형태소 분석기를 사용한 명사 키워드 추출

    Args:
        text (str): 키워드를 추출할 텍스트
        top_n (int): 반환할 상위 키워드 개수

    Returns:
        list: (키워드, 빈도수) 튜플의 리스트
    """
    try:
        from konlpy.tag import Kkma

        kkma = Kkma()

        # 텍스트 전처리
        text = text.lower()
        text = re.sub(r'[^\w\s가-힣]', ' ', text)

        # 불용어 목록 (기존과 동일)
        stopwords = [
            '이', '그', '저', '것', '이것', '그것', '저것',
            '나', '너', '우리', '당신', '그들', '저희', '자기',
            '이런', '그런', '저런', '이렇게', '그렇게', '저렇게',
            '및', '에', '의', '을', '를', '이', '가', '은', '는',
            '로', '으로', '에서', '에게', '한테', '께', '와', '과',
            '이나', '나', '랑', '하고', '까지', '부터', '도', '만',
            '데', '같은', '같이', '처럼', '보다', '라고', '하다', '임',
            '있다', '없다', '되다', '하다', '때문', '때', '내', '그냥'
        ]

        # 명사 추출
        nouns = kkma.nouns(text)

        # 필터링
        filtered_nouns = [noun for noun in nouns if noun not in stopwords and len(noun) > 1]

        # 빈도수 계산
        noun_counter = Counter(filtered_nouns)
        return noun_counter.most_common(top_n)

    except ImportError:
        print("konlpy 또는 KKMA가 설치되어 있지 않습니다. pip install konlpy로 설치해주세요.")
        return []


# 사용 예시
if __name__ == "__main__":
    text = """
    민사소송법 일부개정법률안 (이수진의원 대표발의) 발의연월일 : 2021. 2. 16. 의 안 8120 번 호 발 의 자 : 이수진ㆍ서동용ㆍ이원택 홍정민ㆍ이장섭ㆍ정청래 이규민ㆍ김두관ㆍ이개호 유정주ㆍ도종환ㆍ천준호 양정숙ㆍ오영환ㆍ최혜영 임오경ㆍ안호영ㆍ홍성국 이학영ㆍ정성호ㆍ윤준병 윤영덕ㆍ신현영ㆍ한병도 박성준ㆍ장경태ㆍ기동민 김원이ㆍ이용선ㆍ민병덕 양이원영ㆍ박홍근ㆍ변재일 임종성ㆍ문진석ㆍ신정훈 박광온ㆍ홍익표ㆍ진성준 정춘숙ㆍ김상희ㆍ김주영 남인순ㆍ김영주ㆍ주철현 서영교ㆍ황운하 의원 (47인) 

제안이유 및 주요내용
 「법원조직법」에 해사사건과 국제상사사건을 전담하는 전문법원으 로서 해사국제상사법원을 설치하도록 법적 근거를 마련함에 따라 해 -  사법원의 관할을 정할 필요가 있음. 이에 해사민사사건을 해사국제상사법원의 전속관할로 하고, 증거보 전 사건에서 검증 대상이 선박인 경우 그 소재지를 관할하는 해사국 제상사법원을 관할법원에 추가하려는 것임(안 

제24조의2  및 제24조의3 신설, 안 제376조). 참고사항 가. 해사행정사건은 「법원조직법 일부개정법률안」 제28조의8 신설을 통해 해사국제상사법원의 전속관할로 정하였음. 나. 이 법률안은 이수진의원이 대표발의한 「법원조직법 일부개정법률 안」(의안번호 제8118호), 「각급 법원의 설치와 관할구역에 관한 법률 일부개정법률안」(의안번호 제8121호), 「선박소유자 등의 책 임제한절차에 관한 법률 일부개정법률안」(의안번호 제8122호), 「유류오염손해배상 보장법 일부개정법률안」(의안번호 제8134호), 「중재법 일부개정법률안」(의안번호 제8119호), 「해양사고의 조사 및 심판에 관한 법률 일부개정법률안」(의안번호 제8133호)의 의결 을 전제로 하는 것이므로 같은 법률안이 의결되지 아니하거나 수정 의결 되는 경우에는 이에 맞추어 조정되어야 할 것임. 법률 제 호 민사소송법 일부개정법률안 민사소송법 일부를 다음과 같이 개정한다. 제24조의2 및 제24조의3을 각각 다음과 같이 신설한다. 제24조의2(해사민사사건의 관할) ① 「법원조직법」 제28조의8제1항제 1호의 해사민사사건은 제2조부터 제23조까지의 규정에 따른 관할법 원 소재지를 관할하는 해사국제상사법원 및 그 지원의 전속관할로 한다. ② 제1항에도 불구하고 당사자는 해사국제상사법원에 해사사건에 관한 소를 제기할 수 있다. 제24조의3(지방법원과 해사법원 사이의 관할의 지정) 제28조는 사건이 지방법원과 해사국제상사법원 가운데 어느 법원의 관할에 속하는지 분명하지 아니한 경우에 준용한다. 제376조제1항 후단 및 같은 조 제2항 중 “지방법원에”를 각각 “지방법 원, 해사국제상사법원 및 그 지원에”로 한다. 부 칙 제1조(시행일) 이 법은 2021년 9월 1일부터 시행한다. -  제2조(경과조치) 이 법 시행에 따라 해사국제상사법원의 관할에 속할 사건으로서 이 법 시행일 전날 해사국제상사법원이 아닌 법원에 계 속 중인 사건은 해사국제상사법원의 관할로 한다. 신·구조문대비표 

현 행
 

개 정 안
 <신 설> 제24조의2(해사민사사건의 관할) ① 「법원조직법」 제28조의7 제1항제1호의 해사민사사건은 제2조부터 제23조까지의 규정 에 따른 관할법원 소재지를 관 할하는 해사국제상사법원 및 그 지원의 전속관할로 한다. ② 제1항에도 불구하고 당사자 는 해사국제상사법원에 해사사 건에 관한 소를 제기할 수 있 다. <신 설> 제24조의3(지방법원과 해사법원 사이의 관할의 지정) 제28조는 사건이 지방법원과 해사국제상 사법원 가운데 어느 법원의 관 할에 속하는지 분명하지 아니 한 경우에 준용한다. 제376조(증거보전의 관할) ① 증 제376조(증거보전의 관할) ① --거보전의 신청은 소를 제기한 ---------------------------뒤에는 그 증거를 사용할 심급 ---------------------------의 법원에 하여야 한다. 소를 --------------------. ------제기하기 전에는 신문을 받을 ---------------------------사람이나 문서를 가진 사람의 ----------------------------  거소 또는 검증하고자 하는 목 ---------------------------적물이 있는 곳을 관할하는 지 ------------------------지방 방법원에 하여야 한다. 법원, 해사국제상사법원 및 그 지원에------------. ② 급박한 경우에는 소를 제기 ② ------------------------한 뒤에도 제1항 후단에 규정 ---------------------------된 지방법원에 증거보전의 신 --지방법원, 해사국제상사법원 청을 할 수 있다. 및 그 지원에----------------------------.
"""

    print("\n=== kiwi를 이용한 키워드 추출 ===")
    try:
        keywords2 = extract_keywords_with_kiwi(text, top_n=10)
        for keyword, count in keywords2:
            print(f"{keyword}: {count}회")
    except Exception as e:
        print(f"kiwi 실행 오류: {e}")
        print("pip install kiwipiepy로 kiwi를 설치해보세요.")

    print("\n=== KKMA 키워드 추출 ===")
    try:
        keywords4 = extract_keywords_with_kkma(text, top_n=10)
        for keyword, count in keywords4:
            print(f"{keyword}: {count}회")
    except Exception as e:
        print(f"KKMA 실행 오류: {e}")

    print("\n=== 외부 라이브러리 없이 키워드 추출 ===")

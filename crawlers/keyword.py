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


def get_keyword(text, stopwords=None, count=1):
    """
    한국어 텍스트에서 명사 키워드를 추출하는 함수 (krwordrank.word 사용)

    Args:
        text (str): 키워드를 추출할 텍스트
        stopwords (list): 키워드 불용어 리스트트
        count (list): 추출할 키워드의 최소 빈도 횟수

    Returns:
        list: (키워드, 점수) 튜플의 리스트
    """
    try:
        from krwordrank.word import summarize_with_keywords
        import pandas as pd

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
        text = text.lower()  # 모든 문자를 소문자로 변환
        text = re.sub(r'[^가-힣a-z\s]', ' ', text)  # 한글, 영문, 공백만 남김

        # ✅ 문장 분리 및 정리
        sentences = re.split(r'[.\n]', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        # ✅ 키워드 추출
        keywords = summarize_with_keywords(
            sentences,
            min_count=count,
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

        return df.head(20).values.tolist()
    
    except ImportError:
        print("krwordrank.word 라이브러리가 설치되어 있지 않습니다. pip install krwordrank.word로 설치해주세요.")
        return []


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
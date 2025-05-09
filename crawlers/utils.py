def get_keyword(texts, stopwords=None):
    from krwordrank.word import summarize_with_keywords
    import pandas as pd
    import re

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
        '심지어', '더구나', '확실히', '분명히', '있다고'
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

    # 🔸 조사 및 어미 제거 후 키워드 정리
    # def clean_keyword(keyword):
    #     # 특정 어미나 조사가 있으면 제거
    #     return re.sub(r'(이다|하다|한|를|을|이|가|에|의|은|는|한다|으로|로|까지|에|게|적|고)$', '', keyword)

    # cleaned_keywords = {clean_keyword(k): v for k, v in keywords.items() if clean_keyword(k)}
    
    filtered_keywords = {
        k: v for k, v in keywords.items()
        if not re.match(r'.*(이다|하다|한|를|을|이|가|에|의|은|는|한다|으로|로|까지|에|게|적|고)$', k)  # 조사/어미로 끝나는 키워드 제거
    }

    # 🔸 불용어 제거
    for stopword in stopwords:
        texts = re.sub(r'\b' + stopword + r'\b', ' ', texts)  # 단어 단위 제거

    # 🔸 DataFrame 변환
    df = pd.DataFrame(
        sorted(filtered_keywords.items(), key=lambda x: -x[1]), 
        columns=['Keyword', 'Score']
    )
    return df.head(20)



def get_news(url):
    # pip install newspaper3k lxml_html_clean
    from newspaper import Article 
    import re
    
    def clean_text(text):
        lines = text.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                continue  # 빈 줄 제거

            # 줄 전체 제거 조건 추가: VOD 안내, 브라우저 업그레이드 등 안내 문구 제거
            if re.search(r'(VOD 시청 안내|어도비 플래시 플레이어|브라우저 업그레이드|서비스가 원할하지 않습니다)', line):
                continue

            # 줄 전체 제거 조건: '전경.', '모습.', 'ⓒ' 포함
            if re.search(r'(ⓒ|©|[전경|모습]\.)', line):
                continue  # 줄 자체 제거

            # 부분 제거 조건: 기자 이름, 이메일, 좋아요 등
            line = re.sub(r'[가-힣]+ ?기자', '', line)  # 기자 이름
            line = re.sub(r'[\w\.-]+@[\w\.-]+', '', line)  # 이메일
            line = re.sub(r'(응원수|좋아요|추천수|이미지 확대|닫기)[^\n]*', '', line)  # 좋아요, 응원수 등

            cleaned_lines.append(line.strip())

        return '\n'.join(cleaned_lines).strip()

    
    # 불용어 및 제외 조건
    stopwords = [
        "작가의", "이야기", "포함한", "최대", "매일", "출시", "국내", "정말로", 
        "사실", "보도에 따르면", "출처", "기자", "결국", "따라서","즉", "그래서", 
        "결과적으로", "검색"
    ]

    print(f"\n📰 기사 URL: {url}")

    try:
        article = Article(url, language='ko')
        article.download()
        article.parse()

        title = article.title
        date = article.publish_date
        image = article.top_image
        authors = article.authors
        text = clean_text(article.text)

        print("제목:", title)
        print("발행일:", date)
        print("대표 이미지 URL:", image)
        if authors: print("작성자:", authors)
        print("본문 일부:", text[:100], "...")
        # print("원래 본문:", article.text)
        print("변경된 본문:", text)
        print("키워드:", get_keyword(text, stopwords))
    except Exception as e:
        print("기사 처리 실패:", e)
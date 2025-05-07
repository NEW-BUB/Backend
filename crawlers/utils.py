def get_keyword(stopwords, pref):
    # pip install krwordrank
    from krwordrank.word import summarize_with_keywords
    import re
    
    if not pref : return

    pref = [pref]  # 단일 문자열을 리스트로 변환

    keywords = summarize_with_keywords(
        texts=pref,
        min_count=2,
        max_length=10,
        beta=0.85,
        max_iter=10
    )

    def clean_and_validate(word):
        # 특수문자 제거
        cleaned = re.sub(r'[,\.\(\)\[\]]', '', word)

        # 숫자 or 불용어 or 어미로 끝나면 제외
        if cleaned in stopwords:
            return None
        if re.fullmatch(r'\d+(\.\d+)?', cleaned):  # 정수 또는 소수
            return None
        if re.search(r'(다|니다|습니다|된다|이다|한다|됐다)$', cleaned):
            return None
        if not cleaned.strip():  # 빈 문자열 제거
            return None
        return cleaned

    cleaned_keywords = {}
    for word, score in sorted(keywords.items(), key=lambda x: -x[1])[:15]:
        cleaned = clean_and_validate(word)
        if cleaned:
            cleaned_keywords[cleaned] = score

    return list(cleaned_keywords.keys())


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
    stopwords = {
        '싶은', '작가의', '아니', '이야기', '그리고', '있는', '있을', '위한', '되어', '대상',
        '위해', '같은', '되는', '또', '이와', '이를', '이번', '등을', '또한', '더욱', '있도록',
        '포함한', '최대', '매일'
    }

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
        print("키워드:", get_keyword(stopwords, text))
    except Exception as e:
        print("기사 처리 실패:", e)
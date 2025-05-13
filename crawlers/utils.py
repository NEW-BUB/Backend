# pip install newspaper3k lxml_html_clean
from newspaper import Article 
import re
from .keyword import *
def get_news(url):
    
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
        "결과적으로", "검색", "문제", "즐길", "놀러", "나들", "열린", "넘어"
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
        
        # 키워드 추출
        print("\n=== 외부 라이브러리 없이 키워드 추출 ===")
        keywords1 = get_keyword(text, stopwords, 2)
        for keyword, score in keywords1:
            print(f"{keyword}: {score}")
        
        print("\n=== kiwi를 이용한 키워드 추출 ===")
        keywords2 = extract_keywords_with_kiwi(text, top_n=10)
        for keyword, count in keywords2:
            print(f"{keyword}: {count}회")

        print("\n=== KKMA 키워드 추출 ===")
        keywords3 = extract_keywords_with_kkma(text, top_n=10)
        for keyword, count in keywords3:
            print(f"{keyword}: {count}회")
    except Exception as e:
        print("기사 처리 실패:", e)
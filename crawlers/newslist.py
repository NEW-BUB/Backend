# pip install python-dotenv pydantic-settings
import urllib.request
import json

from .utils import *
from app.core.config import settings

client_id = settings.NAVER_CLIENT_ID
client_secret = settings.NAVER_CLIENT_SECRET

encText = urllib.parse.quote("환경")
display = 10
url = "https://openapi.naver.com/v1/search/news?query=" + encText + "&display=" + str(display)

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
response = urllib.request.urlopen(request)
rescode = response.getcode()

if(rescode==200):
    response_body = response.read()
    data = json.loads(response_body.decode('utf-8'))

    for item in data.get("items", []):
        get_news(item.get("originallink") or item.get("link"))
        print()
else:
    print("Error Code:" + rescode)

# --------------------------------------------------------------------------

# https://newsapi.org/docs/endpoints/top-headlines
# https://newsapi.org/account

# from newsapi import NewsApiClient 

# news_api_key = settings.NEWS_API_KEY

# newsapi = NewsApiClient(api_key=news_api_key)

# top_headlines = newsapi.get_top_headlines(country='us')

# print(top_headlines)

# --------------------------------------------------------------------------

# https://www.thenewsapi.com/documentation#
# https://www.thenewsapi.com/account/dashboard

# the_news_api_key = settings.THE_NEWS_API_KEY

# search = urllib.parse.quote("환경")
# language = "ko"
# limit = 3

# url = f"https://api.thenewsapi.com/v1/news/sources?api_token={the_news_api_key}&language={language}"
# url = f"https://api.thenewsapi.com/v1/news/all?api_token={the_news_api_key}&language={language}&limit={limit}&search={search}"

# request = urllib.request.Request(url)
# response = urllib.request.urlopen(request)
# rescode = response.getcode()

# if(rescode==200):
#     response_body = response.read()
#     data = json.loads(response_body.decode('utf-8'))
    
#     for item in data.get('data', []):
#         print(item)

#     for news_item in data.get('data', []):
#         print(f"Title: {news_item.get('title')}")
#         print(f"Description: {news_item.get('description')}")
#         print(f"URL: {news_item.get('url')}")
#         print(f"Published At: {news_item.get('published_at')}")
#         print(f"Source: {news_item.get('source')}")
#         print(f"Image URL: {news_item.get('image_url')}")
#         print("-" * 50)
# else:
#     print("Error Code:" + rescode)
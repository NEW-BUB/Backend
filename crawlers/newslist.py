# pip install python-dotenv pydantic-settings
import urllib.request
import json

from .utils import *
from app.core.config import settings

client_id = settings.NAVER_CLIENT_ID
client_secret = settings.NAVER_CLIENT_SECRET

encText = urllib.parse.quote("환경")
display = 5
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

    # print()
    # print("전체 리스트")
    # print(response_body.decode('utf-8'))
else:
    print("Error Code:" + rescode)
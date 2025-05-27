from app.database import Base

# 각 모델 클래스를 전부 import (metadata 수집을 위해 반드시 필요)
from .news import News
from .keyword import Keyword
from .party import Party
from .law import Law
from .category import Category
from .keyword_news import KeywordNews
from .keyword_law import KeywordLaw
from .keyword_party_contribution import KeywordPartyContribution
from .news_law import NewsLaw
from .law_party_contribution import LawPartyContribution
from .category_news import CategoryNews
from .category_keyword import CategoryKeyword


__all__ = ["News", "Keyword", "Party", "Law", "Category", "KeywordNews", "KeywordLaw", 
           "KeywordPartyContribution", "NewsLaw", "LawPartyContribution", "CategoryNews", 
           "CategoryKeyword"]
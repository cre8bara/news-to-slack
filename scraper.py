#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
import os
import sys

SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

def scrape_news():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get('http://touraz.kr/news', headers=headers, timeout=5)
        resp.encoding = 'utf-8'
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        news = []
        
        for article_div in soup.find_all('div', class_='ls-article'):
            link = article_div.find('a')
            if link:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                if href and title:
                    if not href.startswith('http'):
                        href = 'http://touraz.kr' + href if href.startswith('/') else 'http://touraz.kr/' + href
                    news.append({'title': title, 'link': href})
        
        return news
    except:
        return []

def send_slack(items):
    if not SLACK_WEBHOOK_URL or not items:
        return False
    
    today = datetime.now()
    date_str = today.strftime('%m월 %d일').lstrip('0').replace('월 0', '월 ')
    day_name = ['월', '화', '수', '목', '금', '토', '일'][today.weekday()]
    
    text = f"*{date_str} ({day_name})요일 오늘이슈*\n"
    text += "cre8bara의 오늘 하루도 응원합니다! 오늘의 관광 뉴스를 확인해보세요 :)\n\n"
    
    for i, news in enumerate(items, 1):
        text += f"{i}. {news['title']}\n{news['link']}\n\n"
    
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json={"text": text}, timeout=5)
        return resp.status_code == 200
    except:
        return False

news = scrape_news()
if news:
    selected = random.sample(news, min(5, len(news)))
    send_slack(selected)

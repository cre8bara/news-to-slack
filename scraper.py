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
        
        if resp.status_code != 200:
            print(f"Error: Status {resp.status_code}")
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        news = []
        
        for link in soup.find_all('a', class_='article-title'):
            title = link.get_text(strip=True)
            href = link.get('href', '')
            if href and title:
                if not href.startswith('http'):
                    href = 'http://touraz.kr' + href if href.startswith('/') else 'http://touraz.kr/' + href
                news.append({'title': title, 'link': href})
        
        print(f"Collected: {len(news)} news")
        return news
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def send_slack(items):
    if not SLACK_WEBHOOK_URL:
        print("No webhook URL")
        return False
    
    if not items:
        print("No news")
        return False
    
    today = datetime.now().strftime('%Y-%m-%d')
    text = f"📰 {today}\n\n"
    for i, news in enumerate(items, 1):
        text += f"{i}. {news['title']}\n{news['link']}\n\n"
    
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json={"text": text}, timeout=5)
        if resp.status_code == 200:
            print("Slack OK")
            return True
        else:
            print(f"Slack error: {resp.status_code}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

news = scrape_news()
if news:
    selected = random.sample(news, min(5, len(news)))
    send_slack(selected)
else:
    sys.exit(1)

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
        
        # <div class="ls-article"> 안의 링크만 찾기
        for article_div in soup.find_all('div', class_='ls-article'):
            link = article_div.find('a')
            if link:
                href = link.get('href', '')
                title = link.get_text(strip=True)
                
                if href and title:
                    if not href.startswith('http'):
                        href = 'http://touraz.kr' + href if href.startswith('/') else 'http://touraz.kr/' + href
                    news.append({'title': title, 'link': href})
        
        print(f"Collected: {len(news)} news")
        return news
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def send_slack(items):
    if not

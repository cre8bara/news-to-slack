#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random
import json
import os
import sys

# Slack Webhook URL (환경변수에서 가져오기)
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

def get_today_date():
    """오늘 날짜를 'YYYY년 MM월 DD일' 형식으로 반환"""
    today = datetime.now()
    return today.strftime('%Y년 %m월 %d일').lstrip('0').replace('년 0', '년 ').replace('월 0', '월 ')

def scrape_news():
    """touraz.kr/news에서 당일 뉴스 가져오기"""
    try:
        # 페이지 요청
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get('http://touraz.kr/news', headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"Error: 페이지 요청 실패 (Status: {response.status_code})")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_items = []
        
        # touraz.kr 구조: <a class="article"> 태그에 링크와 제목
        for article_link in soup.find_all('a', class_='article'):
            title = article_link.get_text(strip=True)
            link = article_link.get('href', '')
            
            # 링크 정규화
            if link:
                if not link.startswith('http'):
                    if link.startswith('/'):
                        link = 'http://touraz.kr' + link
                    else:
                        link = 'http://touraz.kr/' + link
                
                if title:
                    news_items.append({'title': title, 'link': link})
                    print(f"✓ 뉴스 수집: {title[:50]}... | {link}")
        
        print(f"\n✓ 총 수집된 뉴스: {len(news_items)}개")
        return news_items
    
    except Exception as e:
        print(f"Error: 뉴스 수집 실패 - {str(e)}")
        return []

def select_random_news(news_items, count=5):
    """뉴스 중 무작위로 5개 선택"""
    if len(news_items) <= count:
        return news_items
    return random.sample(news_items, count)

def send_to_slack(news_items):
    """Slack에 뉴스 전송"""
    if not SLACK_WEBHOOK_URL:
        print("Error: SLACK_WEBHOOK_URL 환경변수가 설정되지 않음")
        return False
    
    if not news_items:
        print("전송할 뉴스가 없습니다.")
        return False
    
    try:
        today = get_today_date()
        
        # Slack 메시지 구성
        text = f"📰 *{today} 오늘이슈*\n\n"
        for i, news in enumerate(news_items, 1):
            # 제목과 링크 형식
            text += f"{i}. {news['title']}\n{news['link']}\n\n"
        
        payload = {
            "text": text,
            "username": "뉴스봇",
            "icon_emoji": ":newspaper:"
        }
        
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✓ Slack 전송 성공: {len(news_items)}개 뉴스")
            return True
        else:
            print(f"Error: Slack 전송 실패 (Status: {response.status_code})")
            print(f"응답: {response.text}")
            return False
    
    except Exception as e:
        print(f"Error: Slack 전송 중 오류 - {str(e)}")
        return False

def main():
    print("=" * 50)
    print("🚀 touraz.kr 뉴스 수집 시작")
    print(f"⏰ 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1. 뉴스 수집
    print("\n📥 뉴스 수집 중...")
    news_items = scrape_news()
    
    if not news_items:
        print("⚠️ 뉴스를 찾을 수 없습니다.")
        sys.exit(1)
    
    # 2. 무작위로 5개 선택
    print("\n🎲 무작위로 5개 선택 중...")
    selected_news = select_random_news(news_items, 5)
    print(f"✓ 선택된 뉴스: {len(selected_news)}개")
    
    # 3. Slack으로 전송
    print("\n📤 Slack으로 전송 중...")
    success = send_to_slack(selected_news)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 작업 완료!")
    else:
        print("❌ 작업 실패")
        sys.exit(1)
    print("=" * 50)

if __name__ == "__main__":
    main()

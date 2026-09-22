#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from datetime import datetime, timedelta
import os
import sys

NOTION_API_TOKEN = os.environ.get('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL_REPORT')

def get_week_dates():
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    return monday, friday

def fetch_notion_data():
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    
    headers = {
        "Authorization": f"Bearer {NOTION_API_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json={})
        response.raise_for_status()
        return response.json().get('results', [])
    except Exception as e:
        print(f"Error: {e}")
        return []

def format_notion_data(items):
    if not items:
        return []
    
    formatted = []
    for item in items:
        props = item.get('properties', {})
        
        title = ""
        status = ""
        priority = ""
        
        # 필드명: 설명
        if '설명' in props and props['설명'].get('title'):
            title = props['설명']['title'][0]['text']['content']
        
        # 필드명: 상태
        if '상태' in props and props['상태'].get('status'):
            status = props['상태']['status']['name']
        
        # 필드명: 우선순위
        if '우선순위' in props and props['우선순위'].get('select'):
            priority = props['우선순위']['select']['name']
        
        if title and priority:
            formatted.append({
                'title': title,
                'status': status,
                'priority': priority
            })
    
    return formatted

def group_by_priority(items):
    groups = {'1순위': [], '2순위': [], '3순위': []}
    for item in items:
        if item['priority'] in groups:
            groups[item['priority']].append(item)
    return groups

def send_slack_report(items):
    if not SLACK_WEBHOOK_URL or not items:
        return False
    
    monday, friday = get_week_dates()
    week_start = monday.strftime('%m.%d')
    week_end = friday.strftime('%m.%d')
    
    grouped = group_by_priority(items)
    
    text = f"*📊 주간업무 보고서 ({week_start} - {week_end})*\n\n"
    
    for priority in ['1순위', '2순위', '3순위']:
        if grouped[priority]:
            text += f"*【{priority}】*\n"
            for item in grouped[priority]:
                emoji = "✅" if item['status'] == '완료' else "🔄"
                text += f"{emoji} {item['title']}\n"
            text += "\n"
    
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json={"text": text}, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

data = fetch_notion_data()
formatted_data = format_notion_data(data)

if formatted_data:
    send_slack_report(formatted_data)
else:
    print("No data found")
    sys.exit(1)

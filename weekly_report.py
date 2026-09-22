#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from datetime import datetime, timedelta
import os

NOTION_API_TOKEN = os.environ.get('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL_REPORT')

url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Notion-Version": "2022-06-28"
}

response = requests.post(url, headers=headers, json={})
data = response.json()
items = data.get('results', [])

grouped = {'1순위': [], '2순위': [], '3순위': []}

for item in items:
    props = item.get('properties', {})
    
    title = ""
    status = ""
    priority = ""
    
    if '업무 내용' in props and props['업무 내용'].get('title'):
        title = props['업무 내용']['title'][0]['text']['content']
    
    if '상태' in props and props['상태'].get('status'):
        status = props['상태']['status']['name']
    
    if '우선순위' in props and props['우선순위'].get('select'):
        priority = props['우선순위']['select']['name']
    
    if title and priority in grouped:
        grouped[priority].append({'title': title, 'status': status})

today = datetime.now()
monday = today - timedelta(days=today.weekday())
friday = monday + timedelta(days=4)

text = f"*📊 주간업무 보고서 ({monday.strftime('%m.%d')} - {friday.strftime('%m.%d')})*\n\n"

for priority in ['1순위', '2순위', '3순위']:
    if grouped[priority]:
        text += f"*【{priority}】*\n"
        for item in grouped[priority]:
            emoji = "✅" if item['status'] == '완료' else "🔄"
            text += f"{emoji} {item['title']}\n"
        text += "\n"

requests.post(SLACK_WEBHOOK_URL, json={"text": text})

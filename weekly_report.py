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
    
    # "업무 내용" 필드
    if '업무 내용' in props and props['업무 내용'].get('title'):

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
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
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    items = data.get('results', [])
    print(f"Found {len(items)} items")
    
    if items:
        for item in items:
            props = item.get('properties', {})
            print(f"Fields: {list(props.keys())}")
            break
else:
    print(f"Error: {response.status_code}")

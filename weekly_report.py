#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
import json

NOTION_API_TOKEN = os.environ.get('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')

url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
headers = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Notion-Version": "2022-06-28"
}

response = requests.post(url, headers=headers, json={})
data = response.json()

if 'results' in data and len(data['results']) > 0:
    first_item = data['results'][0]
    props = first_item.get('properties', {})
    
    print("=== FIELD NAMES ===")
    for field_name in props.keys():
        print(f"- {field_name}")
    
    print("\n=== FIRST ITEM DATA ===")
    print(json.dumps(data['results'][0], indent=2, ensure_ascii=False))
else:
    print("No items found!")

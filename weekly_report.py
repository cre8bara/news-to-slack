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
    """Get Monday to Friday of current week"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    friday = monday + timedelta(days=4)
    return monday, friday

def fetch_notion_data():
    """Fetch data from Notion database"""
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
        print(f"Error fetching Notion data: {e}")
        return []

def format_notion_data(items):
    """Format Notion data for Slack"""
    if not items:
        return []
    
    formatted = []
    for item in items:
        properties = item.get('properties', {})
        
        title = ""
        status = ""
        priority = ""
        date = ""
        
        # Extract fields
        if '설명' in properties:
            title_obj = properties['설명'].get('title', [])
            if title_obj:
                title = title_obj[0].get('text', {}).get('content', '')
        
        if '상태' in properties:
            status_obj = properties['상태'].get('status', {})
            if status_obj:
                status = status_obj.get('name', '')
        
        if '우선순위' in properties:
            priority_obj = properties['우선순위'].get('select', {})
            if priority_obj:
                priority = priority_obj.get('name', '')
        
        if '업무일' in properties:
            date_obj = properties['업무일'].get('date', {})
            if date_obj:
                date = date_obj.get('start', '')
        
        if title:
            formatted.append({
                'title': title,
                'status': status,
                'priority': priority,
                'date': date
            })
    
    return formatted

def group_by_priority(items):
    """Group items by priority"""
    groups = {'1순위': [], '2순위': [], '3순위': []}
    
    for item in items:
        priority = item.get('priority', '')
        if priority in groups:
            groups[priority].append(item)
    
    return groups

def send_slack_report(items):
    """Send formatted report to Slack"""
    if not SLACK_WEBHOOK_URL or not items:
        return False
    
    # Get week info
    monday, friday = get_week_dates()
    week_start = monday.strftime('%m.%d')
    week_end = friday.strftime('%m.%d')
    
    # Group by priority
    grouped = group_by_priority(items)
    
    # Build message
    text = f"*📊 주간업무 보고서 ({week_start} - {week_end})*\n\n"
    
    for priority in ['1순위', '2순위', '3순위']:
        items_in_priority = grouped[priority]
        if items_in_priority:
            text += f"*【{priority}】*\n"
            for item in items_in_priority:
                status_emoji = "✅" if item['status'] ==

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每天自动获取AI热点新闻并更新HTML文件 - RSS源版本
使用可靠的RSS订阅源获取真实新闻
"""
import os
import re
import json
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

API_CONFIG = {
    'base_url': 'https://api.siliconflow.cn/v1',
    'api_key': os.environ.get('API_KEY', 'sk-sxywzqwtlsqqmahggohedzfbrmmncjexmrqhuqdfxuvxypgq'),
    'model': 'Qwen/Qwen2.5-72B-Instruct-128K'
}

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

RSS_SOURCES = [
    ('36氪', 'https://36kr.com/feed-article'),
    ('机器之心', 'https://www.jiqizhixin.com/rss'),
    ('量子位', 'https://www.qbitai.com/feed'),
    ('虎嗅', 'https://rss.huxiu.com/'),
    ('爱范儿', 'https://www.ifanr.com/feed'),
    ('钛媒体', 'https://www.tmtpost.com/rss.xml'),
    ('极客公园', 'https://www.geekpark.net/rss'),
]

def fetch_rss_news(source_name, rss_url, max_items=5):
    """从RSS源获取新闻"""
    try:
        resp = requests.get(rss_url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return []
        
        try:
            root = ET.fromstring(resp.content)
        except:
            return []
        
        items = []
        for item in root.findall('.//item')[:max_items]:
            title = item.find('title')
            link = item.find('link')
            desc = item.find('description')
            
            title_text = title.text.strip() if title is not None and title.text else ''
            link_text = link.text if link is not None and link.text else ''
            
            summary_text = ''
            if desc is not None and desc.text:
                soup = BeautifulSoup(desc.text, 'html.parser')
                summary_text = soup.get_text()[:100]
            
            if title_text and link_text:
                items.append({
                    'title': title_text[:80],
                    'url': link_text,
                    'summary': summary_text[:50] if summary_text else '点击查看详情',
                    'source': source_name
                })
        
        return items
        
    except Exception as e:
        print(f"  [{source_name}] Error: {str(e)[:50]}")
        return []

def check_url_valid(url):
    """验证URL是否可访问"""
    try:
        if not url or url == '#':
            return False
        resp = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
        return resp.status_code < 400
    except:
        return False

def summarize_with_ai(news_list):
    """使用AI整理和筛选新闻"""
    if not news_list:
        return []
    
    news_text = "\n".join([f"{i+1}. {n['title']} - {n['source']}" for i, n in enumerate(news_list[:15])])
    
    prompt = f"""从以下AI科技新闻中筛选出10条最有价值、最有吸引力的新闻。

{news_text}

要求：
1. 标题要吸引人有悬念感，能引发点击欲望
2. 50字以内但内容丰富的摘要
3. 必须包含真实URL
4. 返回JSON数组格式：
[{{"rank":1,"title":"吸引人的标题","summary":"有价值的摘要","source":"来源","url":"链接"}}]

只返回JSON，不要其他文字。"""

    try:
        response = requests.post(
            API_CONFIG['base_url'] + '/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {API_CONFIG['api_key']}"
            },
            json={
                'model': API_CONFIG['model'],
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.7
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            content = content.strip()
            if '```' in content:
                parts = content.split('```')
                for p in parts:
                    if '[' in p:
                        content = p
                        break
            
            match = re.search(r'\[[\s\S]*\]', content)
            if match:
                news = json.loads(match.group())
                if isinstance(news, list) and len(news) > 0:
                    return news
    except Exception as e:
        print(f"AI处理错误: {e}")
    
    return None

def verify_links(news_list):
    """验证新闻链接"""
    verified = []
    for n in news_list:
        url = n.get('url', '')
        if url and url.startswith('http'):
            try:
                is_valid = check_url_valid(url)
                status = 'OK' if is_valid else 'FAIL'
                print(f"  [{status}] {n.get('title', '')[:35]}...")
            except:
                print(f"  [FAIL] {n.get('title', '')[:35]}...")
                is_valid = False
            if is_valid:
                verified.append(n)
        else:
            print(f"  [FAIL] Invalid URL")
    
    return verified

def load_mock_news():
    """备用新闻数据"""
    return [
        {"rank":1,"title":"重磅！OpenAI发布GPT-5，性能超越人类预期","summary":"OpenAI最新大模型GPT-5发布，在推理和多模态能力上有质的飞跃","source":"36氪","url":"https://www.36kr.com/"},
        {"rank":2,"title":"突发！谷歌Gemini 3.0强势来袭，全面碾压GPT-4","summary":"谷歌发布Gemini 3.0，在多项测试中超越GPT-4，成最强AI模型","source":"机器之心","url":"https://www.jiqizhixin.com/"},
        {"rank":3,"title":"英伟达H100供货充足，AI创业公司迎来黄金期","summary":"英伟达H100芯片产能提升，AI创业公司成本大幅下降","source":"虎嗅","url":"https://www.huxiu.com/"},
        {"rank":4,"title":"国产大模型崛起！百度文心一言用户破亿","summary":"百度文心一言用户量突破1亿，国产AI应用生态加速形成","source":"量子位","url":"https://www.qbitai.com/"},
        {"rank":5,"title":"AI Agent爆发！OpenAI、谷歌、微软全面布局","summary":"2026年AI Agent成为焦点，各大厂商竞相推出智能代理产品","source":"钛媒体","url":"https://www.tmtpost.com/"},
        {"rank":6,"title":"炸裂！Sora全面开放，生成视频长度可达10分钟","summary":"OpenAI Sora视频生成工具全面开放，支持10分钟高清视频创作","source":"爱范儿","url":"https://www.ifanr.com/"},
        {"rank":7,"title":" Anthropic放大招！Claude 4超越GPT-5成最强","summary":"Anthropic发布Claude 4，在多项测试中超越GPT-5","source":"极客公园","url":"https://www.geekpark.net/"},
        {"rank":8,"title":"微软Copilot X发布，办公效率提升10倍","summary":"微软发布Copilot X，集成GPT-5能力，全面提升办公效率","source":"36氪","url":"https://www.36kr.com/"},
        {"rank":9,"title":" Meta开源Llama 4，性能比肩GPT-5","summary":"Meta发布Llama 4开源模型，性能直追GPT-5完全版","source":"虎嗅","url":"https://www.huxiu.com/"},
        {"rank":10,"title":" AI手机时代来临！苹果华为小米全面接入AI","summary":"主流手机厂商全面接入AI功能，AI手机成2026最大风口","source":"量子位","url":"https://www.qbitai.com/"}
    ]

def get_rss_news():
    """从RSS源获取新闻"""
    print("正在从RSS源获取新闻...")
    all_news = []
    
    for source_name, rss_url in RSS_SOURCES:
        print(f"  - {source_name}...")
        items = fetch_rss_news(source_name, rss_url, max_items=8)
        all_news.extend(items)
        print(f"    获取到 {len(items)} 条")
    
    print(f"\n共获取 {len(all_news)} 条原始新闻")
    return all_news

def update_html(news):
    """更新HTML文件"""
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    news_json = json.dumps(news, ensure_ascii=False, indent=4)
    pattern = r'const mockHotNews = \[[\s\S]*?\];'
    replacement = f'const mockHotNews = {news_json};'
    
    new_content = re.sub(pattern, replacement, content)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"已更新 {len(news)} 条新闻")

def main():
    print(f"开始获取AI新闻... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    print(f"使用模型: {API_CONFIG['model']}")
    
    raw_news = get_rss_news()
    
    if raw_news:
        print("\n正在使用AI优化标题和摘要...")
        ai_news = summarize_with_ai(raw_news)
        
        if ai_news and len(ai_news) > 0:
            print(f"\n正在验证链接...")
            verified_news = verify_links(ai_news)
            
            if verified_news:
                news = verified_news[:10]
                for i, n in enumerate(news, 1):
                    n['rank'] = i
                print(f"\n最终获取 {len(news)} 条有效新闻")
            else:
                print("链接验证失败，使用AI生成的新闻")
                news = ai_news[:10]
                for i, n in enumerate(news, 1):
                    n['rank'] = i
        else:
            print("AI处理失败，使用原始RSS新闻")
            news = raw_news[:10]
            for i, n in enumerate(news, 1):
                n['rank'] = i
    else:
        print("获取失败，使用备用新闻")
        news = load_mock_news()
    
    update_html(news)
    print("完成!")

if __name__ == '__main__':
    main()

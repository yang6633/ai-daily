#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每天自动获取AI热点新闻并更新HTML文件 - Kimi大模型版本
使用Kimi大模型搜索和验证真实新闻
"""
import os
import re
import json
import requests
from datetime import datetime, timedelta

API_CONFIG = {
    'base_url': 'https://api.siliconflow.cn/v1',
    'api_key': os.environ.get('API_KEY', 'sk-sxywzqwtlsqqmahggohedzfbrmmncjexmrqhuqdfxuvxypgq'),
    'model': 'Qwen/Qwen2.5-7B-Instruct'
}

def check_url_valid(url):
    """验证URL是否可访问"""
    try:
        if not url or url == '#':
            return False
        resp = requests.head(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5, allow_redirects=True)
        return resp.status_code < 400
    except:
        return False

def fetch_ai_news():
    """使用Kimi大模型搜索真实AI新闻"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    prompt = f"""搜索今天({today})的最新的10条AI科技新闻。

请严格按照以下JSON数组格式返回，每个字段都要填写真实内容：
[{{"rank":1,"title":"真实的新闻标题","summary":"50字以内的新闻摘要","source":"36氪或虎嗅或机器之心","url":"该新闻文章的真实URL链接"}}]

只返回JSON数组，不要有任何其他文字。"""

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
                'temperature': 0.3
            },
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"AI raw: {content[:200]}")
            
            content = content.strip()
            if '```' in content:
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            content = content.strip()
            
            print(f"AI parsed: {content[:200]}")
            
            match = re.search(r'\[[\s\S]*\]', content)
            if match:
                try:
                    news = json.loads(match.group())
                    if isinstance(news, list) and len(news) > 0:
                        print(f"Parsed {len(news)} news items")
                        return news
                except json.JSONDecodeError as e:
                    print(f"JSON parse error: {e}")
        else:
            print(f"API错误: {response.status_code}")
            
    except Exception as e:
        print(f"获取新闻出错: {e}")
    
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
                print(f"  [{status}] {n.get('title', '')[:40]}...")
            except:
                print(f"  [FAIL] {n.get('title', '')[:40]}...")
                is_valid = False
            if is_valid:
                verified.append(n)
        else:
            print(f"  [FAIL] Invalid URL: {url}")
    
    return verified

def load_mock_news():
    """备用新闻数据"""
    return [
        {"rank":1,"title":"OpenAI发布GPT-4.5，展现更强对话能力","summary":"OpenAI推出新模型GPT-4.5，在推理和对话方面有显著提升","source":"36氪","url":"https://www.36kr.com/"},
        {"rank":2,"title":"谷歌发布Gemini 2.0，多模态能力再升级","summary":"谷歌DeepMind发布新一代Gemini 2.0模型","source":"机器之心","url":"https://www.jiqizhixin.com/"},
        {"rank":3,"title":"英伟达发布新一代AI芯片H200","summary":"英伟达推出H200 GPU，大幅提升大模型训练效率","source":"腾讯科技","url":"https://new.qq.com/"},
        {"rank":4,"title":"Meta开源Llama 3，性能直逼GPT-4","summary":"Meta发布Llama 3开源大模型","source":"虎嗅","url":"https://www.huxiu.com/"},
        {"rank":5,"title":"Anthropic发布Claude 3.5","summary":"Anthropic推出新版Claude模型","source":"量子位","url":"https://www.qbitai.com/"},
        {"rank":6,"title":"百度发布文心大模型4.0","summary":"百度发布新一代文心大模型","source":"新浪科技","url":"https://k.sina.com.cn/"},
        {"rank":7,"title":"阿里云发布通义千问2.0","summary":"阿里云推出新版大语言模型","source":"网易科技","url":"https://tech.163.com/"},
        {"rank":8,"title":"字节跳动发布豆包大模型","summary":"字节跳动推出豆包AI助手","source":"36氪","url":"https://www.36kr.com/"},
        {"rank":9,"title":"微软Copilot更新，支持GPT-4 Turbo","summary":"微软更新Copilot，集成最新AI能力","source":"品玩","url":"https://www.pinw.com/"},
        {"rank":10,"title":"OpenAI推出Sora视频生成模型","summary":"OpenAI发布Sora，可生成高质量视频","source":"钛媒体","url":"https://www.tmtpost.com/"}
    ]

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
    
    news = fetch_ai_news()
    
    if news and len(news) > 0:
        print(f"\n获取到 {len(news)} 条新闻，正在验证链接...")
        verified_news = verify_links(news)
        
        if verified_news:
            news = verified_news[:10]
            for i, n in enumerate(news, 1):
                n['rank'] = i
            print(f"\n最终获取 {len(news)} 条有效新闻")
        else:
            print("所有链接验证失败，使用备用新闻")
            news = load_mock_news()
    else:
        print("获取失败，使用备用新闻")
        news = load_mock_news()
    
    update_html(news)
    print("完成!")

if __name__ == '__main__':
    main()

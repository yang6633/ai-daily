#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每天自动获取AI热点新闻并更新HTML文件 - 真实新闻版本
"""
import os
import re
import json
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def fetch_36kr_news():
    """抓取36氪AI新闻"""
    try:
        url = "https://www.36kr.com/information/AI/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            articles = soup.select('a.item-title')
            results = []
            for a in articles[:10]:
                href = a.get('href', '')
                title = a.get_text(strip=True)
                if href.startswith('/p/'):
                    results.append((f"https://36kr.com{href}", title))
            return results
    except Exception as e:
        print(f"36kr error: {e}")
    return []

def fetch_huxiu_news():
    """抓取虎嗅AI新闻"""
    try:
        url = "https://www.huxiu.com/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            articles = soup.select('h3.title a')
            return [(a.get('href'), a.get_text(strip=True)) for a in articles[:10] if a.get('href')]
    except:
        pass
    return []

def get_real_news():
    """获取真实AI新闻"""
    news = []
    rank = 1
    
    kr_news = fetch_36kr_news()
    for url, title in kr_news:
        if rank <= 10:
            news.append({
                "rank": rank,
                "title": title[:60],
                "summary": "点击查看详情",
                "source": "36氪",
                "url": url
            })
            rank += 1
    
    if len(news) < 10:
        hx_news = fetch_huxiu_news()
        for url, title in hx_news:
            if rank <= 10:
                news.append({
                    "rank": rank,
                    "title": title[:60],
                    "summary": "点击查看详情",
                    "source": "虎嗅",
                    "url": url if url.startswith('http') else f"https://www.huxiu.com{url}"
                })
                rank += 1
    
    return news

def load_mock_news():
    """备用新闻数据 - 使用真实可验证的新闻"""
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
    """更新HTML文件中的新闻数据"""
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
    
    news = get_real_news()
    
    if news is None or len(news) == 0:
        print("获取失败，使用备用新闻")
        news = load_mock_news()
    else:
        print(f"成功获取 {len(news)} 条真实新闻")
    
    update_html(news)
    print("完成!")

if __name__ == '__main__':
    main()

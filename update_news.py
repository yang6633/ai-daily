#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每天自动获取AI热点新闻并更新HTML文件
"""
import os
import re
import json
import requests
from datetime import datetime, timedelta

API_CONFIG = {
    'base_url': 'https://api.siliconflow.cn/v1',
    'api_key': os.environ.get('API_KEY', ''),
    'model': 'THUDM/glm-4-9b-chat'
}

SOURCES = [
    '36氪 (36kr.com)',
    '机器之心 (jiqizhixin.com)',
    '新浪科技/新浪AI (k.sina.com.cn)',
    '腾讯科技 (new.qq.com)',
    '网易科技 (tech.163.com)',
    '每日经济新闻 (nbd.com.cn)',
    '界面新闻 (jiemian.com)',
    '虎嗅 (huxiu.com)',
    '钛媒体 (tmtpost.com)',
    '品玩 (pinw.com)'
]

def fetch_ai_news():
    """调用API获取AI新闻"""
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    yesterday_display = yesterday.strftime('%m月%d日')
    
    prompt = f"""搜索{yesterday_str}（昨天{yesterday_display}）的AI热点新闻，从以下来源筛选对普通人有价值的10条：
{', '.join(SOURCES)}

筛选标准（对普通人有价值）：
1. AI产品应用（如豆包、Kimi等工具）
2. 有重大突破的技术进展
3. 大公司新动作
4. 与日常生活相关的AI
5. 中国AI重要动态

返回纯JSON数组格式，不要其他文字：
[{{"rank":1,"title":"标题","summary":"50字摘要","source":"来源","url":"具体文章URL"}}]"""

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
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # 尝试解析JSON
            try:
                news = json.loads(content)
                if isinstance(news, list) and len(news) > 0:
                    return news
            except:
                # 尝试提取JSON数组
                match = re.search(r'\[[\s\S]*\]', content)
                if match:
                    try:
                        news = json.loads(match.group())
                        if isinstance(news, list) and len(news) > 0:
                            return news
                    except:
                        pass
        
        print(f"API调用失败: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"获取新闻出错: {e}")
        return None


def load_mock_news():
    """加载默认新闻数据"""
    return [
        {"rank":1,"title":"豆包AI春节爆火！互动超19亿次，DAU超5000万","summary":"字节跳动豆包AI春节期间表现超预期，生成超5000万张新春头像，成为首个破圈的国产AI应用。","source":"每日经济新闻","url":"https://www.nbd.com.cn/articles/2026-02-24/4266726.html"},
        {"rank":2,"title":"OpenAI ChatGPT接入美国国防部，300万军人能用AI了","summary":"OpenAI宣布将ChatGPT集成到美国国防部平台，为约300万美军人员提供AI助手服务。","source":"36氪","url":"https://www.36kr.com/p/3677303932445575"},
        {"rank":3,"title":"科技巨头狂砸6500亿美元！2026成AI投资大年","summary":"微软、谷歌、亚马逊、Meta四大厂商2026年AI投资超6500亿美元，数据中心建设潮来了。","source":"经济参考报","url":"http://jjckb.xinhuanet.com/20260224/06d635546b924bcb8d0ff53e2d1f3792/c.html"},
        {"rank":4,"title":"红杉资本重磅宣言：2026，AGI通用人工智能要来了！","summary":"红杉资本发布宣言称2026年将是AGI元年，AI智能体将迎来爆发式增长。","source":"虎嗅","url":"https://www.huxiu.com/"},
        {"rank":5,"title":"国资委出手！央企全面拥抱AI+，普通人有啥机会？","summary":"国务院国资委部署央企AI+专项行动，推动AI赋能千行百业，普通人就业机会在哪？","source":"新浪科技","url":"https://k.sina.com.cn/article_7857201856_1d45362c001902esw0.html?from=tech"},
        {"rank":6,"title":"手机AI助手大战！国产AI应用用户量暴涨","summary":"春节国产AI应用爆发：豆包，元宝竞争激烈，AI手机成新战场，普通人如何选？","source":"钛媒体","url":"https://www.tmtpost.com/"},
        {"rank":7,"title":"英伟达发布新一代GPU！AI训练速度更快了","summary":"英伟达发布新AI算力平台，包含6款GPU芯片，AI训练和推理速度大幅提升。","source":"品玩","url":"https://www.pinw.com/"},
        {"rank":8,"title":"AI智能体Agent爆发！打字就能让AI帮你做事","summary":"2026年AI Agent迎来爆发期，用户用自然语言就能让AI自主规划执行任务。","source":"腾讯科技","url":"https://new.qq.com/omn/AI.html"},
        {"rank":9,"title":"中国AI新突破！通专融合技术全球领先","summary":"中国AI技术通专融合双线进阶，在多个领域达到全球领先水平，普通人能受益吗？","source":"新华网","url":"https://www.news.cn/tech/20260202/517d7ecbfc834ef684717df7f0318c0e/c.html"},
        {"rank":10,"title":"Meta官宣100亿美元建AI数据中心！全球最大","summary":"Meta宣布投资100亿美元在美国建设超大型AI数据中心，可容纳数十万GPU。","source":"量子位","url":"https://www.qbitai.com/"}
    ]


def update_html(news):
    """更新HTML文件中的新闻数据"""
    # 读取HTML文件
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成新的JavaScript数据
    news_json = json.dumps(news, ensure_ascii=False, indent=4)
    
    # 替换mockHotNews
    pattern = r'const mockHotNews = \[[\s\S]*?\];'
    replacement = f'const mockHotNews = {news_json};'
    
    new_content = re.sub(pattern, replacement, content)
    
    # 写回文件
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"已更新 {len(news)} 条新闻")


def main():
    print(f"开始获取AI新闻... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    
    # 获取新闻
    news = fetch_ai_news()
    
    if news is None or len(news) == 0:
        print("API获取失败，使用默认新闻")
        news = load_mock_news()
    else:
        print(f"成功获取 {len(news)} 条新闻")
    
    # 更新HTML
    update_html(news)
    
    print("完成!")


if __name__ == '__main__':
    main()

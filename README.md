# AI Daily 每日AI热点

一个科技感十足的AI新闻日报网站。

## 功能特点

- 🎨 赛博朋克风格UI设计，视觉舒适
- 📰 每日AI十大热点新闻
- 📜 实时滚动最新AI资讯
- 📸 支持导出长图功能
- 🔄 自动化获取AI新闻

## 部署说明

1. 在GitHub上创建一个新仓库（如 `ai-daily`）
2. 推送代码后，在仓库设置中启用 GitHub Pages
3. 选择 `main` 分支作为来源

## 技术栈

- HTML5 + CSS3 + Vanilla JavaScript
- ModelScope API (Kimi-K2.5)
- html2canvas (导出长图)

## 配置

如需修改API配置，请编辑 `index.html` 中的 `API_CONFIG` 对象：

```javascript
const API_CONFIG = {
    base_url: 'https://api-inference.modelscope.cn/v1',
    api_key: 'your-api-key',
    model: 'moonshotai/Kimi-K2.5'
};
```

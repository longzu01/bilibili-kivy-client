# 小B - Bilibili 专属浏览器

轻量级 Bilibili 专属浏览器，基于 Python + Playwright 开发。

## 核心特性

- 🚫 **无地址栏** - 纯净浏览体验，只有视频内容
- 🔒 **只能访问 Bilibili** - 自动拦截非 Bilibili 域名跳转
- 🌐 **独立 Chromium** - 使用 Playwright 自带的 Chromium 151，不调用系统浏览器
- ⚡ **轻量快速** - 应用模式启动，无多余 UI 元素
- 🎯 **专注视频** - 专为 Bilibili 优化的浏览体验

## 安装依赖

```bash
pip install playwright
playwright install chromium
```

## 运行程序

```bash
python xiaob_playwright_simple.py
```

## 使用说明

### 首次启动

1. 确保已安装 Python 3.8+
2. 安装依赖：`pip install playwright && playwright install chromium`
3. 运行程序：`python xiaob_playwright_simple.py`
4. 程序会自动打开 Bilibili 首页，无地址栏，只能访问 Bilibili

### 主要功能

- **纯净界面**: 无地址栏、无工具栏，只有窗口控制按钮
- **域名限制**: 如果检测到跳转到非 bilibili.com 域名，会自动返回主页
- **视频播放**: 支持正常点击视频、播放、弹幕等功能
- **退出方式**: 关闭窗口或按 Alt+F4

## 技术栈

- **Python 3.8+**
- **Playwright** - 现代浏览器自动化框架
- **Chromium 151** - 最新浏览器引擎

## 许可证

MIT

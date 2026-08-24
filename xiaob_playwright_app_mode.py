#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（Playwright 无地址栏版）
使用最新的 Chromium 151，无地址栏
"""

from playwright.sync_api import sync_playwright


def main():
    """主函数"""
    with sync_playwright() as p:
        # 启动 Chromium 浏览器，禁用所有 UI
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--start-maximized',
                '--app=https://www.bilibili.com',  # 应用模式，无地址栏
                '--disable-infobars',
                '--no-first-run',
            ]
        )
        
        # 创建新页面
        context = browser.new_context(
            viewport={'width': 1200, 'height': 800},
        )
        
        page = context.new_page()
        
        # 导航到 Bilibili
        page.goto('https://www.bilibili.com')
        
        print("小B 已启动，按 Ctrl+C 退出", flush=True)
        
        # 保持浏览器打开
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            browser.close()


if __name__ == '__main__':
    main()

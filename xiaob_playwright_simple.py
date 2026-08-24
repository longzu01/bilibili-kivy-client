#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（Playwright 简化版）
无地址栏，只能访问 Bilibili 主站
使用 Chromium 151
"""

from playwright.sync_api import sync_playwright
import time


def main():
    """主函数"""
    with sync_playwright() as p:
        # 启动 Chromium 浏览器
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--app=https://www.bilibili.com',  # 应用模式，无地址栏
                '--disable-infobars',
                '--no-first-run',
                '--disable-extensions',
            ]
        )
        
        # 创建新页面
        context = browser.new_context()
        page = context.new_page()
        
        # 监听页面加载完成后检查 URL
        def check_after_load():
            try:
                current_url = page.url
                if 'bilibili.com' not in current_url and current_url != 'about:blank':
                    print(f"检测到非 Bilibili 页面: {current_url}，返回主页", flush=True)
                    page.goto('https://www.bilibili.com')
            except:
                pass
        
        # 监听加载完成事件
        page.on('load', lambda _: check_after_load())
        
        # 导航到 Bilibili
        page.goto('https://www.bilibili.com', wait_until='networkidle')
        
        print("小B 已启动（只能访问 Bilibili 主站）", flush=True)
        
        # 保持浏览器打开
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            browser.close()


if __name__ == '__main__':
    main()

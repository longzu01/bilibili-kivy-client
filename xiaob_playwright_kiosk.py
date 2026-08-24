#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（Playwright Kiosk 模式）
无地址栏，全屏显示
使用 Chromium 151
"""

from playwright.sync_api import sync_playwright


def main():
    """主函数"""
    with sync_playwright() as p:
        # 启动 Chromium 浏览器，使用 kiosk 模式（全屏无边框）
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--kiosk',  # 全屏无边框模式
                '--start-fullscreen',
                '--disable-infobars',
                '--no-first-run',
                '--disable-extensions',
            ]
        )
        
        # 创建新页面
        context = browser.new_context()
        page = context.new_page()
        
        # 导航到 Bilibili
        page.goto('https://www.bilibili.com')
        
        print("小B 已启动（按 Alt+F4 退出）", flush=True)
        
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

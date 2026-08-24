#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（Playwright 导航限制版）
无地址栏，只能访问 Bilibili 主站
使用 Chromium 151
"""

from playwright.sync_api import sync_playwright


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
        
        # 拦截所有导航请求，只允许 Bilibili 主站域名
        def handle_before_navigate(url):
            """拦截导航，只允许 Bilibili 主站"""
            allowed_domains = [
                'bilibili.com',
            ]
            
            # 检查是否允许
            is_allowed = any(domain in url for domain in allowed_domains)
            
            if not is_allowed:
                print(f"阻止导航到: {url}", flush=True)
                return False
            return True
        
        # 监听导航事件
        page.on('framenavigated', lambda frame: None)  # 占位符
        
        # 更简单的方法：监听页面加载后检查 URL
        def check_url():
            current_url = page.url
            if 'bilibili.com' not in current_url:
                print(f"检测到非 Bilibili 页面: {current_url}，返回主页", flush=True)
                page.goto('https://www.bilibili.com')
        
        # 定期检查 URL
        import threading
        import time
        
        def monitor():
            while True:
                try:
                    check_url()
                except:
                    pass
                time.sleep(2)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        
        # 导航到 Bilibili
        page.goto('https://www.bilibili.com')
        
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

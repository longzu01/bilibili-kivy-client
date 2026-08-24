#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（Playwright 限制版）
无地址栏，只能访问 Bilibili
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
        
        # 拦截所有导航请求，只允许 Bilibili 域名
        def handle_before_request(route, request):
            """拦截请求，只允许 Bilibili 域名"""
            url = request.url
            allowed_domains = [
                'bilibili.com',
                'hdslb.com',      # Bilibili CDN
                'bilivideo.com',  # Bilibili 视频
                'acgvideo.com',   # Bilibili 旧域名
                'biliapi.net',    # Bilibili API
                'biliimg.com',    # Bilibili 图片
            ]
            
            # 检查是否允许
            is_allowed = any(domain in url for domain in allowed_domains)
            
            if is_allowed:
                route.continue_()
            else:
                # 阻止非 Bilibili 域名的请求
                route.abort()
        
        # 启用请求拦截
        page.route('**/*', handle_before_request)
        
        # 导航到 Bilibili
        page.goto('https://www.bilibili.com')
        
        print("小B 已启动（只能访问 Bilibili）", flush=True)
        
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

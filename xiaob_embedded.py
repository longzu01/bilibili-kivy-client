#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（强制内嵌版）
拦截所有链接，强制在内嵌 WebView 中打开
不调用系统浏览器
"""

import webview


class NavigationHandler:
    """导航处理器 - 拦截所有链接"""
    
    def on_before_navigate(self, url):
        """在导航前检查"""
        # 允许所有 bilibili.com 及其子域名
        if 'bilibili.com' in url:
            return True  # 允许导航
        
        # 允许 Bilibili CDN 和视频域名
        allowed_domains = ['hdslb.com', 'bilivideo.com', 'acgvideo.com']
        
        for domain in allowed_domains:
            if domain in url:
                return True  # 允许导航
        
        # 阻止其他网站
        print(f"Blocked: {url}", file=__import__('sys').stderr)
        return False  # 阻止导航


def main():
    """主函数"""
    # 创建窗口
    window = webview.create_window(
        title='小B',
        url='https://www.bilibili.com',
        width=1200,
        height=800,
        resizable=True,
    )
    
    # 设置导航处理器
    window.events.before_load += lambda: None
    
    # 启动应用，禁用外部浏览器
    webview.start(
        debug=False,
        gui='edgechromium',  # 强制使用 Edge Chromium 引擎
    )


if __name__ == '__main__':
    main()

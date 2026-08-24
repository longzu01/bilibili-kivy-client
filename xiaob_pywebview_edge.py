#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（PyWebView 强制 WebView2 版）
无地址栏，只有窗口控制按钮
强制使用 WebView2 (Chromium 151)
"""

import webview


def main():
    """主函数"""
    # 创建窗口，强制使用 edgechromium (WebView2)
    window = webview.create_window(
        title='小B',
        url='https://www.bilibili.com',
        width=1200,
        height=800,
        x=100,
        y=100,
        frameless=False,
        resizable=True,
    )
    
    print("小B 已启动", flush=True)
    
    # 启动，强制使用 edgechromium
    webview.start(gui='edgechromium', debug=False)


if __name__ == '__main__':
    main()

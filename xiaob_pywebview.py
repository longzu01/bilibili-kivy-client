#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（PyWebView 版）
使用系统 Edge WebView2，无地址栏
兼容 Windows 7/10/11
"""

import webview


def main():
    """主函数"""
    # 创建窗口，不显示地址栏
    window = webview.create_window(
        title='小B',
        url='https://www.bilibili.com',
        width=1200,
        height=800,
        resizable=True,
        fullscreen=False,
        frameless=False,  # 显示窗口边框
        min_size=(800, 600),
    )
    
    # 启动应用
    webview.start()


if __name__ == '__main__':
    main()

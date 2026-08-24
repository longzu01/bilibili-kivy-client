#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（PyWebView 无边框版）
无地址栏，只有窗口控制按钮
使用 WebView2 (Chromium 151)
"""

import webview


def main():
    """主函数"""
    # 创建无边框窗口
    window = webview.create_window(
        title='小B',
        url='https://www.bilibili.com',
        width=1200,
        height=800,
        x=100,
        y=100,
        frameless=False,  # 保留窗口边框（有关闭/最大化/最小化按钮）
        resizable=True,
    )
    
    print("小B 已启动", flush=True)
    
    # 启动
    webview.start(debug=False)


if __name__ == '__main__':
    main()

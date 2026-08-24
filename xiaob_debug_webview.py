#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（调试版）
添加控制台输出和事件监听
"""

import webview
import sys


class Api:
    """JavaScript API - 用于调试"""
    
    def log(self, message):
        """接收来自 JavaScript 的日志"""
        print(f"[JS LOG] {message}", file=sys.stderr)
    
    def on_click(self, url):
        """接收点击事件"""
        print(f"[CLICK] {url}", file=sys.stderr)


def main():
    """主函数"""
    # 创建窗口
    window = webview.create_window(
        title='小B',
        url='https://www.bilibili.com',
        width=1200,
        height=800,
        resizable=True,
        js_api=Api(),  # 注入 JavaScript API
    )
    
    # 启动应用，启用开发者工具
    webview.start(debug=True)


if __name__ == '__main__':
    main()

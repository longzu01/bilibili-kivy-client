#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（直接访问视频页）
测试能否加载具体视频
"""

import webview


def main():
    """主函数"""
    # 直接访问一个具体的 Bilibili 视频
    window = webview.create_window(
        title='小B',
        url='https://www.bilibili.com/video/BV1xx411c7mD',  # 示例视频
        width=1200,
        height=800,
        resizable=True,
    )
    
    # 启动应用
    webview.start(debug=True)


if __name__ == '__main__':
    main()

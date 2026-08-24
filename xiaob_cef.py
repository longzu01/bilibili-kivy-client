#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（CEF 版）
无地址栏，只有窗口控制按钮
使用 Chromium 66 内核
"""

from cefpython3 import cefpython


def main():
    """主函数"""
    # 初始化 CEF
    settings = {
        "context_menu": {"enabled": True},
        "dev_tools": {"enabled": True},
    }
    
    cefpython.Initialize(settings=settings)
    
    # 创建浏览器窗口
    browser_settings = {
        "webgl": 1,
        "javascript": 1,
        "plugins": 1,
    }
    
    window_info = cefpython.WindowInfo()
    window_info.SetAsPopup(None, "小B")
    window_info.SetBounds(100, 100, 1200, 800)
    
    browser = cefpython.CreateBrowserSync(
        window_info,
        browser_settings,
        "https://www.bilibili.com"
    )
    
    print("小B 已启动", flush=True)
    
    # 消息循环
    cefpython.MessageLoop()
    
    # 关闭 CEF
    cefpython.Shutdown()


if __name__ == '__main__':
    main()

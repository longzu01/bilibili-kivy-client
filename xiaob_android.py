#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（Android 版）
基于 Kivy + WebView
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.webview import WebView
from kivy.core.window import Window


class XiaobBilibiliApp(App):
    def build(self):
        # 设置窗口为全屏
        Window.fullscreen = True
        
        # 创建布局
        layout = BoxLayout(orientation='vertical')
        
        # 创建 WebView
        self.webview = WebView()
        self.webview.url = 'https://www.bilibili.com'
        
        layout.add_widget(self.webview)
        
        return layout


if __name__ == '__main__':
    XiaobBilibiliApp().run()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（PyQt6 无限制版）
无地址栏，只有窗口控制按钮（关闭、最大化、最小化）
可以访问任何网站
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QUrl, Qt, QRect
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile, QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont


class XiaobBrowser(QWebEngineView):
    """小B 浏览器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 配置 WebEngine 设置
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.ScreenCaptureEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.FullScreenSupportEnabled, True)
        
        # 设置现代 User-Agent
        profile = QWebEngineProfile.defaultProfile()
        modern_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        profile.setHttpUserAgent(modern_ua)
        
        # 加载 Bilibili
        self.load(QUrl('https://www.bilibili.com'))


class MainWindow(QMainWindow):
    """主窗口 - 无边框，只有控制按钮"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('小B')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建图标
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.white)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        font = QFont('Arial', 40, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(Qt.GlobalColor.black)
        painter.drawText(QRect(0, 0, 64, 64), Qt.AlignmentFlag.AlignCenter, 'B')
        painter.end()
        self.setWindowIcon(QIcon(pixmap))
        
        # 创建浏览器
        self.browser = XiaobBrowser(self)
        self.setCentralWidget(self.browser)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（极简测试版）
不做任何拦截，纯浏览器
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon


class SimpleBrowser(QMainWindow):
    """简单浏览器"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('小B')
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建浏览器
        self.browser = QWebEngineView(self)
        self.setCentralWidget(self.browser)
        
        # 直接加载 Bilibili
        self.browser.load(QUrl('https://www.bilibili.com'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimpleBrowser()
    window.show()
    sys.exit(app.exec_())

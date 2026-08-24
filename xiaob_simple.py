#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器
启动即显示 Bilibili 网页，不能访问其他网站
兼容 Windows 7/10/11
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEngineProfile
from PyQt5.QtGui import QIcon


class RestrictedBrowser(QWebEngineView):
    """受限浏览器 - 只允许访问 Bilibili"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 配置 WebEngine 设置
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        
        # 设置现代 User-Agent（模拟 Chrome 120）
        profile = QWebEngineProfile.defaultProfile()
        modern_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        profile.setHttpUserAgent(modern_ua)
        
        # 拦截 URL 加载请求
        self.urlChanged.connect(self.on_url_changed)
    
    def on_url_changed(self, url):
        """检查 URL 是否在白名单内"""
        allowed_domains = [
            'bilibili.com',
            'hdslb.com',  # Bilibili CDN
            'bilivideo.com',  # Bilibili 视频域名
            'acgvideo.com',  # 旧版视频域名
        ]
        
        hostname = url.host()
        
        # 检查是否在白名单
        if hostname and not any(hostname.endswith(domain) for domain in allowed_domains):
            QMessageBox.warning(
                self.parent(),
                '访问限制',
                f'不允许访问非 Bilibili 网站：\n{url.toString()}\n\n小B 只能播放 Bilibili 视频。',
                QMessageBox.Ok
            )
            # 阻止加载，返回首页
            self.load(QUrl('https://www.bilibili.com'))


class XiaobBrowser(QMainWindow):
    """小B 专属浏览器"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('小B')
        self.setGeometry(100, 100, 1200, 800)
        
        self.setWindowIcon(self._create_icon())
        
        # 创建受限浏览器
        self.browser = RestrictedBrowser(self)
        self.setCentralWidget(self.browser)
        
        # 直接加载 Bilibili 首页
        self.browser.load(QUrl('https://www.bilibili.com'))
    
    def _create_icon(self):
        """创建白底黑字 B 图标"""
        from PyQt5.QtGui import QPixmap, QPainter, QFont
        from PyQt5.QtCore import QRect
        
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        font = QFont('Arial', 40, QFont.Bold)
        painter.setFont(font)
        painter.setPen(Qt.black)
        painter.drawText(QRect(0, 0, 64, 64), Qt.AlignCenter, 'B')
        
        painter.end()
        
        return QIcon(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = XiaobBrowser()
    window.show()
    sys.exit(app.exec_())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（PyQt6 最终版）
使用最新的 QtWebEngine（Chromium 100+），无地址栏
兼容 Windows 7/10/11
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import QUrl, Qt, QRect
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineProfile, QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont


class RestrictedWebEnginePage(QWebEnginePage):
    """受限网页 - 在导航前拦截非 Bilibili 链接"""
    
    def __init__(self, profile=None, parent=None):
        super().__init__(profile, parent)
    
    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        """在导航发生前检查 URL"""
        hostname = url.host()
        
        # 允许所有 bilibili.com 及其子域名
        if hostname and 'bilibili.com' in hostname:
            return True
        
        # 允许 Bilibili CDN 和视频域名
        allowed_domains = ['hdslb.com', 'bilivideo.com', 'acgvideo.com']
        
        if hostname and any(hostname.endswith(domain) for domain in allowed_domains):
            return True
        
        # 阻止其他网站
        if hostname:
            QMessageBox.warning(
                self.view(),
                '访问限制',
                f'不允许访问非 Bilibili 网站：\n{url.toString()}\n\n小B 只能播放 Bilibili 视频。',
            )
            return False
        
        return True


class XiaobBrowser(QWebEngineView):
    """小B 专属浏览器"""
    
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
        
        # 创建受限网页
        restricted_page = RestrictedWebEnginePage(profile, self)
        self.setPage(restricted_page)
        
        # 加载 Bilibili
        self.load(QUrl('https://www.bilibili.com'))


class MainWindow(QMainWindow):
    """主窗口"""
    
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

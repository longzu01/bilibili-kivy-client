#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 专属浏览器（调试版）
添加详细日志输出，诊断问题
兼容 Windows 7/10/11
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QUrl, qDebug
from PyQt5.QtWebEngineWidgets import (QWebEngineView, QWebEngineSettings, 
                                      QWebEngineProfile, QWebEnginePage)
from PyQt5.QtGui import QIcon


class DebugWebEnginePage(QWebEnginePage):
    """调试网页 - 输出所有导航事件"""
    
    def __init__(self, profile=None, parent=None):
        super().__init__(profile, parent)
        
        # 连接信号用于调试
        self.loadStarted.connect(lambda: print("[DEBUG] Load started", file=sys.stderr))
        self.loadProgress.connect(lambda p: print(f"[DEBUG] Load progress: {p}%", file=sys.stderr))
        self.loadFinished.connect(lambda ok: print(f"[DEBUG] Load finished: {'OK' if ok else 'FAILED'}", file=sys.stderr))
    
    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        """在导航发生前检查 URL"""
        nav_types = {
            0: "LinkClicked",
            1: "FormSubmitted",
            2: "BackForward",
            3: "Reload",
            4: "Other"
        }
        
        hostname = url.host()
        nav_type_name = nav_types.get(navigation_type, f"Unknown({navigation_type})")
        
        print(f"[NAV] Type: {nav_type_name}, MainFrame: {is_main_frame}, URL: {url.toString()}", file=sys.stderr)
        
        # 允许所有 bilibili.com 及其子域名
        if hostname and 'bilibili.com' in hostname:
            print(f"[ALLOW] {url.toString()}", file=sys.stderr)
            return True
        
        # 允许 Bilibili CDN 和视频域名
        allowed_domains = ['hdslb.com', 'bilivideo.com', 'acgvideo.com']
        
        if hostname and any(hostname.endswith(domain) for domain in allowed_domains):
            print(f"[ALLOW CDN] {url.toString()}", file=sys.stderr)
            return True
        
        # 阻止其他网站
        if hostname:
            print(f"[BLOCK] {url.toString()}", file=sys.stderr)
            QMessageBox.warning(
                self.view(),
                '访问限制',
                f'不允许访问非 Bilibili 网站：\n{url.toString()}\n\n小B 只能播放 Bilibili 视频。',
                QMessageBox.Ok
            )
            return False
        
        print(f"[ALLOW OTHER] {url.toString()}", file=sys.stderr)
        return True


class DebugBrowser(QWebEngineView):
    """调试浏览器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        print("[INIT] Creating browser...", file=sys.stderr)
        
        # 配置 WebEngine 设置 - 启用所有必要特性
        settings = self.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, True)
        settings.setAttribute(QWebEngineSettings.SpatialNavigationEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        
        print("[INIT] Settings configured (with WebGL)", file=sys.stderr)
        
        # 设置现代 User-Agent
        profile = QWebEngineProfile.defaultProfile()
        modern_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        profile.setHttpUserAgent(modern_ua)
        
        print(f"[INIT] User-Agent set to: {modern_ua}", file=sys.stderr)
        
        # 创建调试网页
        debug_page = DebugWebEnginePage(profile, self)
        self.setPage(debug_page)
        
        print("[INIT] Browser ready", file=sys.stderr)


class XiaobBrowser(QMainWindow):
    """小B 专属浏览器"""
    
    def __init__(self):
        super().__init__()
        print("[MAIN] Creating window...", file=sys.stderr)
        
        self.setWindowTitle('小B')
        self.setGeometry(100, 100, 1200, 800)
        
        self.setWindowIcon(self._create_icon())
        
        # 创建浏览器
        self.browser = DebugBrowser(self)
        self.setCentralWidget(self.browser)
        
        print("[MAIN] Loading Bilibili...", file=sys.stderr)
        
        # 直接加载 Bilibili 首页
        self.browser.load(QUrl('https://www.bilibili.com'))
        
        print("[MAIN] Window created", file=sys.stderr)
    
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
    print("=" * 60, file=sys.stderr)
    print("小B 调试版启动", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    
    app = QApplication(sys.argv)
    window = XiaobBrowser()
    window.show()
    
    print("[MAIN] Application running...", file=sys.stderr)
    
    sys.exit(app.exec_())

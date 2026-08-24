#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 极简视频播放器
"""

import sys
import requests
from urllib.parse import quote

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon


class VideoItem(QWidget):
    """视频列表项组件"""
    
    def __init__(self, video_data, main_window=None):
        super().__init__()
        self.video_data = video_data
        self.bvid = video_data.get('bvid', '')
        self.url = f'https://www.bilibili.com/video/{self.bvid}' if self.bvid else ''
        self.main_window = main_window
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        title = video_data.get('title', '无标题')
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0066CC;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        owner = video_data.get('owner', {})
        author_name = owner.get('name', '未知UP') if isinstance(owner, dict) else '未知UP'
        
        stat = video_data.get('stat', {})
        view_count = stat.get('view', 0) if isinstance(stat, dict) else 0
        
        stats_text = f"👤 {author_name}  |  ▶️ {self._format_number(view_count)}"
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("font-size: 12px; color: #666666;")
        layout.addWidget(stats_label)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-radius: 5px;
            }
            QWidget:hover {
                background-color: #e8e8e8;
            }
        """)
    
    def _format_number(self, num):
        if num >= 100000000:
            return f'{num / 100000000:.1f}亿'
        elif num >= 10000:
            return f'{num / 10000:.1f}万'
        return str(num)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.url and self.main_window:
            self.main_window.open_video(self.url)


class XiaobClient(QMainWindow):
    """小B 客户端"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('小B')
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置窗口图标（白底黑字 B）
        self.setWindowIcon(self._create_icon())
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.bilibili.com'
        })
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 顶部标题栏
        title_bar = QWidget()
        title_bar.setStyleSheet("background-color: #0066CC; padding: 10px;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(15, 5, 15, 5)
        
        title_label = QLabel('📺 小B')
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        title_layout.addWidget(title_label)
        
        main_layout.addWidget(title_bar)
        
        # 视频列表
        self.video_list = QListWidget()
        self.video_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
        """)
        main_layout.addWidget(self.video_list)
        
        # WebView（初始隐藏）
        self.web_view = QWebEngineView()
        self.web_view.hide()
        main_layout.addWidget(self.web_view)
        
        # 加载热门视频
        self.load_hot_videos()
    
    def _create_icon(self):
        """创建白底黑字 B 图标"""
        from PyQt5.QtGui import QPixmap, QPainter, QFont
        from PyQt5.QtCore import QRect
        
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制黑色 B
        font = QFont('Arial', 40, QFont.Bold)
        painter.setFont(font)
        painter.setPen(Qt.black)
        painter.drawText(QRect(0, 0, 64, 64), Qt.AlignCenter, 'B')
        
        painter.end()
        
        icon = QIcon(pixmap)
        return icon
    
    def load_hot_videos(self):
        """加载热门视频"""
        try:
            url = 'https://api.bilibili.com/x/web-interface/popular'
            response = self.session.get(url, timeout=15)
            
            data = response.json()
            
            if data.get('code') == 0:
                videos = data['data']['list'][:20]
                self.display_videos(videos)
            else:
                error_msg = data.get('message', '加载失败')
                self.show_error(f'加载失败: {error_msg}')
        except Exception as e:
            self.show_error(f'网络错误: {str(e)[:80]}')
    
    def display_videos(self, videos):
        """显示视频列表"""
        self.video_list.clear()
        
        if not videos:
            item = QListWidgetItem('没有找到结果')
            item.setTextAlignment(Qt.AlignCenter)
            self.video_list.addItem(item)
            return
        
        for video in videos:
            widget = VideoItem(video, main_window=self)
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.video_list.addItem(item)
            self.video_list.setItemWidget(item, widget)
    
    def open_video(self, url):
        """在内嵌浏览器中打开视频"""
        print(f"Opening video: {url}", file=sys.stderr)
        
        self.video_list.hide()
        self.web_view.show()
        
        self.web_view.load(QUrl(url))
    
    def show_error(self, message):
        """显示错误信息"""
        self.video_list.clear()
        item = QListWidgetItem(message)
        item.setTextAlignment(Qt.AlignCenter)
        item.setForeground(Qt.red)
        self.video_list.addItem(item)
    
    def keyPressEvent(self, event):
        """ESC 键返回列表"""
        if event.key() == Qt.Key_Escape and self.web_view.isVisible():
            self.web_view.hide()
            self.video_list.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = XiaobClient()
    window.show()
    sys.exit(app.exec_())

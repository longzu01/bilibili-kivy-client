#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili PyQt Client - 基于 PyQt5 的 Bilibili 客户端
内嵌 Chromium 浏览器引擎，支持直接在窗口中播放视频
"""

import sys
import json
import requests
from urllib.parse import quote

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                             QListWidget, QListWidgetItem, QMessageBox, QDialog)
from PyQt5.QtCore import Qt, QUrl, pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView


class VideoItem(QWidget):
    """视频列表项组件"""
    
    def __init__(self, video_data, parent=None):
        super().__init__(parent)
        self.video_data = video_data
        self.bvid = video_data.get('bvid', '')
        self.url = f'https://www.bilibili.com/video/{self.bvid}' if self.bvid else ''
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # 标题
        title = video_data.get('title', '无标题')
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #0066CC;")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # UP主和播放量
        owner = video_data.get('owner', {})
        author_name = owner.get('name', '未知UP') if isinstance(owner, dict) else '未知UP'
        
        stat = video_data.get('stat', {})
        view_count = stat.get('view', 0) if isinstance(stat, dict) else 0
        
        stats_text = f"👤 {author_name}  |  ▶️ {self._format_number(view_count)}"
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("font-size: 12px; color: #666666;")
        layout.addWidget(stats_label)
        
        # 设置样式
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
        """格式化数字"""
        if num >= 100000000:
            return f'{num / 100000000:.1f}亿'
        elif num >= 10000:
            return f'{num / 10000:.1f}万'
        return str(num)
    
    def mousePressEvent(self, event):
        """点击事件"""
        if event.button() == Qt.LeftButton and self.url:
            # 通知父窗口打开视频
            if hasattr(self.parent(), 'open_video'):
                self.parent().open_video(self.url)


class LoginDialog(QDialog):
    """登录对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Bilibili 登录')
        self.setFixedSize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel('🔐 Bilibili 登录')
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0066CC;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 说明
        desc = QLabel(
            '请输入你的 Bilibili Cookie\n\n'
            '获取方法：\n'
            '1. 浏览器登录 bilibili.com\n'
            '2. F12 打开开发者工具\n'
            '3. Network 标签页刷新页面\n'
            '4. 复制 Cookie'
        )
        desc.setStyleSheet("font-size: 12px; color: #666666;")
        layout.addWidget(desc)
        
        # Cookie 输入框
        self.cookie_input = QLineEdit()
        self.cookie_input.setPlaceholderText('粘贴 Cookie 到这里...')
        layout.addWidget(self.cookie_input)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        skip_btn = QPushButton('跳过登录')
        skip_btn.clicked.connect(lambda: self.accept_with_cookie(None))
        
        login_btn = QPushButton('确认登录')
        login_btn.clicked.connect(lambda: self.accept_with_cookie(self.cookie_input.text()))
        
        btn_layout.addWidget(skip_btn)
        btn_layout.addWidget(login_btn)
        layout.addLayout(btn_layout)
    
    def accept_with_cookie(self, cookie):
        self.cookie = cookie.strip() if cookie else None
        self.accept()


class BilibiliClient(QMainWindow):
    """Bilibili 客户端主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Bilibili 客户端')
        self.setGeometry(100, 100, 1200, 800)
        
        # HTTP Session
        self.session = requests.Session()
        self.cookie = None
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 顶部导航栏
        nav_layout = QHBoxLayout()
        
        self.title_label = QLabel('📺 Bilibili 客户端')
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #0066CC;")
        nav_layout.addWidget(self.title_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('搜索视频...')
        self.search_input.returnPressed.connect(self.do_search)
        nav_layout.addWidget(self.search_input)
        
        search_btn = QPushButton('🔍')
        search_btn.clicked.connect(self.do_search)
        nav_layout.addWidget(search_btn)
        
        main_layout.addLayout(nav_layout)
        
        # 视频列表
        self.video_list = QListWidget()
        self.video_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
        """)
        main_layout.addWidget(self.video_list)
        
        # 底部状态栏
        self.status_label = QLabel('就绪')
        self.status_label.setStyleSheet("font-size: 12px; color: #666666;")
        main_layout.addWidget(self.status_label)
        
        # WebView（初始隐藏）
        self.web_view = QWebEngineView()
        self.web_view.hide()
        main_layout.addWidget(self.web_view)
        
        # 显示登录对话框
        self.show_login_dialog()
    
    def show_login_dialog(self):
        """显示登录对话框"""
        dialog = LoginDialog(self)
        if dialog.exec_():
            self.cookie = dialog.cookie
            if self.cookie:
                headers = {
                    'Cookie': self.cookie,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                self.session.headers.update(headers)
                self.status_label.setText('已登录')
            else:
                self.status_label.setText('未登录（部分功能受限）')
            
            # 加载热门视频
            self.load_hot_videos()
    
    def load_hot_videos(self):
        """加载热门视频"""
        self.status_label.setText('加载中...')
        
        try:
            url = 'https://api.bilibili.com/x/web-interface/popular'
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 412:
                self.show_error('需要登录才能查看热门视频')
                return
            
            data = response.json()
            
            if data.get('code') == 0:
                videos = data['data']['list'][:20]
                self.display_videos(videos)
                self.status_label.setText(f'已加载 {len(videos)} 个热门视频')
            elif data.get('code') == -412:
                self.show_error('需要登录才能查看热门视频')
            else:
                error_msg = data.get('message', '加载失败')
                self.show_error(f'加载失败: {error_msg}')
        except Exception as e:
            self.show_error(f'网络错误: {str(e)}')
    
    def do_search(self):
        """执行搜索"""
        keyword = self.search_input.text().strip()
        if not keyword:
            return
        
        self.status_label.setText(f'搜索 "{keyword}"...')
        self.video_list.clear()
        
        try:
            url = f'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={quote(keyword)}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.bilibili.com'
            }
            
            if self.cookie:
                headers['Cookie'] = self.cookie
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if not response.text or len(response.text.strip()) == 0:
                self.show_error('搜索失败: API 返回空响应')
                return
            
            data = response.json()
            
            if data.get('code') == 0:
                results = data['data'].get('result', [])
                videos = results[:20] if results else []
                self.display_videos(videos)
                self.status_label.setText(f'找到 {len(videos)} 个结果')
            elif data.get('code') == -412:
                self.show_error('搜索需要登录')
            else:
                error_msg = data.get('message', '搜索失败')
                self.show_error(f'搜索失败: {error_msg}')
        except Exception as e:
            self.show_error(f'搜索错误: {str(e)}')
    
    def display_videos(self, videos):
        """显示视频列表"""
        self.video_list.clear()
        
        if not videos:
            item = QListWidgetItem('没有找到结果')
            item.setTextAlignment(Qt.AlignCenter)
            self.video_list.addItem(item)
            return
        
        for video in videos:
            widget = VideoItem(video, self)
            item = QListWidgetItem()
            item.setSizeHint(widget.sizeHint())
            self.video_list.addItem(item)
            self.video_list.setItemWidget(item, widget)
    
    def open_video(self, url):
        """在 WebView 中打开视频"""
        print(f"Opening video: {url}", file=sys.stderr)
        
        # 隐藏列表，显示 WebView
        self.video_list.hide()
        self.web_view.show()
        
        # 加载视频页面
        self.web_view.load(QUrl(url))
        self.status_label.setText(f'正在播放: {url}')
    
    def show_error(self, message):
        """显示错误信息"""
        self.video_list.clear()
        item = QListWidgetItem(message)
        item.setTextAlignment(Qt.AlignCenter)
        item.setForeground(Qt.red)
        self.video_list.addItem(item)
        self.status_label.setText('错误')
    
    def keyPressEvent(self, event):
        """ESC 键返回列表"""
        if event.key() == Qt.Key_Escape and self.web_view.isVisible():
            self.web_view.hide()
            self.video_list.show()
            self.status_label.setText('就绪')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = BilibiliClient()
    window.show()
    sys.exit(app.exec_())

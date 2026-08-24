#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili PyQt Client - 修复版二维码登录
使用 qrcode 库生成二维码图片
"""

import sys
import json
import time
import requests
from urllib.parse import quote

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                             QListWidget, QListWidgetItem, QMessageBox, QDialog,
                             QTabWidget)
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QPixmap


class VideoItem(QWidget):
    """视频列表项组件"""
    
    def __init__(self, video_data, parent=None):
        super().__init__(parent)
        self.video_data = video_data
        self.bvid = video_data.get('bvid', '')
        self.url = f'https://www.bilibili.com/video/{self.bvid}' if self.bvid else ''
        
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
        if event.button() == Qt.LeftButton and self.url:
            if hasattr(self.parent(), 'open_video'):
                self.parent().open_video(self.url)


class QRCodeLoginDialog(QDialog):
    """二维码登录对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Bilibili 登录')
        self.setFixedSize(450, 550)
        
        self.qrcode_key = None
        self.oauth_key = None
        self.cookie = None
        self.poll_timer = QTimer()
        self.poll_timer.timeout.connect(self.check_qr_status)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel('🔐 Bilibili 登录')
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #0066CC;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Tab 切换
        self.tab_widget = QTabWidget()
        
        # 二维码登录 Tab
        qr_tab = QWidget()
        qr_layout = QVBoxLayout(qr_tab)
        
        qr_desc = QLabel('请使用哔哩哔哩 APP 扫描二维码登录')
        qr_desc.setStyleSheet("font-size: 12px; color: #666666;")
        qr_desc.setAlignment(Qt.AlignCenter)
        qr_layout.addWidget(qr_desc)
        
        # 显示二维码图片
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        self.qr_label.setMinimumHeight(250)
        self.qr_label.setStyleSheet("background-color: white; border: 1px solid #ddd;")
        qr_layout.addWidget(self.qr_label)
        
        self.qr_status_label = QLabel('正在生成二维码...')
        self.qr_status_label.setStyleSheet("font-size: 12px; color: #666666;")
        self.qr_status_label.setAlignment(Qt.AlignCenter)
        qr_layout.addWidget(self.qr_status_label)
        
        refresh_btn = QPushButton('刷新二维码')
        refresh_btn.clicked.connect(self.generate_qrcode)
        qr_layout.addWidget(refresh_btn)
        
        self.tab_widget.addTab(qr_tab, '二维码登录')
        
        # Cookie 登录 Tab
        cookie_tab = QWidget()
        cookie_layout = QVBoxLayout(cookie_tab)
        
        cookie_desc = QLabel(
            '请输入你的 Bilibili Cookie\n\n'
            '获取方法：\n'
            '1. 浏览器登录 bilibili.com\n'
            '2. F12 打开开发者工具\n'
            '3. Network 标签页刷新页面\n'
            '4. 复制 Cookie'
        )
        cookie_desc.setStyleSheet("font-size: 12px; color: #666666;")
        cookie_layout.addWidget(cookie_desc)
        
        self.cookie_input = QLineEdit()
        self.cookie_input.setPlaceholderText('粘贴 Cookie 到这里...')
        cookie_layout.addWidget(self.cookie_input)
        
        cookie_login_btn = QPushButton('确认登录')
        cookie_login_btn.clicked.connect(lambda: self.accept_with_cookie(self.cookie_input.text()))
        cookie_layout.addWidget(cookie_login_btn)
        
        self.tab_widget.addTab(cookie_tab, 'Cookie 登录')
        
        layout.addWidget(self.tab_widget)
        
        # 底部按钮
        btn_layout = QHBoxLayout()
        
        skip_btn = QPushButton('跳过登录')
        skip_btn.clicked.connect(lambda: self.accept_with_cookie(None))
        
        btn_layout.addWidget(skip_btn)
        layout.addLayout(btn_layout)
        
        # 生成二维码
        self.generate_qrcode()
    
    def generate_qrcode(self):
        """生成二维码"""
        try:
            # 调用 Bilibili API 获取二维码
            url = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate'
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('code') == 0:
                self.qrcode_key = data['data']['qrcode_key']
                qrcode_url = data['data']['url']
                
                # 尝试使用 qrcode 库生成二维码图片
                try:
                    import qrcode
                    from io import BytesIO
                    
                    qr = qrcode.QRCode(version=1, box_size=10, border=5)
                    qr.add_data(qrcode_url)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    
                    # 转换为 QPixmap
                    buffer = BytesIO()
                    img.save(buffer, format='PNG')
                    pixmap = QPixmap()
                    pixmap.loadFromData(buffer.getvalue())
                    
                    # 缩放图片
                    scaled_pixmap = pixmap.scaled(250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.qr_label.setPixmap(scaled_pixmap)
                    
                except ImportError:
                    # 如果没有 qrcode 库，显示 URL 让用户手动访问
                    self.qr_label.setText(f'二维码 URL:\n{qrcode_url}\n\n请安装 qrcode 库: pip install qrcode[pil]')
                
                self.qr_status_label.setText('请使用哔哩哔哩 APP 扫描二维码')
                
                # 开始轮询检查状态
                self.poll_timer.start(3000)
            else:
                self.qr_status_label.setText(f'生成二维码失败: {data.get("message", "未知错误")}')
        except Exception as e:
            self.qr_status_label.setText(f'网络错误: {str(e)}')
    
    def check_qr_status(self):
        """检查二维码扫描状态"""
        if not self.qrcode_key:
            return
        
        try:
            url = f'https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key={self.qrcode_key}'
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('code') == 0:
                status = data['data'].get('code')
                
                if status == 0:  # 扫码成功
                    self.poll_timer.stop()
                    # 从响应头中提取 Cookie
                    cookies = response.headers.get('Set-Cookie', '')
                    if cookies:
                        self.cookie = cookies.split(';')[0]
                        self.accept()
                    else:
                        self.qr_status_label.setText('登录成功但未获取到 Cookie')
                elif status == 86101:  # 未扫描
                    self.qr_status_label.setText('等待扫描...')
                elif status == 86090:  # 已扫描未确认
                    self.qr_status_label.setText('已在手机确认，请等待...')
                elif status == 86038:  # 二维码过期
                    self.poll_timer.stop()
                    self.qr_status_label.setText('二维码已过期，请点击刷新')
        except Exception as e:
            print(f"检查状态错误: {e}", file=sys.stderr)
    
    def accept_with_cookie(self, cookie):
        self.cookie = cookie.strip() if cookie else None
        self.poll_timer.stop()
        self.accept()


class BilibiliClient(QMainWindow):
    """Bilibili 客户端主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Bilibili 客户端')
        self.setGeometry(100, 100, 1200, 800)
        
        self.session = requests.Session()
        self.cookie = None
        
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
        
        login_btn = QPushButton('🔑 登录')
        login_btn.clicked.connect(self.show_login_dialog)
        nav_layout.addWidget(login_btn)
        
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
        
        # WebView（初始隐藏）
        self.web_view = QWebEngineView()
        self.web_view.hide()
        main_layout.addWidget(self.web_view)
        
        # 底部状态栏
        self.status_label = QLabel('就绪')
        self.status_label.setStyleSheet("font-size: 12px; color: #666666;")
        main_layout.addWidget(self.status_label)
        
        # 直接加载热门视频（不强制登录）
        self.load_hot_videos()
    
    def show_login_dialog(self):
        """显示登录对话框"""
        dialog = QRCodeLoginDialog(self)
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
            
            self.load_hot_videos()
    
    def load_hot_videos(self):
        """加载热门视频"""
        self.status_label.setText('加载中...')
        
        try:
            url = 'https://api.bilibili.com/x/web-interface/popular'
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 412:
                self.show_error('需要登录才能查看热门视频\n请点击右上角 🔑 登录')
                return
            
            data = response.json()
            
            if data.get('code') == 0:
                videos = data['data']['list'][:20]
                self.display_videos(videos)
                self.status_label.setText(f'已加载 {len(videos)} 个热门视频')
            elif data.get('code') == -412:
                self.show_error('需要登录才能查看热门视频\n请点击右上角 🔑 登录')
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
                self.show_error('搜索需要登录\n请点击右上角 🔑 登录')
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
        
        self.video_list.hide()
        self.web_view.show()
        
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

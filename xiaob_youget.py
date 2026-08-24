#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小B - Bilibili 真·视频播放器 (you-get 引擎)
完全独立，不依赖浏览器
"""

import sys
import requests
import subprocess
import tempfile
import os
from urllib.parse import quote

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
                             QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class VideoItem(QWidget):
    """视频列表项组件"""
    
    def __init__(self, video_data, main_window=None):
        super().__init__()
        self.video_data = video_data
        self.bvid = video_data.get('bvid', '')
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
        if event.button() == Qt.LeftButton and self.bvid and self.main_window:
            self.main_window.play_video(self.bvid)


class XiaobPlayer(QMainWindow):
    """小B 视频播放器"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('小B')
        self.setGeometry(100, 100, 1200, 800)
        
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
        
        font = QFont('Arial', 40, QFont.Bold)
        painter.setFont(font)
        painter.setPen(Qt.black)
        painter.drawText(QRect(0, 0, 64, 64), Qt.AlignCenter, 'B')
        
        painter.end()
        
        return QIcon(pixmap)
    
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
    
    def play_video(self, bvid):
        """用 you-get 下载并播放视频"""
        print(f"Playing video: {bvid}", file=sys.stderr)
        
        # 构造 Bilibili URL
        url = f'https://www.bilibili.com/video/{bvid}'
        
        # 询问用户：下载到本地播放还是在线播放
        reply = QMessageBox.question(
            self,
            '播放方式',
            '选择播放方式：\n\nYes = 下载到本地后播放（更稳定）\nNo = 直接在线播放（更快）',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 下载到临时文件
            self._download_and_play(url)
        else:
            # 直接用 you-get 播放
            self._stream_and_play(url)
    
    def _download_and_play(self, url):
        """下载视频到本地并播放"""
        try:
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            
            # 使用 you-get 下载
            cmd = ['you-get', '-o', temp_dir, url]
            print(f"Downloading: {' '.join(cmd)}", file=sys.stderr)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                self.show_error(f'下载失败: {result.stderr[:200]}')
                return
            
            # 找到下载的视频文件
            video_files = [f for f in os.listdir(temp_dir) if f.endswith(('.mp4', '.flv', '.mkv'))]
            
            if not video_files:
                self.show_error('未找到视频文件')
                return
            
            video_path = os.path.join(temp_dir, video_files[0])
            
            # 用系统默认播放器打开
            subprocess.Popen(['start', video_path], shell=True)
            print(f"Playing local file: {video_path}", file=sys.stderr)
            
        except Exception as e:
            self.show_error(f'播放失败: {str(e)[:80]}')
    
    def _stream_and_play(self, url):
        """直接在线播放（you-get 会调用系统播放器）"""
        try:
            cmd = ['you-get', url]
            print(f"Streaming: {' '.join(cmd)}", file=sys.stderr)
            
            # you-get 会自动调用系统默认播放器
            subprocess.Popen(cmd, shell=True)
            print("Video streaming started", file=sys.stderr)
            
        except Exception as e:
            self.show_error(f'播放失败: {str(e)[:80]}')
    
    def show_error(self, message):
        """显示错误信息"""
        self.video_list.clear()
        item = QListWidgetItem(message)
        item.setTextAlignment(Qt.AlignCenter)
        item.setForeground(Qt.red)
        self.video_list.addItem(item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = XiaobPlayer()
    window.show()
    sys.exit(app.exec_())

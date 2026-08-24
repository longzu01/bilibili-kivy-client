#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili Kivy Client - 轻量级 Bilibili 客户端
参考"哔哩终端"设计，支持登录、搜索、视频浏览等功能
"""

import sys
import re
import threading
from urllib.parse import quote

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle

import requests


class VideoCard(BoxLayout):
    """视频卡片组件"""
    
    def __init__(self, video_data, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=150, padding=8, spacing=5, **kwargs)
        
        # 顶部：封面 + 标题
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=100, spacing=8)
        
        # 视频封面
        cover_url = video_data.get('pic', '')
        if cover_url and cover_url.startswith('http'):
            # 使用异步加载
            cover_img = Image(source=cover_url, allow_stretch=True, keep_ratio=True, size_hint_x=None, width=120)
        else:
            # 占位图
            cover_img = Widget(size_hint_x=None, width=120)
            with cover_img.canvas:
                Color(0.2, 0.25, 0.35, 1)
                Rectangle(pos=cover_img.pos, size=(120, 100))
        
        # 标题和简介
        info_layout = BoxLayout(orientation='vertical', spacing=3)
        
        title = video_data.get('title', '无标题')
        title = re.sub(r'<[^>]+>', '', title)  # 清理 HTML
        title_label = Label(
            text=title[:60] + '...' if len(title) > 60 else title,
            color=(0.15, 0.35, 0.75, 1),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=50
        )
        title_label.bind(size=title_label.setter('text_size'))
        title_label.text_size = (Window.width - 160, None)
        
        # UP 主和统计信息
        owner = video_data.get('owner', {})
        author_name = owner.get('name', '未知UP') if isinstance(owner, dict) else '未知UP'
        
        stat = video_data.get('stat', {})
        view_count = stat.get('view', 0) if isinstance(stat, dict) else 0
        
        stats_text = f'👤 {author_name}  |  ▶️ {self._format_number(view_count)}'
        stats_label = Label(
            text=stats_text,
            color=(0.4, 0.45, 0.55, 1),
            halign='left',
            size_hint_y=None,
            height=25
        )
        
        info_layout.add_widget(title_label)
        info_layout.add_widget(stats_label)
        
        top_layout.add_widget(cover_img)
        top_layout.add_widget(info_layout)
        
        self.add_widget(top_layout)
        
        # 底部分隔线
        separator = Widget(size_hint_y=None, height=2)
        with separator.canvas:
            Color(0.75, 0.8, 0.9, 0.5)
            Rectangle(pos=separator.pos, size=(Window.width, 2))
        self.add_widget(separator)
    
    def _format_number(self, num):
        """格式化数字（万/亿）"""
        if num >= 100000000:
            return f'{num / 100000000:.1f}亿'
        elif num >= 10000:
            return f'{num / 10000:.1f}万'
        return str(num)


class LoginDialog(BoxLayout):
    """登录对话框"""
    
    def __init__(self, on_login_success, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=15, **kwargs)
        self.on_login_success = on_login_success
        
        # 标题
        title = Label(
            text='🔐 Bilibili 登录',
            font_size='24sp',
            bold=True,
            color=(0.2, 0.4, 0.8, 1),
            size_hint_y=None,
            height=40
        )
        self.add_widget(title)
        
        # 说明文字
        desc = Label(
            text='请输入你的 Bilibili Cookie\n\n获取方法：\n1. 浏览器登录 bilibili.com\n2. F12 打开开发者工具\n3. Network 标签页刷新页面\n4. 复制 Cookie',
            color=(0.5, 0.5, 0.5, 1),
            halign='center',
            size_hint_y=None,
            height=120
        )
        desc.bind(size=desc.setter('text_size'))
        desc.text_size = (Window.width - 40, None)
        self.add_widget(desc)
        
        # Cookie 输入框
        self.cookie_input = TextInput(
            hint_text='粘贴 Cookie 到这里...',
            multiline=True,
            size_hint_y=None,
            height=80,
            font_size='12sp'
        )
        self.add_widget(self.cookie_input)
        
        # 按钮区域
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        
        skip_btn = Button(text='跳过登录', background_color=(0.6, 0.6, 0.6, 1))
        skip_btn.bind(on_press=lambda x: self.on_login_success(None))
        
        login_btn = Button(text='确认登录', background_color=(0.2, 0.5, 0.9, 1))
        login_btn.bind(on_press=self.handle_login)
        
        btn_layout.add_widget(skip_btn)
        btn_layout.add_widget(login_btn)
        self.add_widget(btn_layout)
    
    def handle_login(self, instance):
        cookie = self.cookie_input.text.strip()
        if not cookie:
            return
        self.on_login_success(cookie)


class BilibiliClientApp(App):
    """Bilibili 客户端主应用"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = requests.Session()
        self.cookie = None
        self.current_page = 'home'
    
    def build(self):
        """构建主界面"""
        # 主布局
        main_layout = BoxLayout(orientation='vertical')
        
        # 顶部导航栏
        nav_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, padding=10, spacing=10)
        
        self.title_label = Label(
            text='📺 Bilibili 客户端',
            font_size='18sp',
            bold=True,
            color=(0.2, 0.4, 0.8, 1),
            halign='left'
        )
        
        # 搜索框
        self.search_input = TextInput(
            hint_text='搜索视频...',
            multiline=False,
            size_hint_x=0.6
        )
        self.search_input.bind(on_text_validate=self.do_search)
        
        search_btn = Button(text='🔍', size_hint_x=None, width=50)
        search_btn.bind(on_press=self.do_search)
        
        nav_bar.add_widget(self.title_label)
        nav_bar.add_widget(self.search_input)
        nav_bar.add_widget(search_btn)
        
        main_layout.add_widget(nav_bar)
        
        # 内容区域（滚动视图）
        self.scroll_view = ScrollView()
        self.result_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.result_layout.bind(minimum_height=self.result_layout.setter('height'))
        self.scroll_view.add_widget(self.result_layout)
        
        main_layout.add_widget(self.scroll_view)
        
        # 底部状态栏
        status_bar = BoxLayout(size_hint_y=None, height=30, padding=5)
        self.status_label = Label(
            text='就绪',
            color=(0.5, 0.5, 0.5, 1),
            font_size='12sp',
            halign='left'
        )
        status_bar.add_widget(self.status_label)
        main_layout.add_widget(status_bar)
        
        # 显示登录对话框
        Clock.schedule_once(lambda dt: self.show_login_dialog(), 0.5)
        
        return main_layout
    
    def show_login_dialog(self):
        """显示登录对话框"""
        from kivy.uix.popup import Popup
        
        def on_login_success(cookie):
            self.cookie = cookie
            if cookie:
                # 设置 Cookie
                headers = {
                    'Cookie': cookie,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                self.session.headers.update(headers)
                self.status_label.text = '已登录'
            else:
                self.status_label.text = '未登录（部分功能受限）'
            
            popup.dismiss()
            # 加载热门视频
            self.load_hot_videos()
        
        dialog = LoginDialog(on_login_success=on_login_success)
        popup = Popup(
            title='',
            content=dialog,
            size_hint=(0.8, 0.6),
            auto_dismiss=False
        )
        popup.open()
    
    def load_hot_videos(self):
        """加载热门视频"""
        self.status_label.text = '加载中...'
        
        try:
            url = 'https://api.bilibili.com/x/web-interface/popular'
            response = self.session.get(url, timeout=10)
            data = response.json()
            
            if data.get('code') == 0:
                videos = data['data']['list'][:15]
                Clock.schedule_once(lambda dt: self.display_videos(videos), 0)
                self.status_label.text = f'已加载 {len(videos)} 个热门视频'
            else:
                error_msg = data.get('message', '加载失败')
                self.show_error(f'加载失败: {error_msg}')
        except Exception as e:
            self.show_error(f'网络错误: {str(e)}')
    
    def do_search(self, instance):
        """执行搜索"""
        keyword = self.search_input.text.strip()
        if not keyword:
            return
        
        self.status_label.text = f'搜索 "{keyword}"...'
        self.result_layout.clear_widgets()
        
        # 显示加载中
        loading = Label(
            text='搜索中...',
            color=(0.2, 0.4, 0.8, 1),
            size_hint_y=None,
            height=50
        )
        self.result_layout.add_widget(loading)
        
        # 后台线程搜索
        thread = threading.Thread(target=self.search_videos, args=(keyword,))
        thread.daemon = True
        thread.start()
    
    def search_videos(self, keyword):
        """搜索视频（后台线程）"""
        try:
            url = f'https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={quote(keyword)}'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.bilibili.com'
            }
            
            if self.cookie:
                headers['Cookie'] = self.cookie
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            # 检查响应
            if not response.text or len(response.text.strip()) == 0:
                Clock.schedule_once(lambda dt: self.show_error('搜索失败: API 返回空响应'), 0)
                return
            
            data = response.json()
            
            if data.get('code') == 0:
                results = data['data'].get('result', [])
                videos = results[:15] if results else []
                Clock.schedule_once(lambda dt: self.display_videos(videos), 0)
                self.status_label.text = f'找到 {len(videos)} 个结果'
            elif data.get('code') == -412:
                Clock.schedule_once(lambda dt: self.show_error('搜索需要登录，请在设置中添加 Cookie'), 0)
            else:
                error_msg = data.get('message', '搜索失败')
                Clock.schedule_once(lambda dt: self.show_error(f'搜索失败: {error_msg}'), 0)
                
        except Exception as e:
            Clock.schedule_once(lambda dt: self.show_error(f'搜索错误: {str(e)}'), 0)
    
    def display_videos(self, videos):
        """显示视频列表"""
        self.result_layout.clear_widgets()
        
        if not videos:
            no_result = Label(
                text='没有找到结果',
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=50
            )
            self.result_layout.add_widget(no_result)
            return
        
        for video in videos:
            card = VideoCard(video)
            self.result_layout.add_widget(card)
    
    def show_error(self, message):
        """显示错误信息"""
        self.result_layout.clear_widgets()
        error_label = Label(
            text=message,
            color=(0.8, 0.2, 0.2, 1),
            size_hint_y=None,
            height=50,
            halign='center'
        )
        error_label.bind(size=error_label.setter('text_size'))
        error_label.text_size = (Window.width - 20, None)
        self.result_layout.add_widget(error_label)
        self.status_label.text = '错误'


if __name__ == '__main__':
    print("Starting Bilibili Client...", file=sys.stderr)
    try:
        app = BilibiliClientApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

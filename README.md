# Bilibili Kivy Client

轻量级 Bilibili 第三方客户端，基于 Python + Kivy 开发。

## 功能特性

- 📺 **热门视频浏览** - 展示 Bilibili 热门视频列表
- 🔍 **视频搜索** - 支持关键词搜索（需登录）
- 🔐 **Cookie 登录** - 支持通过 Cookie 登录解锁完整功能
- 🖼️ **视频封面** - 显示视频缩略图
- 📱 **响应式界面** - 适配不同窗口大小
- ⚡ **轻量快速** - 异步加载，不阻塞界面

## 安装依赖

```bash
pip install kivy requests
```

## 运行程序

```bash
python bilibili_client.py
```

## 使用说明

### 首次启动

1. 程序启动后会弹出登录对话框
2. 可以选择"跳过登录"使用基础功能
3. 或输入 Cookie 解锁完整功能（搜索等）

### 获取 Cookie

1. 浏览器访问 [bilibili.com](https://www.bilibili.com) 并登录
2. 按 `F12` 打开开发者工具
3. 切换到 **Network** 标签页
4. 刷新页面
5. 点击任意请求，在 **Headers** 中找到 **Cookie**
6. 复制完整的 Cookie 字符串

### 主要功能

- **首页**: 自动加载热门视频
- **搜索**: 在顶部搜索框输入关键词，按回车或点击搜索按钮
- **视频卡片**: 显示封面、标题、UP主和播放量

## 技术栈

- **Python 3.8+**
- **Kivy 2.x** - 跨平台 GUI 框架
- **Requests** - HTTP 客户端

## 参考项目

灵感来源于 [哔哩终端 (BiliClient)](https://github.com/huanli233/BiliClient)

## License

MIT

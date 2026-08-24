# Bilibili Android App

小B - Bilibili 专属浏览器 Android 版

## 功能特性

- 🌐 **WebView 加载** - 基于 Android WebView 加载 Bilibili 网页
- 🔒 **域名限制** - 只能访问 bilibili.com 及相关域名
- ⚡ **轻量快速** - 无多余功能，专注视频浏览
- 📱 **原生体验** - 支持返回键导航

## 构建要求

- Android Studio 2023+
- JDK 17+
- Android SDK API Level 34

## 构建步骤

1. 用 Android Studio 打开 `android` 目录
2. 等待 Gradle 同步完成
3. 点击 **Build > Build Bundle(s) / APK(s) > Build APK(s)**
4. 生成的 APK 在 `app/build/outputs/apk/debug/` 目录下

## 安装

将生成的 APK 文件传输到 Android 手机，直接安装即可。

## 技术栈

- **Android SDK** - 原生 Android 开发
- **WebView** - 网页渲染引擎
- **Material Design** - UI 组件库

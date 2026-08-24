# Bilibili Android App - 小B

基于 Android WebView 的 Bilibili 专属浏览器应用。

## 核心特性

- 🌐 **WebView 加载** - 使用 Android 原生 WebView 加载 Bilibili 网页
- 🔒 **域名限制** - 自动拦截非 Bilibili 域名的跳转
- ⚡ **轻量快速** - 无地址栏，专注视频浏览体验
- 📱 **返回键支持** - 支持浏览器历史回退

## 项目结构

```
android/
├── app/
│   ├── src/main/
│   │   ├── java/com/xiaob/bilibili/
│   │   │   └── MainActivity.java      # 主 Activity
│   │   ├── res/
│   │   │   ├── layout/
│   │   │   │   └── activity_main.xml  # 布局文件
│   │   │   └── values/
│   │   │       ├── strings.xml        # 字符串资源
│   │   │       └── themes.xml         # 主题配置
│   │   └── AndroidManifest.xml        # 清单文件
│   └── build.gradle                   # App 构建配置
├── build.gradle                       # 根构建配置
└── README.md                          # 说明文档
```

## 构建方法

### 方法一：Android Studio

1. 用 Android Studio 打开 `android` 目录
2. 等待 Gradle 同步完成
3. 点击 **Build > Build Bundle(s) / APK(s) > Build APK(s)**
4. 生成的 APK 在 `app/build/outputs/apk/debug/` 目录下

### 方法二：命令行

```bash
cd android
./gradlew assembleDebug
```

生成的 APK 在 `app/build/outputs/apk/debug/app-debug.apk`

## 安装

将生成的 APK 文件传输到 Android 手机，直接安装即可。

## 技术栈

- **Android SDK API 34** - 目标版本
- **minSdk 21** - 最低支持 Android 5.0
- **WebView** - 网页渲染引擎
- **Material Design** - UI 组件库

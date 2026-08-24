# 小B Android 版 - 构建指南

## 前置要求

### Windows 用户
推荐使用 WSL2（Windows Subsystem for Linux）或虚拟机运行 Ubuntu。

### Linux/Mac 用户
直接在本机操作。

## 安装 Buildozer

```bash
pip install buildozer
```

## 安装依赖

```bash
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    build-essential \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    autoconf \
    automake \
    libtool
```

## 构建 APK

```bash
# 初始化 buildozer
buildozer init

# 构建 debug 版本
buildozer android debug

# 构建 release 版本
buildozer android release
```

生成的 APK 文件在 `bin/` 目录下。

## 安装到手机

```bash
# 通过 ADB 安装
adb install bin/xiaob.bilibili-1.0-arm64-v8a_armeabi-v7a-debug.apk
```

或者将 APK 文件传输到手机，手动安装。

## 注意事项

- 首次构建会下载大量依赖，需要较长时间（30分钟以上）
- 确保网络连接稳定
- 需要至少 5GB 磁盘空间

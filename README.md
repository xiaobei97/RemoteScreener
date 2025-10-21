

**English | [中文](-%E4%B8%AD%E6%96%87%E7%89%88)**

# 🖥️ RemoteScreener

## Project Purpose

RemoteScreener is a simple and efficient remote screen monitoring system. It supports both LAN and public network deployment, suitable for remote assistance, teaching, enterprise IT, and home monitoring scenarios. The client silently captures the screen and pushes it to the server, which can be deployed locally or on a public VPS. The server provides real-time viewing via web browser and supports multiple viewers simultaneously.


✨ **Key Features**

- 🌐 Cross-network remote screen monitoring, server can be deployed on LAN or public network

- 🕵️‍♂️ Silent client operation, auto-reconnect, adaptive frame rate

- 🔒 Simple token authentication for secure access

- 🎚️ Flexible quality/frame rate configuration for different network environments

- 🖼️ Real-time web viewing, canvas auto-adapts to resolution

- 👀 Supports multiple browsers, always pushes the latest frame to avoid lag

## Tech Stack

- 🐍 Python 3

- 🍰 Flask (web server)

- 🔗 websockets (client-server communication)

- 🖥️ mss (screen capture)

- 🧮 OpenCV, numpy (image processing & encoding)

- 📦 PyInstaller (packaging to EXE)



## 🚀 Getting Started

### 1️⃣ Install Dependencies

Go to both `client` and `server` directories and run:

```shell
pip install -r requirements.txt
```

For better video encoding, it is recommended to install ffmpeg:

```shell
pip install ffmpeg-python
# Or download from https://ffmpeg.org/download.html and add to PATH
```

### 2️⃣ Package as EXE

Use PyInstaller to package both client and server as Windows EXE files.

#### 📦 Install PyInstaller

```shell
pip install pyinstaller
```

#### 🖥️ Package Client

In the `client` directory, run:

```shell
pyinstaller --noconsole --onefile client.py
```

⚠️ **Note:** After packaging, make sure to place `config.json` in the same directory as the client EXE, otherwise configuration will not load!

📝 Edit `config.json` as needed (server IP, port, token, frame rate, quality, etc.):

```json
{
	"server_ip": "127.0.0.1",
	"server_port": 8765,
	"token": "123456",
	"frame_rate": 10,
	"min_frame_rate": 3,
	"max_frame_rate": 20,
	"quality": 80
}
```

#### 🗄️ Package Server

In the `server` directory, run:

```shell
pyinstaller --onefile server.py
```

💡 It is recommended to keep the server console window for logs.

---

## � Future Plans

- 🤝 Multi-client push and split-screen display

- 🛡️ Frame encryption and permission management

- 🕹️ Remote control and file transfer

- 🔐 Traffic encryption for enhanced security

- 🌏 Better public network deployment and cross-network compatibility

---

---

## 🌏 中文版

---

## 🖥️ 远程屏幕监控系统

### 项目用途

本项目旨在实现一个简单高效的远程屏幕监控系统，支持局域网和公网部署，适用于远程协助、教学演示、企业运维、家庭监控等场景。客户端可静默采集屏幕并推送到服务端，服务端可部署在本地或公网 VPS，通过网页实时展示画面，支持多浏览器同时观看。

✨ **主要功能**

- 🌐 支持跨网络远程屏幕监控，服务端可部署于公网或局域网

- 🕵️‍♂️ 客户端静默运行，断线自动重连，帧率自适应

- 🔒 简单 token 校验，保障访问安全

- 🎚️ 画质/帧率可灵活配置，适应不同网络环境

- 🖼️ 服务端网页实时观看，canvas 自适应分辨率

- 👀 支持多浏览器同时观看，推送最新帧避免延迟堆积

### 技术栈

- 🐍 Python 3

- 🍰 Flask（服务端网页）

- 🔗 websockets（客户端与服务端通信）

- 🖥️ mss（屏幕采集）

- 🧮 OpenCV、numpy（图像处理与编码）

- 📦 PyInstaller（打包为EXE）

### 使用说明

#### 1️⃣ 安装依赖

分别进入 `client` 和 `server` 目录，执行：

```shell
pip install -r requirements.txt
```

如需更高效的视频编码，推荐安装 ffmpeg：

```shell
pip install ffmpeg-python
# 或自行下载安装 https://ffmpeg.org/download.html 并配置环境变量
```

#### 2️⃣ 打包为 EXE

推荐使用 PyInstaller 将客户端和服务端打包为 Windows 下的 EXE 文件。

##### 📦 安装 PyInstaller

```shell
pip install pyinstaller
```

##### 🖥️ 打包客户端

在 `client` 目录下执行：

```shell
pyinstaller --noconsole --onefile client.py
```

⚠️ **注意：** 打包后请务必将 `config.json` 放在客户端 EXE 的同目录下，否则无法加载配置！

📝 请根据实际需求修改 `config.json`，如服务器IP、端口、token、帧率、画质等参数。

`config.json` 示例：

```json
{
	"server_ip": "127.0.0.1",
	"server_port": 8765,
	"token": "123456",
	"frame_rate": 10,
	"min_frame_rate": 3,
	"max_frame_rate": 20,
	"quality": 80
}
```

##### 🗄️ 打包服务端

在 `server` 目录下执行：

```shell
pyinstaller --onefile server.py
```

💡 服务端建议保留命令行窗口，方便查看日志。

---

### 未来版本展望

- 🤝 支持多客户端同时推送，分屏展示

- 🛡️ 增加画面加密与权限管理

- 🕹️ 支持远程控制与文件传输

- 🔐 支持流量加密，提升数据安全性

- 🌏 优化公网部署体验，提升跨网络兼容性

---
### 3️⃣ 运行方式


🖱️ 双击 EXE 文件即可启动客户端和服务端。


🌍 服务端启动后，浏览器访问：

```
http://本机IP:5000
```


🔑 首次访问需输入 token（默认 123456，可通过环境变量 `SCREEN_TOKEN` 设置）。

## 未来版本展望

- 🤝 支持多客户端同时推送，分屏展示
- 🛡️ 增加画面加密与权限管理
- 🕹️ 支持远程控制与文件传输
- 🔐 支持流量加密，提升数据安全性
- 🌏 优化公网部署体验，提升跨网络兼容性

🎉 欢迎提出建议或贡献代码！


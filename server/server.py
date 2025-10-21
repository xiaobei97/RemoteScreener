import asyncio
import websockets
import threading
import base64
import time
from flask import Flask, render_template_string
import os
import json

# 配置
TOKEN = os.environ.get('SCREEN_TOKEN', '123456')
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5000
WS_HOST = '0.0.0.0'
WS_PORT = 8765
WEB_WS_PORT = 8766

app = Flask(__name__)

# 全局变量
latest_frame = None
frame_lock = threading.Lock()
web_clients = []
web_clients_lock = threading.Lock()
last_frame_time = 0

# HTML模板
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>屏幕监控系统</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #1e1e1e; color: white; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 20px; padding: 20px; background: #2d2d2d; border-radius: 10px; }
        .status-panel { display: flex; justify-content: space-around; margin-bottom: 20px; padding: 15px; background: #2d2d2d; border-radius: 10px; }
        .status-item { text-align: center; }
        .status-value { font-size: 1.2em; font-weight: bold; color: #4CAF50; }
        .video-container { background: black; border-radius: 10px; padding: 10px; margin-bottom: 20px; text-align: center; }
        #screen { max-width: 100%; max-height: 70vh; border: 2px solid #333; border-radius: 5px; }
        .controls { display: flex; justify-content: center; gap: 10px; margin-bottom: 20px; }
        button { padding: 10px 20px; background: #007acc; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #005a9e; }
        .connection-status { padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 10px; }
        .connected { background: #4CAF50; }
        .disconnected { background: #f44336; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖥️ 屏幕监控系统</h1>
            <p>实时查看客户端桌面画面</p>
        </div>
        
        <div id="tokenPrompt" class="status-panel">
            <div style="text-align: center; width: 100%;">
                <h3>请输入访问令牌</h3>
                <input type="password" id="tokenInput" value="123456" style="padding: 10px; margin: 10px; width: 200px;">
                <button onclick="connectWebSocket()">连接</button>
            </div>
        </div>

        <div id="mainContent" class="hidden">
            <div class="status-panel">
                <div class="status-item">
                    <div>连接状态</div>
                    <div id="status" class="status-value">等待连接...</div>
                </div>
                <div class="status-item">
                    <div>最后更新</div>
                    <div id="lastUpdate" class="status-value">-</div>
                </div>
                <div class="status-item">
                    <div>客户端数量</div>
                    <div id="clientCount" class="status-value">0</div>
                </div>
            </div>

            <div class="connection-status disconnected" id="connectionStatus">
                等待连接...
            </div>

            <div class="video-container">
                <canvas id="screen"></canvas>
            </div>

            <div class="controls">
                <button onclick="setQuality(40)">低质量</button>
                <button onclick="setQuality(60)">中等质量</button>
                <button onclick="setQuality(80)">高质量</button>
                <button onclick="takeScreenshot()">📸 截图</button>
                <button onclick="toggleFullscreen()">⛶ 全屏</button>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let canvas = document.getElementById('screen');
        let ctx = canvas.getContext('2d');
        let img = new Image();
        let lastUpdateTime = 0;
        let connectionStatus = document.getElementById('connectionStatus');
        let statusElement = document.getElementById('status');
        let lastUpdateElement = document.getElementById('lastUpdate');
        let clientCountElement = document.getElementById('clientCount');
        let tokenPrompt = document.getElementById('tokenPrompt');
        let mainContent = document.getElementById('mainContent');

        function connectWebSocket() {
            const token = document.getElementById('tokenInput').value;
            if (!token) {
                alert('请输入访问令牌！');
                return;
            }

            // 隐藏令牌输入，显示主内容
            tokenPrompt.classList.add('hidden');
            mainContent.classList.remove('hidden');

            // 连接WebSocket
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.hostname}:${window.location.port.replace('5000', '8766')}`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                console.log('已连接到服务器');
                connectionStatus.textContent = '已连接到服务器';
                connectionStatus.className = 'connection-status connected';
                statusElement.textContent = '已连接';
                
                // 发送认证消息
                ws.send(JSON.stringify({
                    type: 'auth',
                    token: token
                }));
            };

            ws.onclose = function() {
                console.log('与服务器断开连接');
                connectionStatus.textContent = '与服务器断开连接';
                connectionStatus.className = 'connection-status disconnected';
                statusElement.textContent = '连接断开';
                
                // 5秒后重连
                setTimeout(() => {
                    connectWebSocket();
                }, 5000);
            };

            ws.onerror = function(error) {
                console.log('连接错误:', error);
                connectionStatus.textContent = '连接错误';
                connectionStatus.className = 'connection-status disconnected';
            };

            ws.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'frame') {
                        const now = Date.now();
                        img.onload = function() {
                            // 自适应canvas大小
                            canvas.width = img.width;
                            canvas.height = img.height;
                            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
                            
                            // 更新状态
                            lastUpdateElement.textContent = new Date().toLocaleTimeString();
                            lastUpdateTime = now;
                        };
                        img.src = 'data:image/jpeg;base64,' + data.data;
                    }
                    else if (data.type === 'client_count') {
                        clientCountElement.textContent = data.data;
                        statusElement.textContent = `已连接 (${data.data}客户端)`;
                    }
                } catch (e) {
                    console.error('处理消息错误:', e);
                }
            };
        }

        function setQuality(quality) {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: 'set_quality',
                    quality: quality
                }));
            }
        }

        function takeScreenshot() {
            if (canvas.width > 0 && canvas.height > 0) {
                const link = document.createElement('a');
                link.download = 'screenshot_' + new Date().toISOString().replace(/[:.]/g, '-') + '.png';
                link.href = canvas.toDataURL();
                link.click();
            }
        }

        function toggleFullscreen() {
            if (!document.fullscreenElement) {
                canvas.requestFullscreen().catch(err => {
                    console.log('全屏请求失败:', err);
                });
            } else {
                document.exitFullscreen();
            }
        }

        // 定期检查连接状态
        setInterval(() => {
            const now = Date.now();
            if (now - lastUpdateTime > 5000 && lastUpdateTime > 0) {
                statusElement.textContent = '无数据流';
            }
        }, 1000);

        // 全屏事件监听
        canvas.addEventListener('dblclick', toggleFullscreen);

        // 自动连接（使用默认令牌）
        setTimeout(() => {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                connectWebSocket();
            }
        }, 1000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

class ScreenWebSocketServer:
    def __init__(self):
        self.clients = set()
    
    async def register(self, websocket):
        """注册屏幕客户端"""
        token = websocket.request_headers.get('X-Token')
        if token != TOKEN:
            await websocket.close(1008, "Invalid token")
            return False
        
        self.clients.add(websocket)
        print(f"新的屏幕客户端连接，当前客户端数: {len(self.clients)}")
        await self.broadcast_client_count()
        return True
    
    async def unregister(self, websocket):
        """注销屏幕客户端"""
        if websocket in self.clients:
            self.clients.remove(websocket)
            print(f"屏幕客户端断开，当前客户端数: {len(self.clients)}")
            await self.broadcast_client_count()
    
    async def broadcast_client_count(self):
        """广播客户端数量"""
        count_data = json.dumps({"type": "client_count", "data": len(self.clients)})
        with web_clients_lock:
            for client in web_clients[:]:
                try:
                    await client.send(count_data)
                except:
                    web_clients.remove(client)
    
    async def handle_client(self, websocket, path):
        """处理屏幕客户端连接"""
        if not await self.register(websocket):
            return
        
        try:
            async for message in websocket:
                global latest_frame, last_frame_time
                with frame_lock:
                    latest_frame = base64.b64encode(message).decode('utf-8')
                    last_frame_time = time.time()
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"处理客户端数据时出错: {e}")
        finally:
            await self.unregister(websocket)

# 创建WebSocket服务器实例
screen_server = ScreenWebSocketServer()

async def screen_websocket_main():
    """启动屏幕客户端的WebSocket服务器"""
    print(f"启动屏幕客户端WebSocket服务器 {WS_HOST}:{WS_PORT}")
    async with websockets.serve(screen_server.handle_client, WS_HOST, WS_PORT, max_size=2**23):
        await asyncio.Future()

async def web_client_main():
    """启动Web客户端的WebSocket服务器"""
    print(f"启动Web客户端WebSocket服务器 {WS_HOST}:{WEB_WS_PORT}")
    
    async def handle_web_client(websocket, path):
        """处理Web客户端连接"""
        print("新的Web客户端连接")
        
        try:
            # 等待认证消息
            auth_message = await websocket.recv()
            auth_data = json.loads(auth_message)
            
            if auth_data.get('type') != 'auth' or auth_data.get('token') != TOKEN:
                await websocket.close(1008, "Invalid token")
                return
                
            # 认证成功，添加到客户端列表
            with web_clients_lock:
                web_clients.append(websocket)
                
            # 发送当前客户端数量
            await websocket.send(json.dumps({
                "type": "client_count",
                "data": len(screen_server.clients)
            }))
            
            print(f"Web客户端认证成功，当前Web客户端数: {len(web_clients)}")
            
            try:
                # 保持连接并处理消息
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        if data.get('type') == 'set_quality':
                            print(f"设置画质: {data.get('quality')}")
                    except json.JSONDecodeError:
                        continue
            except websockets.exceptions.ConnectionClosed:
                pass
            except Exception as e:
                print(f"处理Web客户端消息时出错: {e}")
                
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"Web客户端认证失败: {e}")
        finally:
            with web_clients_lock:
                if websocket in web_clients:
                    web_clients.remove(websocket)
                    print(f"Web客户端断开，当前Web客户端数: {len(web_clients)}")
    
    async with websockets.serve(handle_web_client, WS_HOST, WEB_WS_PORT):
        await asyncio.Future()

async def frame_broadcaster():
    """帧数据广播器 - 将屏幕数据推送给所有Web客户端"""
    global latest_frame
    while True:
        await asyncio.sleep(0.05)  # 20 FPS
        with frame_lock:
            if latest_frame:
                frame_data = json.dumps({
                    "type": "frame",
                    "data": latest_frame
                })
                
                # 发送给所有Web客户端
                with web_clients_lock:
                    for client in web_clients[:]:
                        try:
                            await client.send(frame_data)
                        except:
                            web_clients.remove(client)
                
                latest_frame = None

async def main_async():
    """主异步函数"""
    # 同时启动所有服务
    await asyncio.gather(
        screen_websocket_main(),
        web_client_main(),
        frame_broadcaster()
    )

def start_servers():
    """启动所有服务器"""
    print("=" * 50)
    print("🖥️ 屏幕监控系统服务端")
    print("=" * 50)
    print(f"Web访问地址: http://localhost:{FLASK_PORT}")
    print(f"屏幕客户端端口: {WS_PORT}")
    print(f"Web客户端端口: {WEB_WS_PORT}")
    print(f"访问令牌: {TOKEN}")
    print("=" * 50)
    
    # 启动异步服务
    asyncio.run(main_async())

if __name__ == '__main__':
    # 启动Flask服务器在一个线程中
    import threading
    
    def start_flask():
        app.run(host=FLASK_HOST, port=FLASK_PORT, debug=False, threaded=True, use_reloader=False)
    
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # 在主线程中启动异步服务
    start_servers()
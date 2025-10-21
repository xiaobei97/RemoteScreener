import asyncio
import websockets
import mss
import numpy as np
import cv2
import time
import sys
import os
import json

# 加载配置 - 优化版本
def load_config():
    """加载配置文件，优先使用exe同目录的config.json"""
    # 方法1：尝试exe所在目录的config.json
    exe_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    exe_config_path = os.path.join(exe_dir, 'config.json')
    
    # 方法2：尝试当前工作目录的config.json
    current_config_path = 'config.json'
    
    config_paths = [
        exe_config_path,      # exe同目录
        current_config_path,  # 当前工作目录
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"成功加载配置文件: {config_path}")
                return config
            except Exception as e:
                print(f"读取配置文件失败 {config_path}: {e}")
                continue
    
    # 如果没有找到配置文件，使用默认配置
    print("未找到配置文件，使用默认配置")
    return {
        "server_ip": "127.0.0.1",
        "server_port": 8765,
        "token": "123456",
        "frame_rate": 10,
        "min_frame_rate": 3,
        "max_frame_rate": 20,
        "quality": 80
    }

config = load_config()
SERVER_URI = f"ws://{config['server_ip']}:{config['server_port']}"
TOKEN = config.get('token', '123456')
FRAME_RATE = config.get('frame_rate', 10)
MIN_FRAME_RATE = config.get('min_frame_rate', 3)
MAX_FRAME_RATE = config.get('max_frame_rate', 20)

# 静默运行（Windows下隐藏控制台窗口）
def hide_console():
    if sys.platform == 'win32':
        try:
            import ctypes
            whnd = ctypes.windll.kernel32.GetConsoleWindow()
            if whnd != 0:
                ctypes.windll.user32.ShowWindow(whnd, 0)
        except:
            pass

# 帧率自适应+内部断线重连
async def send_screen():
    global FRAME_RATE
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # 主显示器
        
        while True:
            try:
                # 添加token到请求头
                headers = {
                    'X-Token': TOKEN
                }
                
                async with websockets.connect(SERVER_URI, extra_headers=headers, max_size=2**23, ping_interval=20, ping_timeout=10) as ws:
                    print(f"成功连接到服务器 {SERVER_URI}")
                    
                    while True:
                        start_time = time.time()
                        
                        # 捕获屏幕
                        img = sct.grab(monitor)
                        frame = np.array(img)
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                        
                        # 编码为JPEG
                        ret, buf = cv2.imencode('.jpg', frame, [
                            int(cv2.IMWRITE_JPEG_QUALITY), 
                            config.get('quality', 80)
                        ])
                        
                        if not ret:
                            continue
                            
                        # 发送帧数据
                        await ws.send(buf.tobytes())
                        
                        # 帧率自适应
                        elapsed = time.time() - start_time
                        target_interval = 1.0 / FRAME_RATE
        
                        if elapsed > target_interval and FRAME_RATE > MIN_FRAME_RATE:
                            FRAME_RATE = max(MIN_FRAME_RATE, FRAME_RATE - 1)
                            print(f"降低帧率至: {FRAME_RATE} FPS")
                        elif elapsed < target_interval * 0.7 and FRAME_RATE < MAX_FRAME_RATE:
                            FRAME_RATE = min(MAX_FRAME_RATE, FRAME_RATE + 1)
                            print(f"提高帧率至: {FRAME_RATE} FPS")
                        
                        # 控制帧率
                        sleep_time = max(0, target_interval - elapsed)
                        await asyncio.sleep(sleep_time)
                        
            except websockets.exceptions.InvalidStatusCode as e:
                print(f"连接被拒绝: {e}")
                await asyncio.sleep(5)
            except websockets.exceptions.ConnectionClosed as e:
                print(f"连接关闭: {e}")
                await asyncio.sleep(2)
            except Exception as e:
                print(f"连接错误: {e}")
                await asyncio.sleep(3)

async def main():
    hide_console()
    print("客户端启动中...")
    await send_screen()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("客户端已退出")
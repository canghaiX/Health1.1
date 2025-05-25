import self
from PyAibote import HumanBotMain
import time, os
import subprocess
import threading  # 新增：用于启动HTTP服务器
from http.server import HTTPServer, SimpleHTTPRequestHandler  # 新增：提供HLS文件访问

class CustomWinScript(HumanBotMain):
    Log_Level = "DEBUG"
    Log_Storage = True

    def __init__(self):
        super().__init__()
        self.ffmpeg_proc = None  # 初始化属性
        self.http_server = None

    def script_main(self):
        # 0. 启动HTTP静态文件服务器
        self.start_http_server()

        # 1. 启动HLS转码
        self.start_hls_transcode()

        # 2. 初始化数字人并推流
        rtmp_url = "rtmp://127.0.0.1:8087/live/stream"
        result = self.init_new_metahuman(
            r"G:/PyAibote/NewHuman/model",
            0.4,
            True,
            False,
            rtmp_url
        )
        print("[初始化数字人结果]:", result)

        # 3. 添加背景和语音驱动（保持不变）
        result = self.new_metahuman_add_background(r"G:/PyAibote/NewHuman/background/2.jpg")
        print("背景"+str(result))
        result = self.new_metahuman_audio_to_lab("127.0.0.1:8087", r"G:/PyAibote/NewHuman/testAudio/audio4.wav")
        print("声音" + str(result))
        result = self.new_metahuman_human_speak(r"G:/PyAibote/NewHuman/testAudio/audio4.wav", True)
        print("口型" + str(result))

    def start_http_server(self):
        """启动HTTP服务器提供HLS文件"""
        def server_task():
            server = HTTPServer(('', 8080), SimpleHTTPRequestHandler)
            self.http_server = server
            print("[HTTP服务器] 已启动在端口8080")
            server.serve_forever()

        threading.Thread(target=server_task, daemon=True).start()

    def start_hls_transcode(self):
        """启动FFmpeg转码为HLS格式"""
        try:
            # 确保输出目录存在
            hls_dir = "hls_output"
            if not os.path.exists(hls_dir):
                os.makedirs(hls_dir)

            # 终止旧进程
            os.system("taskkill /IM ffmpeg.exe /F")

            # 启动FFmpeg转码
            self.ffmpeg_proc = subprocess.Popen(
                [
                    'ffmpeg.exe',
                    '-i', 'rtmp://127.0.0.1:8087/live/stream',  # 输入流地址
                    '-c', 'copy',                                # 不重新编码
                    '-f', 'hls',                                 # 输出HLS格式
                    '-hls_time', '4',                            # 分片时长4秒
                    '-hls_list_size', '6',                       # 播放列表保留6个分片
                    '-hls_flags', 'delete_segments',             # 自动删除旧分片
                    f'{hls_dir}/stream.m3u8'                     # 输出路径
                ],
                stdout=open('ffmpeg.log', 'w'),
                stderr=subprocess.STDOUT,
                shell=True
            )
            print(f"[HLS转码] PID:{self.ffmpeg_proc.pid} 已启动")
            print(f"[播放地址] http://127.0.0.1:8080/hls_output/stream.m3u8")
        except Exception as e:
            print(f"[错误] 转码启动失败: {str(e)}")
            self.retry_start()

    def __del__(self):
        """对象销毁时清理资源"""
        try:
            if self.ffmpeg_proc:
                self.ffmpeg_proc.terminate()
            if self.http_server:
                self.http_server.shutdown()
        except AttributeError:
            pass

if __name__ == '__main__':
    CustomWinScript.execute("0.0.0.0", 9999, Debug=True, Qt=None)
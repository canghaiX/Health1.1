import self
from PyAibote import HumanBotMain
import time, os
import subprocess  # 新增：用于启动FFmpeg转码

from flask import Flask
from flask_cors import CORS

app=Flask(__name__)
CORS(app)
class CustomWinScript(HumanBotMain):
    Log_Level = "DEBUG"
    Log_Storage = True

    def script_main(self):
        # 1. 启动本地RTMP服务器（假设使用FFmpeg转发到HTTP-FLV，解决浏览器兼容性问题）
        self.start_http_flv_proxy()

        # 2. 初始化数字人，推流到RTMP服务器
        rtmp_url: str = "rtmp://127.0.0.1/live/stream"
        result = self.init_new_metahuman(
            r"G:/PyAibote/NewHuman/model",
            0.4,
            True,
            False,
            rtmp_url
        )
        print("[初始化数字人结果]:", result)

        # 3. 添加背景和语音驱动
        result=self.new_metahuman_add_background(r"G:/PyAibote/NewHuman/background/2.jpg")
        print("背景"+str(result))
        result=self.new_metahuman_audio_to_lab("127.0.0.1", r"G:/PyAibote/NewHuman/testAudio/audio4.wav")
        print("声音" + str(result))
        result=self.new_metahuman_human_speak(r"G:/PyAibote/NewHuman/testAudio/audio4.wav", True)
        print("口型" + str(result))

    def start_http_flv_proxy(self):
        """启动FFmpeg将RTMP转码为HTTP-FLV，供前端播放"""
        # ffmpeg_cmd = [
        #     'ffmpeg',
        #     '-i', 'rtmp://127.0.0.1/live/stream',  # 输入RTMP流
        #     '-c', 'copy',                          # 直接复制流（不转码）
        #     '-f', 'flv',                           # 输出FLV格式
        #     'http://127.0.0.1:8080/live/stream.flv' # HTTP-FLV输出地址
        # ]
        stream_dir="http://127.0.0.1:80/live/stream.flv"
        ffmpeg_cmd = [
            'ffmpeg.exe',
            '-listen', '1',  # 启用 RTMP 监听模式
            '-timeout', '5000000',  # 超时设为 5 秒（单位：微秒）
            '-i', 'rtmp://127.0.0.1:1935/live/stream',  # 显式指定端口
            '-c', 'copy',  # 禁用转码
            '-f', 'flv',
            '-flvflags', 'no_duration_filesize',  # 忽略文件头校验
            os.path.join(stream_dir, 'stream.flv')  # 完整输出路径
        ]
        # 在后台启动FFmpeg进程
        subprocess.Popen(ffmpeg_cmd, shell=True, stderr=subprocess.DEVNULL)
        print("[FFmpeg转码已启动] RTMP → HTTP-FLV")

    # def start_http_flv_proxy(self):
    # #"""改进的 FFmpeg 启动方法（Windows 兼容）"""
    #     try:
    #         # 终止旧进程
    #         os.system("taskkill /IM ffmpeg.exe /F")
    #
    #         # 启动新进程（带错误重试）
    #         self.ffmpeg_proc = subprocess.Popen(
    #             [
    #                 'ffmpeg.exe',
    #                 '-i', 'rtmp://127.0.0.1/live/stream',
    #                 '-c', 'copy',
    #                 '-f', 'flv',
    #                 'http://127.0.0.1:80/live/stream.flv'
    #             ],
    #             stdout=open('ffmpeg.log', 'w'),
    #             stderr=subprocess.STDOUT,
    #             shell=True  # Windows 必须启用 shell
    #         )
    #         print(f"[FFmpeg PID:{self.ffmpeg_proc.pid}] 转码进程已启动")
    #     except Exception as e:
    #         print(f"启动失败: {str(e)}")
    #         self.retry_start()  # 添加重试逻辑

if __name__ == '__main__':
    # 确保端口9999未被占用，启动脚本
    CustomWinScript.execute("0.0.0.0", 9999, Debug=True, Qt=None)
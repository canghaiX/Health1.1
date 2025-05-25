from PyAibote import HumanBotMain
import time, os
import subprocess

class CustomWinScript(HumanBotMain):
    Log_Level = "DEBUG"
    Log_Storage = True

    def script_main(self):
        # 启动FFmpeg推流进程（捕获整个桌面）
        ffmpeg_cmd = [
            r'G:/PyAibote/ffmpegFull/bin/ffmpeg.exe',
            '-f', 'gdigrab',
            '-framerate', '30',
            '-i', 'desktop',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-f', 'flv',
            'rtmp://127.0.0.1/live/stream'
        ]
        self.ffmpeg_process = subprocess.Popen(ffmpeg_cmd)
        #rtmp://your_server_ip/live/stream


        rtmp_url = "rtmp://127.0.0.1/live/stream"
        # 初始化数字人（确认是否需要关闭内置推流）
        result = self.init_new_metahuman(
            r"G:/PyAibote/NewHuman/model",
            0.4,
            False,
            False,
            ""  # 如果使用外部FFmpeg则留空RTMP地址
        )
        print("数字人初始化结果:", result)

        # ... 其他原有代码 ...

    def __del__(self):
        # 确保退出时关闭FFmpeg进程
        if hasattr(self, 'ffmpeg_process'):
            self.ffmpeg_process.terminate()

if __name__ == '__main__':
    CustomWinScript.execute("127.0.0.1", 9999, Debug=True, Qt=None)
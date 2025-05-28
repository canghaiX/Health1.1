# 1. 导入 WinBotMain 类
import time

from PyAibote import WinBotMain
import subprocess
import signal
import os
from flask import Flask
from flask_cors import CORS
app=Flask(__name__)
CORS(app)
class CustomWinScript(WinBotMain):
    Log_Level = "DEBUG"
    Log_Storage = True
    ffmpeg_proc = None  # FFmpeg进程句柄

    def script_main(self):
        #self.start_http_flv_proxy()
        # rtmp_url: str = "rtmp://127.0.0.1/live/stream"
        # result = self.init_metahuman(
        #     "../NewHuman/model",
        #     0.4,
        #     True,
        #     False,
        #     rtmp_url
        # )
        # print("[初始化数字人结果]:", result)
        # 初始化语音服务
        # 启动视频推流服务

        self.init_speech_service("CmwzTb35WSvnOYEPoY9wC12ExtiNJkI37VJlc9itceLmM6osBYstJQQJ99BAACYeBjFXJ3w3AAAYACOG1fhO", "eastus")

        # 初始化数字人
        self.init_metahuman("../humanModel/humanModel2", 0.5, 0.5, False, False)
        self.replace_background("../NewHuman/background/2.jpg", -1, -1, -1, 50)
        self.start_stream_service()
        # 主交互循环
        from openai import OpenAI
        client = OpenAI(
            api_key='sk-7548be9550ca4f15a8b211deddbfc9e3',
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        while True:
            try:

                print("请说话:")
                user_input = self.microphone_to_text("zh-cn")
                print(user_input)

                # 生成回复
                print("completion启动")
                completion = client.chat.completions.create(
                    model="qwen2.5-32b-instruct",  # 您可以按需更换为其它深度思考模型
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_input},
                    ],
                )


                print("completion完成")
                response = completion.choices[0].message.content
                print(response)
                # 数字人交互
                self.show_speech_text(0, "楷体", 20, 128, 255, 0, False, False)
                self.metahuman_speech("../voice/2.mp3", response, "zh-cn", "zh-cn-XiaochenNeural", 0, True, 0,
                                      "General")

            except Exception as e:
                print("交互异常:", str(e))

    def start_stream_service(self):
        """启动FFmpeg将RTMP转码为HTTP-FLV，供前端播放"""
        # ffmpeg_cmd = [
        #     'ffmpeg',
        #     '-i', 'rtmp://127.0.0.1/live/stream',  # 输入RTMP流
        #     '-c', 'copy',                          # 直接复制流（不转码）
        #     '-f', 'flv',                           # 输出FLV格式
        #     'http://127.0.0.1:8080/live/stream.flv' # HTTP-FLV输出地址
        # ]
        stream_dir = "http://127.0.0.1:80/live/stream.flv"
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


    def stop_stream_service(self):
        """停止推流服务"""
        if self.ffmpeg_proc:
            self.ffmpeg_proc.send_signal(signal.CTRL_C_EVENT)
            self.ffmpeg_proc.kill()
            self.ffmpeg_proc = None
            print("FFmpeg推流已停止")

    def __del__(self):
        """对象销毁时清理资源"""
        self.stop_stream_service()


if __name__ == '__main__':
    CustomWinScript.execute("0.0.0.0", 9999, Debug=True)
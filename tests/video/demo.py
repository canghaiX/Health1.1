# 1. 导入 HumanBotMain 类
# 1. Import HumanBotMain class
from PyAibote import HumanBotMain
import time, os
import subprocess  # 新增：用于启动FFmpeg转码
# import ffmpeg


# 2. 自定义一个脚本类，继承 HumanBotMain
# 2. Customize a script class and inherit HumanBotMain.
class CustomWinScript(HumanBotMain):
    # 2.1. 设置是否终端打印输出 DEBUG：输出， INFO：不输出, 默认打印输出
    # 2.1. Set whether the terminal prints output DEBUG: output, INFO: no output, and print output by default.
    Log_Level = "DEBUG"

    # 2.2. 终端打印信息是否存储LOG文件 True： 储存， False：不存储
    # 2.2. Does the terminal print information store the LOG file? True: yes, False: no.
    Log_Storage = True

    # 2.3. 注意：script_main 此方法是脚本执行入口必须存在此方法
    # 2.3. Note: script_main This method must exist in the script execution portal.
    def script_main(self):
        # 初始化数字人 [测试基础模型在环境包中]   [这些地址需要修改为本地对应地址] [127.0.0.1修改为推流ip地址]
        result = self.init_new_metahuman(r"G:\PyAibote\NewHuman\model", 0.4,
                                         False, False,
                                         "rtmp://127.0.0.1/live/stream")
        print("初始化数字人形象"+str(result))

        # 切换数字人形象 
        # self.new_metahuman_switch_action(r"D:\Project\Static\Img\666.mp4", 0.5, False, False)

        # 添加数字人背景
        result = self.new_metahuman_add_background(r"G:/PyAibote/NewHuman/background/2.jpg")
        print("调节数字人背景"+str(result))

        # 生成lab文件 [嘴型]
        result = self.new_metahuman_audio_to_lab("127.0.0.1", r"G:/PyAibote/NewHuman/testAudio/audio1.wav")
        print("嘴型"+str(result))

        # 数字人说话
        result = self.new_metahuman_human_speak(r"G:/PyAibote/NewHuman/testAudio/audio1.wav", True)
        print("数字人说话"+str(result))

        # 语音识别
        # result = self.clone_audio_to_text("127.0.0.1", "")
        # print(result)

        # 关闭驱动 方法一
        # os.popen('taskkill /f /t /im  "AiDriver.exe"')

        # 关闭驱动 方法二  终端直接输入
        # taskkill /f /t /im  "AiDriver.exe"

    # def start_http_flv_proxy(self):
    #     """启动FFmpeg将RTMP转码为HTTP-FLV，供前端播放"""
    #     ffmpeg_cmd = [
    #         'ffmpeg',
    #         '-i', 'rtmp://127.0.0.1/live/stream',  # 输入RTMP流
    #         '-c', 'copy',                          # 直接复制流（不转码）
    #         '-f', 'flv',                           # 输出FLV格式
    #         'http://127.0.0.1:8080/live/stream.flv' # HTTP-FLV输出地址
    #     ]
    #     # 在后台启动FFmpeg进程
    #     subprocess.Popen(ffmpeg_cmd, shell=True, stderr=subprocess.DEVNULL)
    #     print("[FFmpeg转码已启动] RTMP → HTTP-FLV")
if __name__ == '__main__':
    # 3. IP为:0.0.0.0, 监听 9999 号端口
    # 3. IP: 0.0.0, listening to port 9999.
    # 3.1. 在远端部署脚本时，请设置 Debug=False，客户端手动启动 WindowsDriver.exe 时需指定远端 IP 或端口号
    # 3.1. When deploying the script remotely, please set Debug=False, and the client needs to specify the remote IP or port number when manually starting the WindowsDriver.exe.
    # 3.2. 命令行启动示例：AiDriver.exe "127.0.0.1" 9999
    # 3.2. Command line startup example: AiDriver.exe "127.0.0.1" 9999
    # 3.3 Qt 使用线程启动时传递的Qt对象用来和Qt UI窗口通信
    # 3.3 Qt Use the Qt object passed when the Qt thread starts to communicate with the Qt UI window
    CustomWinScript.execute("0.0.0.0", 9999, Debug=True, Qt=None)
# (ffmpeg.input('desktop', format='gdigrab', framerate=30)
#  .output('rtmp://127.0.0.1/streamkey', vcodec='libx264', preset='ultrafast', f='flv')
#  .run_async())

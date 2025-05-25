# 1. 导入 WinBotMain 类
from PyAibote import WinBotMain
import time,os

# 2. 自定义一个脚本类，继承 WinBotMain
class CustomWinScript(WinBotMain):

    # 2.1. 设置是否终端打印输出 DEBUG：输出， INFO：不输出, 默认打印输出
    Log_Level = "DEBUG"

    # 2.2. 终端打印信息是否存储LOG文件 True： 储存， False：不存储
    Log_Storage = True

    # 2.3. 注意：script_main 此方法是脚本执行入口必须存在此方法
    def script_main(self):
        # 查询所有窗口句柄
        # result = self.find_windows()
        # print(result)

        # 初始化语音服务
        result = self.init_speech_service("CmwzTb35WSvnOYEPoY9wC12ExtiNJkI37VJlc9itceLmM6osBYstJQQJ99BAACYeBjFXJ3w3AAAYACOG1fhO", "eastus")
        print(result)

        # 数字人初始化
        result = self.init_metahuman("../humanModel/humanModel2", 0.5, 0.5, False, False)
        print(result)

        # 替换数字人背景
        result = self.replace_background("../NewHuman/background/2.jpg", -1, -1, -1, 50)
        print(result)


        from openai import OpenAI
        import os

        # 初始化OpenAI客户端
        client = OpenAI(
            api_key='sk-7548be9550ca4f15a8b211deddbfc9e3',
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )

        messages = [{"role": "user", "content": "你是谁"}]
        while(1):
            print("请说话:")

            # 麦克风输入流转换文本
            user_input = self.microphone_to_text("zh-cn")
            print(user_input)

            # 文心一言chatgpt
            # output = self.wen_xin_bot("F6Wr5YuqrbAT8MunFXpbGCaw", "Pbb2oW5XiEihOLjPWbAwjqdWtm7Xbrjd", input)
            # print(output['result'])


            completion = client.chat.completions.create(
                model="qwen2.5-32b-instruct",  # 您可以按需更换为其它深度思考模型
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input},
                ],
            )

            print(completion.choices[0].message.content)



            # 显示数字人说话的文本
            result = self.show_speech_text(0, "楷体", 20, 128, 255, 0, False, False)
            print(result)

            # 数字人说话
            result = self.metahuman_speech("../humanModel/humanModel2/voice/2.mp3", completion.choices[0].message.content, "zh-cn", "zh-cn-XiaochenNeural", 0, True, 0, "General")
            print(result)

        # # 自动关闭
        # time.sleep(60000)
        # self.close_driver_local()

if __name__ == '__main__':
    # 3. IP为:0.0.0.0, 监听 9999 号端口
    # 3.1. 在远端部署脚本时，请设置 Debug=False，客户端手动启动 WindowsDriver.exe 时需指定远端 IP 或端口号
    # 3.2. 命令行启动示例： WindowsDriver.exe "127.0.0.1" 9999 {'Name':'PyAibote'}
    CustomWinScript.execute("0.0.0.0", 9999, Debug=True)
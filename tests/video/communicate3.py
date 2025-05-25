# 1. 导入 WinBotMain 类

from PyAibote import WinBotMain
import time,os
import re
from openai import OpenAI
import json
# 2. 自定义一个脚本类，继承 WinBotMain
class CustomWinScript(WinBotMain):

    # 2.1. 设置是否终端打印输出 DEBUG：输出， INFO：不输出, 默认打印输出
    Log_Level = "DEBUG"

    # 2.2. 终端打印信息是否存储LOG文件 True： 储存， False：不存储
    Log_Storage = True
    question_list = [
        '第一个问题，在社会科学的分类中，既然哲学社会科学具有双重属性且常与人文社会科学概念混用，那么我们应该如何清晰界定它们之间的区别和联系，并在研究中准确运用这些概念呢？',
        '第二个问题，社会科学研究方法论包含方法论、研究方式和具体方法与技术三个层次，那么在实际研究中，我们应如何确保这三个层次的协调统一，以提高研究的科学性和有效性？',
        '第三个问题，面对马克思主义在中国化进程中取得的成绩以及面临的西方意识形态渗透挑战，我们应当如何在坚持马克思主义基本原理的基础上，积极应对并化解这些挑战，推动马克思主义在中国的新发展？',
        '第四个问题，在社会系统研究方法中，既然社会被视为复杂大系统，那么我们在进行矛盾分析时应如何平衡好矛盾普遍性与特殊性的关系以促进社会和谐发展？',
        '第五个问题，学术论文选题的原则之一是创新性，但在尊重著作权保护、避免学术不端行为的前提下，我们怎样才能做到既保证选题的创新性又遵循学术规范？']

    # 添加存储学生回答的列表
    student_answer_list = []

    # 2.3. 注意：script_main 此方法是脚本执行入口必须存在此方法
    def script_main(self):
        # 语音服务初始化
        result = self.init_speech_service("CmwzTb35WSvnOYEPoY9wC12ExtiNJkI37VJlc9itceLmM6osBYstJQQJ99BAACYeBjFXJ3w3AAAYACOG1fhO", "eastus")
        print(result)

        # 数字人初始化
        result = self.init_metahuman("E:/humanModel2", 0.5, 0.5, False, False)
        print(result)

        # 显示数字人说话文本
        result = self.show_speech_text(0, "Arial", 30, 128, 255, 0, False, False)
        print(result)

      
        try:
            for i in range(len(self.question_list)):
                # 数字人读出问题
                result = self.metahuman_speech("E:/humanModel2/voice/1.mp3",
                                           self.question_list[i], "zh-cn", "zh-cn-XiaochenNeural",
                                           0, True, 0, "General")
                print(f"问题 {i+1}: {self.question_list[i]}")
                
                print("请说出您的答案...(说回答完毕结束回答)")
                answer_parts = []
                while True:
                    try:
                        current_answer = self.microphone_to_text("zh-cn")
                        if current_answer and current_answer.strip() != "":
                            # 先检查是否包含"回答完毕"
                            if "回答完毕" in current_answer:
                                # 移除"回答完毕"这几个字
                                current_answer = current_answer.replace("回答完毕", "").strip()
                                if current_answer:  # 如果除了"回答完毕"还有其他内容
                                    answer_parts.append(current_answer)
                                    print("回答结束，正在保存...")
                                    break
                            else:
                                print(f"当前录音内容: {current_answer}")
                                answer_parts.append(current_answer)
                                print("继续回答...")
                        else:
                            print("未检测到回答，请继续...")
                            time.sleep(1)
                    except Exception as e:
                        print(f"录音出错，请重试: {str(e)}")
                        time.sleep(1)
                
                # 将所有回答部分合并成完整答案
                complete_answer = " ".join(answer_parts)
                self.student_answer_list.append(complete_answer)
                print(f"已记录第 {i+1} 个问题的回答")
                time.sleep(2)
                
            print("所有问题已回答完毕！")
            print("答案列表：", self.student_answer_list)
            
        except Exception as e:
            print(f"发生错误: {str(e)}")
        finally:
            self.close_driver_local()

if __name__ == '__main__':
    # 3. IP为:0.0.0.0, 监听 9999 号端口
    # 3.1. 在远端部署脚本时，请设置 Debug=False，客户端手动启动 WindowsDriver.exe 时需指定远端 IP 或端口号
    # 3.2. 命令行启动示例： WindowsDriver.exe "127.0.0.1" 9999 {'Name':'PyAibote'}
    CustomWinScript.execute("0.0.0.0", 9999, Debug=True)
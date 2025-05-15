#处理雷达波数据
#2025.5.14 21.25:目前的类只包含了将雷达波数据结论摘取出来的逻辑，还需要对雷达波数据是否异常进行判断的逻辑，来决定是否触发主动问答。
class HealthDataProcessor:
    def __init__(self, json_data):
        self.json_data = json_data
        self.error_messages = {
            "invalid_format": "错误：数据格式不符合预期",
            "invalid_status": "错误：检查未成功完成"
        }

    def process(self):
        """处理健康检查数据，返回关键结论或错误信息"""
        try:
            # 验证顶层结构
            if not self._validate_top_level():
                return self.error_messages["invalid_format"]
            
            # 验证数据状态
            if not self._validate_status():
                return self.error_messages["invalid_status"]
            
            # 提取并拼接结论
            return self._extract_conclusions()
            
        except (KeyError, TypeError, ValueError) as e:
            return f"错误：{str(e)}"

    def _validate_top_level(self):
        """验证顶层JSON结构是否有效"""
        return (
            isinstance(self.json_data, dict) and
            "data" in self.json_data and
            isinstance(self.json_data["data"], dict)
        )

    def _validate_status(self):
        """验证检查状态是否成功"""
        data = self.json_data["data"]
        return (
            data.get("success") == 1 and
            data.get("errorCode") == 0
        )

    def _extract_conclusions(self):
        """提取并拼接最终结论"""
        conclusion = self.json_data["data"].get("conclusion", {})
        heart = conclusion.get("heartConclusion", "")
        breath = conclusion.get("breathConclusion", "")
        combined = "\n".join([s.strip() for s in [heart, breath] if s])
        return combined if combined else self.error_messages["invalid_format"]

# 使用示例
if __name__ == "__main__":
    # 测试数据
    sample_data = {
  "success": "true",
  "failReason": "null",
  "data": {
    "success": 1,
    "errorCode": 0,
    "csgCollectId": "a8afa745-819c-46a0-aea3-02cfd4de3884",
    "person": {
      "name": "hsap",
      "sex": "Male",
      "age": 26
    },
    "startTime": "1745819347505",
    "endTime": "1745819407505",
    "heartRate": 76,
    "conclusion": {
      "heartConclusion": "在此次检查中：\n您的平均心率 76 次/分钟，房颤发生概率 0%，早搏发生概率 75%，心动过速发生概率 0%，心动过缓发生概率 0%，心律不齐发生概率 44%，心脏收缩时间间期(PEP/LVET)为 0.0，心电波形(QRS)时限 - 毫秒，(QT)间期 - 毫秒，心率变异性(rMSSD)为 29.48 毫秒，LF/HF为1.02 毫秒。\n此段心电图疑似早搏；若出现心悸、气短、胸闷、眩晕等症状，请咨询医生做进一步检查。",
      "breathConclusion": "您的平均呼吸率 16 次/分钟，平均呼吸深度 9.0 毫米，呼气吸气比 5.73 。\n呼吸较深；若出现呼吸不畅、喘不上气、呼吸困难、头晕恶心等症状，请咨询医生做进一步检查。"
    },
    "sti": 0.0,
    "hrvFeature": {
      "sdnn": 25.753937,
      "rmssd": 29.48272,
      "pnn50": 0.46153846,
      "cvsd": 0.03916111,
      "cvcdi": 0.034208268,
      "lf": 273.5398,
      "hf": 267.2555,
      "lfHfRatio": 1.0235142
    },
    "breathFeature": {
      "breathRate": 16,
      "avgBreathDepth": 9.00252,
      "maxBreathDepth": 45.28404,
      "minBreathDepth": 1.2028135,
      "expiratoryTime": 825,
      "inspiratoryTime": 4725
    }
  }
}

    processor = HealthDataProcessor(sample_data)
    result = processor.process()
    print(result)    

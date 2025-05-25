#处理雷达波数据
#2025.5.14 21.25:目前的类只包含了将雷达波数据结论摘取出来的逻辑，还需要对雷达波数据是否异常进行判断的逻辑，来决定是否触发主动问答。
class HealthDataProcessor:
    def __init__(self, json_data):
        self.json_data = json_data
        self.error_messages = {
            "invalid_format": "错误：数据格式不符合预期",
            "invalid_status": "错误：检查未成功完成"
        }
        self.anomalies = []
        self.normal_ranges = {
            # 时域指标
            'rmssd': {'low': 8.46, 'high': 130.46, 'unit': '毫秒'},
            'sdnn': {'low': 12.05, 'high': 154.69, 'unit': '毫秒'},
            'pnn50': {'low': 0.21, 'high': 57.50, 'unit': '%'},
            'lf': {'low': 8.46, 'high': 130.46, 'unit': 'ms2'},
            'hf': {'low': 5.0, 'high': 93.8, 'unit': 'ms2'},
            'lfHfRatio': {'low': 0.66, 'high': 1.55, 'unit': 'C.U'},
            # 呼吸指标
            'breathRate': {'low': 12, 'high': 20, 'unit': '次/分钟'},
            'avgBreathDepth': {'low': 5.0, 'high': 15.0, 'unit': '毫米'},
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
    #以下为雷达波异常判断部分，异常会返回False
    def is_health_data_normal(self):
        """检查健康数据是否全部正常"""
        try:
            if not self._validate_top_level():
                return self.error_messages["invalid_format"]
            if not self._validate_status():
                return self.error_messages["invalid_status"]
            #判定是否异常，异常会返回false
            self.anomalies = []
            self._check_hrv_features()
            self._check_breath_features()
            self._check_conclusions()
            return len(self.anomalies) == 0 
        except (KeyError, TypeError, ValueError) as e:
            return f"错误：{str(e)}"

    def get_anomalies(self):
        """获取详细异常信息"""
        return self.anomalies

    def _check_hrv_features(self):
        hrv = self.json_data.get('data', {}).get('hrvFeature', {})
        for key, ranges in self.normal_ranges.items():
            if key in hrv:
                value = hrv[key]
                if not (ranges['low'] <= value <= ranges['high']):
                    self._add_anomaly(
                        key.upper() if key in ['rmssd', 'sdnn'] else key.title(),
                        value,
                        f'超出正常范围 ({ranges["low"]}-{ranges["high"]} {ranges["unit"]})'
                    )

    def _check_breath_features(self):
        breath = self.json_data.get('data', {}).get('breathFeature', {})
        for key, ranges in self.normal_ranges.items():
            if key in breath:
                value = breath[key]
                if not (ranges['low'] <= value <= ranges['high']):
                    display_key = key.replace('avg', 'Avg ').title()
                    self._add_anomaly(
                        display_key,
                        value,
                        f'超出正常范围 ({ranges["low"]}-{ranges["high"]} {ranges["unit"]})'
                    )

    def _check_conclusions(self):
        conclusion = self.json_data.get('data', {}).get('conclusion', {})
        heart_conclusion = conclusion.get('heartConclusion', '')
        breath_conclusion = conclusion.get('breathConclusion', '')
        
        if "疑似" in heart_conclusion or "异常" in heart_conclusion:
            self._add_anomaly('心脏结论', '异常', heart_conclusion)
        
        if "异常" in breath_conclusion or "较深" in breath_conclusion:
            self._add_anomaly('呼吸结论', '异常', breath_conclusion)

    def _add_anomaly(self, indicator, value, reason):
        self.anomalies.append({
            '指标': indicator,
            '值': value,
            '异常原因': reason
        })

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

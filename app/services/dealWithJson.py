import json
def json_test():
    data={"会员号":13962989897.0,"姓名":"卢俊","性别":"男","出生日期":"1968-9-1",
      "身高 (cm)":174.0,"体重 (kg)":75.0,"检查日期":"2017-05-16","检查时间":"15:41","钠":"标准",
      "钾":"-10","氯":"标准","镁":"标准","钙":"标准","磷":"6","铁":"标准","PH":7.29,"HCO3-":23.8,
      "PaCO2":53.2,"PaO2":None,"[H+]":53.65,"SBE":0.0,"iSO2":96.0,"间质的过氧亚硝酸自由基":0.0,
      "间质的小分子自由基":0.0,"间质的过氧化氢自由基":0.0,"间质的超氧阴离子自由基":0.0,"间质的羟自由基":0.0,
      "五羟色胺":0.0,"多巴胺":-10.0,"儿茶酚胺":10.0,"乙酰胆碱":-20.0,"间质的甘油三酯":0.0,
      "谷草转氨酶AST\/谷丙转氨酶ALT":5.0,"碱性磷酸酶ALP和转肽酶GGT":0.0,"间质的血糖":0.0,
      "间质的LDL低密度脂蛋白":0.0,"间质的促甲状腺激素":-15.0,"间质的促卵泡激素":0.0,"间质的脱氢表雄酮":0.0,
      "间质的皮质醇":0.0,"醛固酮":27.0,"肾上腺髓质激素分泌量":37.0,"间质的睾丸激素":3.0,"胰岛素分泌量":2.0,
      "甲状旁腺激素分泌量":-15.0,"甲状腺激素分泌量":15.0,"间质的抗利尿激素":10.0,"间质的促肾上腺皮质激素":0.0,
      "呼吸系统的当前状态":None,"呼吸系统的当前状态-说明":"呼吸器官疾病(支气管炎、气喘或是耳鼻喉炎症)的可能性\r\n换气不足\r\n血碳酸偏高",
      "消化系统的当前状态":None,"消化系统的当前状态-说明":"消化器官出现问题的可能性","免疫系统的当前状态":None,
      "免疫系统的当前状态-说明":"自身免疫性疾病的倾向 \r\n \r\n免疫球蛋白轻度增加，例如IgG\r\n \r\n  19  胸腺",
      "泌尿生殖系统和肾脏的当前状态":None,"泌尿生殖系统和肾脏的当前状态-说明":"肾功能轻度改变","骨骼系统的当前状态":None,
      "骨骼系统的当前状态-说明":"骨关节功能改变导致脊椎阻滞而引起的疼痛\r\n左臂的神经肌肉过分兴奋的风险\r\n右臂的神经肌肉过分兴奋的风险",
      "心血管系统的当前状态":None,"心血管系统的当前状态-说明":"植物神经系统或下丘脑引起血压变化的倾向",
      "内分泌系统的当前状态":None,"内分泌系统的当前状态-说明":"肾上腺皮质功能轻度变化\r\n甲状腺机能亢进\r\n醛固酮分泌轻度变化","神经系统的当前状态":None,
      "神经系统的当前状态-说明":"压力过大的可能性\r\n植物神经系统失调的可能","自由基水平状态":None,"自由基水平状态-说明":None,
      "过敏的当前状态":None,"过敏的当前状态-说明":None,"内环境和基础代谢状况":None,
      "内环境和基础代谢状况-说明":"应激引起的内环境不平衡状态\r\n组织含氧量降低和血液携氧能力下降\r\n水分潴留",
      "耳鼻喉的当前状态":None,"耳鼻喉的当前状态-说明":None,"皮肤的当前状态":None,"皮肤的当前状态-说明":None,
      "细胞变性的当前状态":None,"细胞变性的当前状态-说明":None,"感染的当前状态":None,"感染的当前状态-说明":None,
      "气管附近":37.0,"支气管区域":37.0,"左肺上叶区域":2.0,"左肺下叶区域":-15.0,"右肺上叶区域":8.0,"右肺中叶区域":-17.0,
      "右肺下叶区域":None,"胸部左侧区域":11.0,"胸部右侧区域":12.0,"食道上段":37.0,"食道下段":-4.0,"胃区域":21.0,
      "十二指肠区域":21.0,"小肠区域":-16.0,"盲肠和阑尾区域":-9.0,"升结肠区域":-9.0,"结肠肝区":-8.0,"结肠脾区":-10.0,"降结肠区域":-24.0,
      "乙状结肠区域":-24.0,"直肠区域":-17.0,"肝左叶及胆管区域":-12.0,"肝右页":12.0,"胆囊区域":-4.0,"胰腺区域":-8.0,"胸腺":19.0,"脾脏区域":3.0,
      "左肾及输尿管区域":-24.0,"右肾及输尿管区域":21.0,"膀胱区域":-17.0,"前列腺区域":None,"左睾丸区域":-24.0,"右睾丸区域":-9.0,"左卵巢":None,"右卵巢":None,
      "左眼和泪腺区域":10.0,"右眼和泪腺区域":5.0,"左上颌窦区域":11.0,"右上颌窦区域":16.0,"右侧鼻前庭和固有鼻腔区域":26.0,"左侧鼻前庭和固有鼻腔区域":20.0,
      "左唾液腺":0.0,"右唾液腺":0.0,"左耳区域":7.0,"右耳区域":18.0,"左侧额叶皮层":14.0,"右侧额叶皮层":15.0,"左侧颞叶":4.0,"右侧颞叶":14.0,"垂体区域":7.0,
      "下丘脑区域":21.0,"丘脑":27.0,"左杏仁体":-4.0,"右杏仁体":-14.0,"左侧边缘系统（海马）":14.0,"右侧边缘系统（海马）":4.0,"左侧颅内血管":14.0,"右侧颅内血管":15.0,
      "左侧肾上腺髓质":41.0,"右侧肾上腺髓质":47.0,"甲状腺区域":42.0,"甲状腺左叶区域":33.0,"甲状腺右叶区域":33.0,"左侧颈部区域":0.0,"右侧颈部区域":0.0,"左横隔膜神经区":20.0,
      "右侧膈神经区域":23.0,"左膝区域（腿部血管）":-24.0,"右膝区域（腿部血管）":18.0,"左大腿神经血管束":-24.0,"右大腿神经血管束":18.0,"左小腿神经血管束":-24.0,
      "右小腿神经血管束":18.0,"左手神经血管束":35.0,"右手神经血管束":40.0,"左上臂神经血管束":35.0,"右上臂神经血管束":40.0,"左前臂神经血管束":35.0,
      "右前臂神经血管束":40.0,"左脚神经血管束":-24.0,"右脚神经血管束":18.0,"心脏区域":3.0,"左颈动脉":40.0,"右颈动脉":48.0,"上腔静脉":-2.0,
      "下腔静脉":0.0,"左前庭压力感受器":25.0,"右前庭压力感受器":30.0,"主动脉":-6.0,"冠状血管":19.0,"心肺循环":19.0,"门脉循环":32.0,"心肌":10.0,
      "左心室":-15.0,"右心室":-2.0,"C1":8.0,"C2":8.0,"C3":8.0,"C4":18.0,"C5":28.0,"C6":33.0,"C7":33.0,"C8":37.0,"Th1":36.0,"Th2":33.0,
      "Th3":33.0,"Th4":11.0,"Th5":11.0,"Th6":11.0,"Th7":11.0,"Th8":11.0,"Th9":11.0,"Th10":11.0,"Th11":17.0,"Th12":17.0,"L1":11.0,"L2":-16.0,
      "L3":-16.0,"L4":-1.0,"L5":-1.0,"S1":-16.0,"S2":-16.0,"S3":-16.0,"S4":-17.0,"S5":-17.0,"Co1":-17.0,
      "人体成分分析及建议":"BMI（基础代谢）: 24.77\r\n理想体重 65.09 kg\r\n瘦重(去脂重): 27%\r\n体脂重量 : 8%\r\n建议每日总卡路里 2591",
      "推荐饮食":None}
    str=""
    data1=[]
    data1.append(data["身高 (cm)"])
    data1.append(data["体重 (kg)"])
    #第一部分
    str+=json_demo1(data,data1)
    #第二部分
    str+=json_demo2(data,data1)
    str+= json_demo3(data, data1)
    str+= json_demo4(data, data1)
    str += json_demo5(data, data1)
    str += json_demo6(data, data1)
    str += json_demo7(data, data1)
    str += json_demo8(data, data1)
    str += json_demo9(data, data1)
    str += json_demo10(data, data1)
    str += json_demo11(data, data1)
    str += json_demo12(data, data1)
    str += json_demo13(data, data1)
    str += json_demo14(data, data1)
    str += json_demo15(data, data1)
    str += json_demo16(data, data1)
    print(str)
    print(data1)
    # print(data["会员号"])


def json_demo1_test(data,str1,data1):
  if (data[str1] == "标准"or(int(data[str1])>=-5 and int(data[str1])<=5)):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""
def json_demo1(data,data1):
  str=""
  str += json_demo1_test(data, "钠", data1)
  str += json_demo1_test(data, "钾", data1)
  str += json_demo1_test(data, "氯", data1)
  str += json_demo1_test(data, "镁", data1)
  str += json_demo1_test(data, "钙", data1)
  str += json_demo1_test(data, "磷", data1)
  str += json_demo1_test(data, "铁", data1)
  return str
def json_demo2(data,  data1):
  str=""
  if (data["PH"]>=7.29 and data["PH"]<=7.37):
    str+="您的PH含量正常\r\n"
  else:
    data1.append({"PH": data["PH"]})
  if (data["HCO3-"]>=22 and data["HCO3-"]<=26):
    str+="您的HCO3含量正常\r\n"
  else:
    data1.append({"HCO3": data["HCO3-"]})
  if (data["PaCO2"]>=41 and data["PaCO2"]<=51):
    str+="您的PaCO2含量正常\r\n"
  else:
    data1.append({"PaCO2": data["PaCO2"]})
  if (data["[H+]"]>=42.6 and data["[H+]"]<=51.3):
    str+="您的[H+]含量正常\r\n"
  else:
    data1.append({"[H+]": data["[H+]"]})
  if (data["SBE"]>=-2 and data["SBE"]<=2):
    str+="您的SBE含量正常\r\n"
  else:
    data1.append({"SBE": data["SBE"]})
  if (data["iSO2"]>=95.00):
    str+="您的iSO2含量正常\r\n"
  else:
    data1.append({"iSO2": data["iSO2"]})

  return str

def json_demo3_test(data,str1,data1):
  if (data[str1] <=10):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""

def json_demo3(data, data1):
    str = ""
    str += json_demo3_test(data, "间质的过氧亚硝酸自由基", data1)
    str += json_demo3_test(data, "间质的小分子自由基", data1)
    str += json_demo3_test(data, "间质的过氧化氢自由基", data1)
    str += json_demo3_test(data, "间质的超氧阴离子自由基", data1)
    str += json_demo3_test(data, "间质的羟自由基", data1)
    return str

def json_demo4_test(data,str1,data1):
  if (data[str1] <=10):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""

def json_demo4(data, data1):
  str = ""
  if (data["五羟色胺"] <= 10 and data["五羟色胺"]>=-10):
    str+="您的五羟色胺含量正常\r\n"
  else:
    data1.append({"五羟色胺": data["五羟色胺"]})
    str+= ""
  str += json_demo3_test(data, "多巴胺", data1)
  str += json_demo3_test(data, "儿茶酚胺", data1)
  str += json_demo3_test(data, "乙酰胆碱", data1)
  return str
def json_demo5_test(data,str1,data1):
  if (data[str1] <=5 and data[str1]>=-5):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""

def json_demo5(data, data1):
    str = ""
    str += json_demo5_test(data, "间质的甘油三酯", data1)
    str += json_demo5_test(data, "谷草转氨酶AST\/谷丙转氨酶ALT", data1)
    str += json_demo5_test(data, "碱性磷酸酶ALP和转肽酶GGT", data1)
    str += json_demo5_test(data, "间质的血糖", data1)
    str += json_demo5_test(data, "间质的LDL低密度脂蛋白", data1)
    return str
def json_demo6_test(data,str1,data1):
  if (data[str1] <=20 and data[str1]>=-20):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""
def json_demo6(data, data1):
    str = ""
    str += json_demo6_test(data, "间质的促甲状腺激素", data1)
    str += json_demo6_test(data, "间质的促卵泡激素", data1)
    str += json_demo6_test(data, "间质的脱氢表雄酮", data1)
    str += json_demo6_test(data, "间质的皮质醇", data1)
    str += json_demo6_test(data, "醛固酮", data1)
    str += json_demo6_test(data, "肾上腺髓质激素分泌量", data1)
    str += json_demo6_test(data, "间质的睾丸激素", data1)
    str += json_demo6_test(data, "胰岛素分泌量", data1)
    str += json_demo6_test(data, "肾上腺髓质激素分泌量", data1)
    str += json_demo6_test(data, "甲状旁腺激素分泌量", data1)
    str += json_demo6_test(data, "甲状腺激素分泌量", data1)
    str += json_demo6_test(data, "间质的抗利尿激素", data1)
    str += json_demo6_test(data, "间质的促肾上腺皮质激素", data1)
    return str
def json_demo7_test(data,str1,data1):
  if (data[str1] <=20 and data[str1]>=-20):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""
def json_demo7(data, data1):
    str = ""
    str += json_demo7_test(data, "胸部左侧区域", data1)
    str += json_demo7_test(data, "支气管区域", data1)
    str += json_demo7_test(data, "气管附近", data1)
    str += json_demo7_test(data, "左肺上叶区域", data1)
    str += json_demo7_test(data, "左肺下叶区域", data1)
    str += json_demo7_test(data, "胸部右侧区域", data1)
    str += json_demo7_test(data, "右肺中叶区域", data1)
    str += json_demo7_test(data, "右肺上叶区域", data1)

    return str

def json_demo8_test(data,str1,data1):
  if (data[str1] <=20 and data[str1]>=-20):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""
def json_demo8(data, data1):
    str = ""
    str += json_demo8_test(data, "小肠区域", data1)
    str += json_demo8_test(data, "直肠区域", data1)
    str += json_demo8_test(data, "盲肠和阑尾区域", data1)
    str += json_demo8_test(data, "升结肠区域", data1)
    str += json_demo8_test(data, "降结肠区域", data1)
    str += json_demo8_test(data, "肝左叶及胆管区域", data1)
    str += json_demo8_test(data, "胰腺区域", data1)
    str += json_demo8_test(data, "结肠脾区", data1)
    str += json_demo8_test(data, "结肠肝区", data1)
    str += json_demo8_test(data, "十二指肠区域", data1)
    str += json_demo8_test(data, "胃区域", data1)
    str += json_demo8_test(data, "食道下段", data1)
    str += json_demo8_test(data, "胆囊区域", data1)
    str += json_demo8_test(data, "食道上段", data1)
    str += json_demo8_test(data, "肝右页", data1)

    return str
def json_demo9_test(data,str1,data1):
  if (data[str1] <=20 and data[str1]>=-20):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""
def json_demo9(data, data1):
    str = ""
    str += json_demo9_test(data, "左唾液腺", data1)
    str += json_demo9_test(data, "右唾液腺", data1)
    str += json_demo9_test(data, "左侧鼻前庭和固有鼻腔区域", data1)
    str += json_demo9_test(data, "左耳区域", data1)
    str += json_demo9_test(data, "左上颌窦区域", data1)
    str += json_demo9_test(data, "左眼和泪腺区域", data1)
    str += json_demo9_test(data, "右侧鼻前庭和固有鼻腔区域", data1)
    str += json_demo9_test(data, "右上颌窦区域", data1)
    str += json_demo9_test(data, "右耳区域", data1)
    return str
def json_demo10_test(data,str1,data1):
  if (data[str1] <=20 and data[str1]>=-20):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""
def json_demo10(data, data1):
    str = ""
    str += json_demo10_test(data, "胸腺", data1)
    str += json_demo10_test(data, "脾脏区域", data1)
    return str
def json_demo11_test(data,str1,data1):
  if (data[str1] <=20 and data[str1]>=-20):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""
def json_demo11(data, data1):
    str = ""
    str += json_demo11_test(data, "左肾及输尿管区域", data1)
    str += json_demo11_test(data, "右肾及输尿管区域", data1)
    return str
def json_demo12_test(data,str1,data1):
  if (data[str1] <=20 and data[str1]>=-20):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""
def json_demo12(data, data1):
    str = ""
    str += json_demo12_test(data, "右侧额叶皮层", data1)
    str += json_demo12_test(data, "左侧颅内血管", data1)
    str += json_demo12_test(data, "左侧额叶皮层", data1)
    str += json_demo12_test(data, "右侧颅内血管", data1)
    str += json_demo12_test(data, "丘脑", data1)
    str += json_demo12_test(data, "右杏仁体", data1)
    str += json_demo12_test(data, "左杏仁体", data1)
    str += json_demo12_test(data, "垂体区域", data1)
    str += json_demo12_test(data, "右侧边缘系统（海马）", data1)
    str += json_demo12_test(data, "左侧颞叶", data1)
    str += json_demo12_test(data, "右侧颞叶", data1)
    str += json_demo12_test(data, "左侧边缘系统（海马）", data1)
    str += json_demo12_test(data, "下丘脑区域", data1)
    return str
def json_demo13_test(data,str1,data1):
  if (data[str1] <=20 and data[str1]>=-20):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""
def json_demo13(data, data1):
    str = ""
    str += json_demo13_test(data, "左侧肾上腺髓质", data1)
    str += json_demo13_test(data, "左侧颈部区域", data1)
    str += json_demo13_test(data, "右侧颈部区域", data1)
    str += json_demo13_test(data, "甲状腺区域", data1)
    str += json_demo13_test(data, "右侧肾上腺髓质", data1)
    str += json_demo13_test(data, "甲状腺右叶区域", data1)
    str += json_demo13_test(data, "甲状腺左叶区域", data1)
    return str
def json_demo14_test(data,str1,data1):
  if (data[str1] <=20 and data[str1]>=-20):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""
def json_demo14(data, data1):
    str = ""
    str += json_demo14_test(data, "冠状血管", data1)
    str += json_demo14_test(data, "右前庭压力感受器", data1)
    str += json_demo14_test(data, "左前庭压力感受器", data1)
    str += json_demo14_test(data, "心肌", data1)
    str += json_demo14_test(data, "右颈动脉", data1)
    str += json_demo14_test(data, "左颈动脉", data1)
    str += json_demo14_test(data, "左心室", data1)
    str += json_demo14_test(data, "左膝区域（腿部血管）", data1)
    str += json_demo14_test(data, "左大腿神经血管束", data1)
    str += json_demo14_test(data, "左小腿神经血管束", data1)
    str += json_demo14_test(data, "左脚神经血管束", data1)
    str += json_demo14_test(data, "右膝区域（腿部血管）", data1)
    str += json_demo14_test(data, "右大腿神经血管束", data1)
    str += json_demo14_test(data, "右小腿神经血管束", data1)
    str += json_demo14_test(data, "右脚神经血管束", data1)
    str += json_demo14_test(data, "左横隔膜神经区", data1)
    str += json_demo14_test(data, "左手神经血管束", data1)
    str += json_demo14_test(data, "左上臂神经血管束", data1)
    str += json_demo14_test(data, "左前臂神经血管束", data1)
    str += json_demo14_test(data, "主动脉", data1)
    str += json_demo14_test(data, "心脏区域", data1)
    str += json_demo14_test(data, "右侧膈神经区域", data1)
    str += json_demo14_test(data, "右手神经血管束", data1)
    str += json_demo14_test(data, "右上臂神经血管束", data1)
    str += json_demo14_test(data, "右前臂神经血管束", data1)
    str += json_demo14_test(data, "上腔静脉", data1)
    str += json_demo14_test(data, "右心室", data1)
    str += json_demo14_test(data, "心肺循环", data1)
    str += json_demo14_test(data, "下腔静脉", data1)
    str += json_demo14_test(data, "门脉循环", data1)
    return str
def json_demo15_test(data,str1,data1):
  if (data[str1] <=20 and data[str1]>=-20):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""
def json_demo15(data, data1):
    str = ""
    str += json_demo15_test(data, "C1", data1)
    str += json_demo15_test(data, "C2", data1)
    str += json_demo15_test(data, "C3", data1)
    str += json_demo15_test(data, "C4", data1)
    str += json_demo15_test(data, "S4", data1)
    str += json_demo15_test(data, "S5", data1)
    str += json_demo15_test(data, "Co1", data1)
    str += json_demo15_test(data, "L2", data1)
    str += json_demo15_test(data, "L3", data1)
    str += json_demo15_test(data, "L4", data1)
    str += json_demo15_test(data, "L5", data1)
    str += json_demo15_test(data, "S1", data1)
    str += json_demo15_test(data, "S2", data1)
    str += json_demo15_test(data, "S3", data1)
    str += json_demo15_test(data, "C5", data1)
    str += json_demo15_test(data, "C6", data1)
    str += json_demo15_test(data, "C7", data1)
    str += json_demo15_test(data, "Th4", data1)
    str += json_demo15_test(data, "Th5", data1)
    str += json_demo15_test(data, "Th6", data1)
    str += json_demo15_test(data, "Th8", data1)
    str += json_demo15_test(data, "Th9", data1)
    str += json_demo15_test(data, "Th10", data1)
    str += json_demo15_test(data, "L1", data1)
    str += json_demo15_test(data, "Th1", data1)
    str += json_demo15_test(data, "Th11", data1)
    str += json_demo15_test(data, "Th12", data1)
    str += json_demo15_test(data, "Th2", data1)
    str += json_demo15_test(data, "Th3", data1)
    return str
def json_demo16_test(data,str1,data1):
  if (data[str1] <=20 and data[str1]>=-20):
    return "您的"+str1+"含量正常\r\n"
  else:
    data1.append({str1: data[str1]})
    return ""
def json_demo16(data, data1):
    str = ""
    # str += json_demo13_test(data, "右侧上颌牙齿区域", data1)
    # str += json_demo13_test(data, "左侧下颌牙齿区域", data1)
    return str
#呼吸系统
def main():
    json_test()
if __name__ == "__main__":
    main()
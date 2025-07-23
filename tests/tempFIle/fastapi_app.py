from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForSequenceClassification, AutoModel,AutoTokenizer
import torch
 
app = FastAPI()
 
# 加载本地模型
model_path = "/home/hsap/hsap_model/DeepSeek-R1-Distill-Qwen-32B"
tokenizer = AutoTokenizer.from_pretrained(model_path)
# model = AutoModelForSequenceClassification.from_pretrained(model_path)
model = AutoModel.from_pretrained(model_path, trust_remote_code=True).half().cuda()
model = model.eval()

class TextRequest(BaseModel):
    text: str
 
@app.post("/predict")
async def predict(request: TextRequest):
    # 预处理和预测
    inputs = tokenizer(request.text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 获取预测结果
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    
    # 返回结果
    return {
        "text": request.text,
        "predictions": predictions.tolist()
    }

@app.post("/chat")
async def predict(request: TextRequest):
    response, history = model.chat(tokenizer, "你好", history=[])
    print(response)
    # while True:
    #         test_text = input("Kun Peng：")
    #         if test_text == "exit":
    #                 break
    #         response, history = model.chat(tokenizer, test_text, history=history)
    #         print("AI: " + response)

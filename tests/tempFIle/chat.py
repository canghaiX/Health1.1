from fastapi import FastAPI, Request
from transformers import AutoTokenizer, AutoModelForCausalLM
import uvicorn
import json
import datetime
import torch
import re
import os

# 设置设备参数
NUM_GPUS = torch.cuda.device_count() if torch.cuda.is_available() else 0
os.environ["CUDA_VISIBLE_DEVICES"] = ",".join([str(i) for i in range(NUM_GPUS)]) if NUM_GPUS > 0 else ""
print(f"检测到 {NUM_GPUS} 个GPU可用")

# 清理GPU内存函数
def torch_gc():
    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            with torch.cuda.device(i):
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()

# 文本分割函数
def split_text(text):
    pattern = re.compile(r'<think>(.*?)</think>(.*)', re.DOTALL)
    match = pattern.search(text)
  
    if match:
        think_content = match.group(1).strip()
        answer_content = match.group(2).strip()
    else:
        think_content = ""
        answer_content = text.strip()
  
    return think_content, answer_content

# 创建FastAPI应用
app = FastAPI()

# 处理POST请求的端点
@app.post("/")
async def create_item(request: Request):
    global model, tokenizer
    json_post_raw = await request.json()
    json_post = json.dumps(json_post_raw)
    json_post_list = json.loads(json_post)
    prompt = json_post_list.get('prompt')

    messages = [
        {"role": "user", "content": prompt}
    ]

    # 应用聊天模板
    input_text = tokenizer.apply_chat_template(
        messages, 
        tokenize=False, 
        add_generation_prompt=True
    )
    
    # 获取正确的设备
    device = model.device if not isinstance(model, torch.nn.DataParallel) else model.module.device
    
    # 添加显式的注意力掩码
    inputs = tokenizer(
        input_text,
        return_tensors="pt", 
        padding=True,
        return_attention_mask=True
    ).to(device)
    
    # 解决pad token和eos token相同的问题
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id
    
    # 设置生成参数
    generate_kwargs = {
        "input_ids": inputs.input_ids,
        "attention_mask": inputs.attention_mask,
        "max_new_tokens": 8192,
        "pad_token_id": tokenizer.pad_token_id
    }
    
    # 判断使用哪个模型
    model_to_generate = model.module if isinstance(model, torch.nn.DataParallel) else model
    
    # 生成文本
    with torch.no_grad():
        with torch.cuda.amp.autocast():
            generated_ids = model_to_generate.generate(**generate_kwargs)
    
    # 解码生成的文本
    response = tokenizer.decode(
        generated_ids[0][inputs.input_ids.shape[1]:], 
        skip_special_tokens=True
    )
    
    # 分割思考和回答
    think_content, answer_content = split_text(response)
    
    # 构建响应
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    answer = {
        "response": response,
        "think": think_content,
        "answer": answer_content,
        "status": 200,
        "time": time
    }
    
    # 记录日志
    log = f"[{time}], prompt:\"{prompt}\", think:\"{think_content}\", answer:\"{answer_content}\""
    print(log)
    
    # 清理内存
    torch_gc()
    
    return answer

# 主函数入口
if __name__ == '__main__':
    # 加载预训练的分词器和模型
    model_name_or_path = "/home/hsap/hsap_model/DeepSeek-R1-Distill-Qwen-32B"
    
    print("加载分词器...")
    tokenizer = AutoTokenizer.from_pretrained(
        model_name_or_path,
        use_fast=False
    )
    
    # 确保分词器有pad token
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    
    print("加载模型...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if NUM_GPUS > 0 else None,
        trust_remote_code=True
    )
    
    # 设置DataParallel
    if NUM_GPUS > 1:
        print(f"启用DataParallel以使用{NUM_GPUS}个GPU...")
        model = torch.nn.DataParallel(model)
    
    # 确保模型在评估模式
    model.eval()
    
    print("启动服务...")
    uvicorn.run(app, host='0.0.0.0', port=6007, workers=1)
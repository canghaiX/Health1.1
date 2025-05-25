



# Python拉流示例 [Demo]
import cv2

# 推流地址
rtmp_url = "rtmp://127.0.0.1/live/stream"
    
# 创建Video对象
cap = cv2.VideoCapture(rtmp_url)
    
# 检查是否成功打开流
if not cap.isOpened():
    exit()
    
# 读取并显示视频帧
while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('RTMP Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
cap.release()
cv2.destroyAllWindows()



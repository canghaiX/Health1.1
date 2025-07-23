from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database.base import Base

class RadarWave(Base):
    __tablename__ = 'radar_wave'
    
    user_id = Column(Integer, primary_key=True, index=True, comment='用户唯一标识')
    radar_data = Column(Text, nullable=True, comment='最新的无异常雷达波数据')
    radar_date = Column(DateTime, nullable=True, comment='无异常数据存放时间')
    abnormal_data = Column(Text, nullable=True, comment='最近一次触发异常的雷达波数据')
    abnormal_date = Column(DateTime, nullable=True, comment='异常数据存放时间')
    device_id = Column(String(50), nullable=True, comment='采集设备ID')
import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any, Optional, Union

class SQLHelper:
    """MySQL数据库操作助手类"""
    
    def __init__(self, host: str, user: str, password: str, database: str):
        """
        初始化数据库连接参数
        
        Args:
            host: 数据库主机地址
            user: 数据库用户名
            password: 数据库密码
            database: 数据库名称
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
    
    def connect(self) -> bool:
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return self.connection.is_connected()
        except Error as e:
            print(f"连接数据库失败: {e}")
            return False
    
    def disconnect(self) -> None:
        """断开数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> bool:
        """
        执行SQL查询（INSERT, UPDATE, DELETE等）
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            操作是否成功
        """
        if not self.connect():
            return False
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params or ())
            self.connection.commit()
            return True
        except Error as e:
            print(f"执行查询失败: {e}")
            self.connection.rollback()
            return False
        finally:
            self.disconnect()
    
    def fetch_one(self, query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
        """
        获取单条查询结果
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果字典或None
        """
        if not self.connect():
            return None
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchone()
        except Error as e:
            print(f"获取数据失败: {e}")
            return None
        finally:
            self.disconnect()
    
    def fetch_all(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        获取所有查询结果
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        if not self.connect():
            return []
            
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor.fetchall()
        except Error as e:
            print(f"获取数据失败: {e}")
            return []
        finally:
            self.disconnect()
    
    # 通用CRUD方法
    
    def create_record(self, table_name: str, data: Dict[str, Any]) -> bool:
        """
        插入单条记录
        
        Args:
            table_name: 表名
            data: 记录数据，键为字段名，值为字段值
            
        Returns:
            插入是否成功
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        return self.execute_query(query, tuple(data.values()))
    
    def get_record(self, table_name: str, conditions: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        获取单条记录
        
        Args:
            table_name: 表名
            conditions: 查询条件，键为字段名，值为字段值
            
        Returns:
            记录数据或None
        """
        where_clause = ' AND '.join([f"{key} = %s" for key in conditions])
        query = f"SELECT * FROM {table_name} WHERE {where_clause}"
        return self.fetch_one(query, tuple(conditions.values()))
    
    def get_records(self, table_name: str, conditions: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        获取多条记录
        
        Args:
            table_name: 表名
            conditions: 查询条件，键为字段名，值为字段值
            
        Returns:
            记录数据列表
        """
        if conditions:
            where_clause = ' AND '.join([f"{key} = %s" for key in conditions])
            query = f"SELECT * FROM {table_name} WHERE {where_clause}"
            return self.fetch_all(query, tuple(conditions.values()))
        else:
            query = f"SELECT * FROM {table_name}"
            return self.fetch_all(query)
    
    def update_record(self, table_name: str, data: Dict[str, Any], conditions: Dict[str, Any]) -> bool:
        """
        更新记录
        
        Args:
            table_name: 表名
            data: 需要更新的数据，键为字段名，值为字段值
            conditions: 更新条件，键为字段名，值为字段值
            
        Returns:
            更新是否成功
        """
        set_clause = ', '.join([f"{key} = %s" for key in data])
        where_clause = ' AND '.join([f"{key} = %s" for key in conditions])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
        params = tuple(data.values()) + tuple(conditions.values())
        return self.execute_query(query, params)
    
    def delete_record(self, table_name: str, conditions: Dict[str, Any]) -> bool:
        """
        删除记录
        
        Args:
            table_name: 表名
            conditions: 删除条件，键为字段名，值为字段值
            
        Returns:
            删除是否成功
        """
        where_clause = ' AND '.join([f"{key} = %s" for key in conditions])
        query = f"DELETE FROM {table_name} WHERE {where_clause}"
        return self.execute_query(query, tuple(conditions.values()))
    
    # 特定表的便捷方法
    
    def get_hra_json_data(self, user_id: int) -> List[Dict[str, Any]]:
        """
        根据用户ID获取HRA数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            HRA数据列表
        """
        return self.get_records("hra_data", {"user_id": user_id})
    
    def create_user(self, user_name: str, phone: str, ex_field: str = None) -> bool:
        """
        创建新用户
        
        Args:
            user_name: 用户姓名
            phone: 手机号
            ex_field: 扩展字段
            
        Returns:
            创建是否成功
        """
        data = {"user_name": user_name, "phone": phone}
        if ex_field:
            data["ex_field"] = ex_field
        return self.create_record("users", data)
    
    # 雷达波数据相关方法
    
    def create_radar_wave_data(self, data: Dict[str, Any]) -> bool:
        """
        插入雷达波数据
        
        Args:
            data: 雷达波数据字典，应包含以下键：
                - csgCollectId
                - user_id
                - equipment_id
                - startTime
                - endTime
                - heartRate
                - heartConclusion
                - breathConclusion
                - sti
                - sdnn
                - rmssd
                - pnn50
                - cvsd
                - cvcdi
                - lf
                - hf
                - ifHfRatio
                - breathRate
                - avgBreathDepth
                - maxBreathDepth
                - minBreathDepth
                - expiratoryTime
                - inspiratoryTime
                
        Returns:
            插入是否成功
        """
        required_fields = [
            "csgCollectId", "user_id", "equipment_id", "startTime", "endTime",
            "heartRate", "heartConclusion", "breathConclusion", "sti", "sdnn",
            "rmssd", "pnn50", "cvsd", "cvcdi", "lf", "hf", "ifHfRatio",
            "breathRate", "avgBreathDepth", "maxBreathDepth", "minBreathDepth",
            "expiratoryTime", "inspiratoryTime"
        ]
        
        # 检查必要字段
        for field in required_fields:
            if field not in data:
                print(f"缺少必要字段: {field}")
                return False
                
        return self.create_record("radar_wave", data)
    
    def get_radar_wave_data_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """
        根据用户ID获取雷达波数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            雷达波数据列表
        """
        return self.get_records("radar_wave", {"user_id": user_id})
    
    def get_radar_wave_data_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        根据记录ID获取雷达波数据
        
        Args:
            record_id: 记录ID
            
        Returns:
            雷达波数据或None
        """
        return self.get_record("radar_wave", {"id": record_id})
    
    def update_radar_wave_data(self, record_id: int, data: Dict[str, Any]) -> bool:
        """
        更新雷达波数据
        
        Args:
            record_id: 记录ID
            data: 需要更新的数据
            
        Returns:
            更新是否成功
        """
        return self.update_record("radar_wave", data, {"id": record_id})
    
    def delete_radar_wave_data(self, record_id: int) -> bool:
        """
        删除雷达波数据
        
        Args:
            record_id: 记录ID
            
        Returns:
            删除是否成功
        """
        return self.delete_record("radar_wave", {"id": record_id})
    
    def get_radar_wave_data_by_time_range(self, start_time: str, end_time: str) -> List[Dict[str, Any]]:
        """
        根据时间范围获取雷达波数据
        
        Args:
            start_time: 开始时间（格式：YYYY-MM-DD HH:MM:SS）
            end_time: 结束时间（格式：YYYY-MM-DD HH:MM:SS）
            
        Returns:
            雷达波数据列表
        """
        query = """
        SELECT * FROM radar_wave 
        WHERE startTime >= %s AND endTime <= %s
        """
        return self.fetch_all(query, (start_time, end_time))


# 使用示例
if __name__ == "__main__":
    # 初始化助手
    helper = SQLHelper(
        host="localhost",
        user="your_username",
        password="your_password",
        database="your_database"
    )
    
    # 示例：插入雷达波数据
    radar_data = {
        "csgCollectId": "a8afa745-819c-46a0-aea3-02cfd4de3884",
        "user_id": 1,
        "equipment_id": 101,
        "startTime": "2023-01-01 10:00:00",
        "endTime": "2023-01-01 10:10:00",
        "heartRate": 75,
        "heartConclusion": "正常",
        "breathConclusion": "正常",
        "sti": 0.85,
        "sdnn": 15.2,
        "rmssd": 12.3,
        "pnn50": 5.4,
        "cvsd": 0.05,
        "cvcdi": 0.06,
        "lf": 0.45,
        "hf": 0.55,
        "ifHfRatio": 0.82,
        "breathRate": 18,
        "avgBreathDepth": 3.5,
        "maxBreathDepth": 4.2,
        "minBreathDepth": 2.8,
        "expiratoryTime": 3,
        "inspiratoryTime": 2
    }
    
    if helper.create_radar_wave_data(radar_data):
        print("雷达波数据插入成功")
    
    # 示例：根据用户ID获取雷达波数据
    waves = helper.get_radar_wave_data_by_user(1)
    print(f"获取到 {len(waves)} 条雷达波数据")
    
    # 示例：根据时间范围获取雷达波数据
    waves_in_range = helper.get_radar_wave_data_by_time_range(
        "2023-01-01 00:00:00", 
        "2023-01-02 00:00:00"
    )
    print(f"在指定时间范围内有 {len(waves_in_range)} 条记录")    
"""
不建议使用这个函数，使用或修改sql_helper,此函数作为测试使用而编写
"""
import mysql.connector
from mysql.connector import Error

def get_hra_json_data(user_id):
    """
    根据用户ID从hra_data表中获取hra_json_data
    :param user_id: 用户ID
    :return: 查询结果列表，每个元素是一个包含hra_json_data的字典
    """
    try:
        # 建立数据库连接
        connection = mysql.connector.connect(
            host='localhost',       # 数据库主机地址
            user='your_username',   # 数据库用户名
            password='your_password', # 数据库密码
            database='your_database'  # 数据库名称
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            # 执行查询
            query = """
            SELECT hra_json_data 
            FROM hra_data 
            WHERE user_id = %s
            """
            cursor.execute(query, (user_id,))
            # 获取所有结果
            results = cursor.fetchall()
            return results
            
    except Error as e:
        print(f"数据库操作错误: {e}")
    finally:
        # 关闭数据库连接
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("数据库连接已关闭")

# 使用示例
if __name__ == "__main__":
    user_id = 1  # 替换为实际的用户ID
    hra_data = get_hra_json_data(user_id)
    
    if hra_data:
        print(f"找到 {len(hra_data)} 条记录")
        for data in hra_data:
            print(data['hra_json_data'])
    else:
        print(f"未找到用户ID为 {user_id} 的记录")    
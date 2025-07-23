import json
import mysql.connector

# 数据库连接配置
db_config = {
    'host': '127.0.0.1',
    'user': 'hsap',
    'password': 'yanshandaxue',
    'database': 'hsap'
}

# 固定字段值（确保类型与表结构一致）
FIXED_VALUES = {
    'upload_file_id': 1,  # int(11)
    'equipment_id': 1  # int(11)
}


def import_jsonl_to_mysql(jsonl_file_path):
    # 连接到MySQL数据库
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # 获取当前最大ID（确保返回int类型）
        cursor.execute("SELECT COALESCE(MAX(id), 0) FROM hra_data")
        current_id = cursor.fetchone()[0] + 1  # 确保从下一个ID开始

        # 获取当前最大user_id（确保返回int类型）
        cursor.execute("SELECT COALESCE(MAX(user_id), 0) FROM hra_data")
        current_user_id = cursor.fetchone()[0] + 1  # 确保从下一个user_id开始

        # 准备插入语句
        insert_sql = """
                     INSERT INTO hra_data
                         (id, hra_json_data, upload_file_id, user_id, equipment_id)
                     VALUES (%s, %s, %s, %s, %s) \
                     """

        # 读取.jsonl文件并逐行处理
        with open(jsonl_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # 验证JSON格式是否有效
                try:
                    json_data = json.loads(line)
                    # 确保json_data是字典类型，如果不是则转换为字典
                    if not isinstance(json_data, dict):
                        json_data = {"data": json_data}
                except json.JSONDecodeError as e:
                    print(f"跳过无效的JSON行: {line}. 错误: {e}")
                    continue

                # 准备插入数据（确保类型匹配）
                insert_data = (
                    int(current_id),  # id字段 - int(11)
                    json.dumps(json_data, ensure_ascii=False)[:65535],  # hra_json_data - varchar(65535)
                    int(FIXED_VALUES['upload_file_id']),  # upload_file_id - int(11)
                    int(current_user_id),  # user_id - int(11)
                    int(FIXED_VALUES['equipment_id'])  # equipment_id - int(11)
                )

                # 执行插入
                cursor.execute(insert_sql, insert_data)
                current_id += 1
                current_user_id += 1  # 每插入一行，user_id也自增

        # 提交事务
        conn.commit()
        print(f"成功导入 {cursor.rowcount} 条记录")

    except Exception as e:
        conn.rollback()
        print(f"导入过程中发生错误: {e}")
    finally:
        cursor.close()
        conn.close()


# 使用示例
if __name__ == "__main__":
    jsonl_file_path = '/home/hsap/Health1.1/merged(2).jsonl'  # 替换为你的.jsonl文件路径
    import_jsonl_to_mysql(jsonl_file_path)
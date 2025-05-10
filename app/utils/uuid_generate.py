import hashlib
import os


def generate_uid():
    # 生成一个随机的字节串
    random_bytes = os.urandom(8)  # 生成8字节的随机数据

    # 使用SHA-256哈希算法，然后取前16位（32个十六进制字符的一半）
    hash_object = hashlib.sha256(random_bytes)
    hash_hex = hash_object.hexdigest()[:16]
    return hash_hex

-- 创建数据库
CREATE DATABASE IF NOT EXISTS hsap CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE hsap;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    user_id INT NOT NULL PRIMARY KEY COMMENT '用户唯一标识',
    user_name VARCHAR(80) NOT NULL COMMENT '用户姓名',
    phone VARCHAR(11)  COMMENT '手机号',
    ex_field VARCHAR(255) COMMENT '拓展字段'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- HRA数据表
CREATE TABLE IF NOT EXISTS hra_data (
    user_id INT NOT NULL PRIMARY KEY COMMENT '关联用户ID',
    hra_data TEXT  COMMENT 'HRA报告的json数据',
    hra_date TIMESTAMP(6)  COMMENT '数据存入时间',
    CONSTRAINT fk_hra_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 问答数据表
CREATE TABLE IF NOT EXISTS qa_data (
    user_id INT NOT NULL PRIMARY KEY COMMENT '关联用户ID',
    hra_qa_data TEXT  COMMENT '问答数据',
    qa_date TIMESTAMP(6)  COMMENT '问答时间',
    hra_report_data TEXT  COMMENT '生成的报告',
    report_date TIMESTAMP(6)  COMMENT '报告生成时间',
    CONSTRAINT fk_qa_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 雷达波数据表
CREATE TABLE IF NOT EXISTS radar_wave (
    user_id INT NOT NULL PRIMARY KEY COMMENT '关联用户ID',
    radar_data TEXT COMMENT '正常雷达波数据',
    radar_date TIMESTAMP(6) COMMENT '正常数据时间',
    abnormal_data TEXT COMMENT '异常雷达波数据',
    abnormal_date TIMESTAMP(6) COMMENT '异常数据时间',
    device_id INT COMMENT '设备ID',
    CONSTRAINT fk_radar_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- 创建索引优化查询性能
CREATE INDEX idx_hra_data_user ON hra_data(user_id);
CREATE INDEX idx_qa_data_user ON qa_data(user_id);
CREATE INDEX idx_radar_wave_user ON radar_wave(user_id);
CREATE INDEX idx_conversations_user ON conversations(user_id);
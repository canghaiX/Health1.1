DROP TABLE IF EXISTS `conversation`;
CREATE TABLE `conversation`  (
  `UUID` varchar(128) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `Summary` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `userId` varchar(20) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`UUID`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;



DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `user_id` int(11) NOT NULL COMMENT '用户id',
  `user_name` varchar(80) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '用户姓名',
  `phone` varchar(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '手机号',
  `ex_field` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL COMMENT '拓展字段',
  PRIMARY KEY (`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;



DROP TABLE IF EXISTS `uploaded_files`;
CREATE TABLE `uploaded_files`  (
  `id` int(11) NOT NULL COMMENT 'hra上传文件的id',
  `file_path` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '文件路径',
  `file_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '文件名称',
  `upload_time` datetime(0) NOT NULL COMMENT '上传时间',
  `user_id` int(11) NOT NULL COMMENT 'user表的user_id做外键',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;




DROP TABLE IF EXISTS `hra_data`;
CREATE TABLE `hra_data`  (
  `id` int(11) NOT NULL COMMENT 'id，标识',
  `hra_json_data` varchar(1023) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT 'hra报告的json数据',
  `upload_file_id` int(11) NOT NULL COMMENT 'uploaded_files表的id，外键',
  `user_id` int(11) NOT NULL COMMENT 'users表的id，作外键（可能多余）',
  `equipment_id` int(11) NOT NULL COMMENT '设备id',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;



DROP TABLE IF EXISTS `radar_wave`;
CREATE TABLE `radar_wave`  (
  `id` int(11) NOT NULL COMMENT 'id，标识',
  `csgCollectId` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '样例：a8afa745-819c-46a0-aea3-02cfd4de3884',
  `user_id` int(11) NOT NULL COMMENT '关联到用户',
  `equipment_id` int(11) NULL DEFAULT NULL COMMENT '设备id',
  `startTime` datetime(0) NOT NULL COMMENT '开始时间戳，毫秒级',
  `endTime` datetime(0) NOT NULL COMMENT '结束时间戳，毫秒级',
  `heartRate` int(11) NOT NULL COMMENT '心率',
  `heartConclusion` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '心脏诊断结果',
  `breathConclusion` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT '呼吸诊断结果',
  `sti` float NOT NULL COMMENT '应该是某种指标',
  `sdnn` float NOT NULL COMMENT '心脏相关',
  `rmssd` float NOT NULL COMMENT '心脏相关',
  `pnn50` float NOT NULL COMMENT '心脏相关',
  `cvsd` float NOT NULL COMMENT '心脏相关',
  `cvcdi` float NOT NULL COMMENT '心脏相关',
  `lf` float NOT NULL COMMENT '心脏相关',
  `hf` float NOT NULL COMMENT '心脏相关',
  `ifHfRatio` float NOT NULL COMMENT '心脏相关',
  `breathRate` int(11) NOT NULL COMMENT '呼吸频率',
  `avgBreathDepth` float NOT NULL COMMENT '平均呼吸深度',
  `maxBreathDepth` float NOT NULL COMMENT '最大呼吸深度',
  `minBreathDepth` float NOT NULL COMMENT '最小呼吸深度',
  `expiratoryTime` int(11) NOT NULL COMMENT '呼吸机呼气时间',
  `inspiratoryTime` int(11) NOT NULL COMMENT '吸气时间',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
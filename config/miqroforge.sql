/*
 Navicat Premium Data Transfer

 Source Server         : 10.36.160.25_32002
 Source Server Type    : MySQL
 Source Server Version : 100908
 Source Host           : 10.36.160.25:32002
 Source Schema         : miqroforge_dev

 Target Server Type    : MySQL
 Target Server Version : 100908
 File Encoding         : 65001

 Date: 08/08/2025 15:46:35
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for job
-- ----------------------------
DROP TABLE IF EXISTS `job`;
CREATE TABLE `job`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '作业ID',
  `task_id` bigint NOT NULL COMMENT '关联任务ID',
  `node_id` bigint NOT NULL COMMENT '任务节点ID',
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '作业名称',
  `ns` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '作业运行资源空间',
  `image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '作业运行镜像',
  `command` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '作业运行指令',
  `args` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `sort` smallint NOT NULL COMMENT '作业执行顺序',
  `data_dir` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '作业输入目录',
  `status` smallint NOT NULL COMMENT '作业状态 (0=Pending,1=Running,2=Success,3=Failed,4=Unknown)',
  `created_time` datetime NOT NULL DEFAULT current_timestamp COMMENT '作业创建时间',
  `finished_time` datetime NULL DEFAULT NULL COMMENT '作业结束时间',
  `retry_count` tinyint UNSIGNED NOT NULL DEFAULT 0 COMMENT '重试次数',
  `cost_time` int NULL DEFAULT NULL COMMENT '耗时(秒)',
  `msg` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '作业信息',
  `node_type` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '节点类型',
  `cpu` int NULL DEFAULT NULL COMMENT 'cpu核心数',
  `memory` int NULL DEFAULT NULL COMMENT '内存大小 G',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_task_id`(`task_id` ASC) USING BTREE,
  INDEX `idx_status_created_time`(`status` ASC, `created_time` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2886 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '作业记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for job_history
-- ----------------------------
DROP TABLE IF EXISTS `job_history`;
CREATE TABLE `job_history`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '作业ID',
  `job_id` bigint NOT NULL COMMENT 'jobID',
  `task_id` bigint NOT NULL COMMENT '关联任务ID',
  `node_id` bigint NOT NULL COMMENT '任务节点ID',
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '作业名称',
  `ns` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '作业运行资源空间',
  `image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '作业运行镜像',
  `command` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '作业运行指令',
  `args` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '作业运行命令参数',
  `sort` smallint NOT NULL COMMENT '作业执行顺序',
  `data_dir` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '作业输入目录',
  `status` smallint NOT NULL COMMENT '作业状态 (0=Pending,1=Running,2=Success,3=Failed,4=Unknown)',
  `created_time` datetime NOT NULL DEFAULT current_timestamp COMMENT '作业创建时间',
  `finished_time` datetime NULL DEFAULT NULL COMMENT '作业结束时间',
  `retry_count` tinyint UNSIGNED NOT NULL DEFAULT 0 COMMENT '重试次数',
  `cost_time` int NULL DEFAULT NULL COMMENT '耗时(秒)',
  `msg` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '作业信息',
  `node_type` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '节点类型',
  `cpu` int NULL DEFAULT NULL COMMENT 'cpu 核心数',
  `memory` int NULL DEFAULT NULL COMMENT '内存大小 G',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_task_id`(`task_id` ASC) USING BTREE,
  INDEX `idx_status_created_time`(`status` ASC, `created_time` ASC) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2808 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '作业历史记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for node
-- ----------------------------
DROP TABLE IF EXISTS `node`;
CREATE TABLE `node`  (
  `id` varchar(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '节点ID',
  `type` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '节点类型(I:输入,C:计算,T:转换,D:展示)',
  `name` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '节点名称(中英文)',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '描述',
  `version` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '版本号',
  `color` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '颜色',
  `tag` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '标签',
  `input` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '输入参数',
  `output` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '输出参数',
  `performance_config_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '性能配置路径',
  `example_config_path` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '示例配置路径',
  `contact` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '联系人信息',
  `execution_command` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '执行命令',
  `image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '镜像地址',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '节点信息表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for sys_minio_file
-- ----------------------------
DROP TABLE IF EXISTS `sys_minio_file`;
CREATE TABLE `sys_minio_file`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `original_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '图片原始文件名称',
  `suffix` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '后缀名称',
  `bucket` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT 'minio;桶名称',
  `object` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '存储地址',
  `temp` tinyint(1) NULL DEFAULT 1 COMMENT '是否临时文件',
  `created_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '创建人',
  `created_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `updated_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '修改人',
  `updated_time` datetime NULL DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `bucket_object`(`bucket` ASC, `object` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 775 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci COMMENT = '对象存储文件记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for task
-- ----------------------------
DROP TABLE IF EXISTS `task`;
CREATE TABLE `task`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '任务ID',
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '任务名称',
  `created_time` datetime NOT NULL DEFAULT current_timestamp COMMENT '创建时间',
  `start_time` datetime NULL DEFAULT NULL COMMENT '任务实际开始时间',
  `end_time` datetime NULL DEFAULT NULL COMMENT '任务实际结束时间',
  `cost_time` int NULL DEFAULT NULL COMMENT '任务耗时(秒)',
  `status` smallint NOT NULL COMMENT '状态: 1 Created    任务已提交，等待调度	资源不足、依赖未满足 2 Queued	任务进入执行队列（部分系统合并此状态）队列中有更高优先级任务 3 Running	任务正在执行 4 Succeeded  任务成功完成	进程返回0退出码 5 Failed  任务执行失败	程序崩溃/超时/资源不足 6 Cancelled	  任务被主动终止	用户手动停止错误任务',
  `updated_time` datetime NOT NULL DEFAULT current_timestamp ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `data_dir` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '数据目录路径',
  `deleted` bigint NOT NULL DEFAULT 0 COMMENT '是否删除: 0L未删除，ID已删除',
  `created_by` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '创建人',
  `priority` tinyint UNSIGNED NULL DEFAULT 50 COMMENT '任务优先级(1-100)',
  `retry_count` tinyint UNSIGNED NULL DEFAULT 0 COMMENT '重试次数',
  `error_message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '错误信息',
  `progress` tinyint UNSIGNED NULL DEFAULT 0 COMMENT '进度百分比(0-100)',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_created_time`(`created_time` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE,
  INDEX `idx_status_updated_time`(`status` ASC, `updated_time` ASC) USING BTREE,
  INDEX `idx_deleted`(`deleted` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 259 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '任务表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for task_node
-- ----------------------------
DROP TABLE IF EXISTS `task_node`;
CREATE TABLE `task_node`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '节点ID',
  `vo_id` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `task_id` bigint NOT NULL COMMENT '关联任务ID',
  `name_cn` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '节点中文名称',
  `name_en` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '节点英文名称',
  `node_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '节点编码',
  `category_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '节点分类',
  `sort` smallint UNSIGNED NOT NULL DEFAULT 0 COMMENT '节点排序(0-9999)',
  `image` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '节点镜像',
  `command` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '运行命令',
  `args` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '命令参数',
  `status` smallint NULL DEFAULT NULL COMMENT '节点状态1.  created，2. running，3. success 4. failed 5. cancelled',
  `msg` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '状态信息',
  `data_dir` varchar(512) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '数据存储目录',
  `props` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL COMMENT '节点属性',
  `job_num` int NULL DEFAULT NULL COMMENT '作业数量',
  `created_time` datetime NULL DEFAULT NULL COMMENT '创建时间',
  `finished_time` datetime NULL DEFAULT NULL COMMENT '完成时间',
  `start_time` datetime NULL DEFAULT NULL COMMENT '开始时间',
  `type` int NULL DEFAULT NULL COMMENT '节点类型 0：输入型 1：计算型，2：转换型，3：展示型',
  `desc_cn` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '中文描述',
  `desc_en` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '英文描述',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_task_id`(`task_id` ASC) USING BTREE,
  INDEX `idx_vo_id`(`vo_id` ASC) USING BTREE,
  INDEX `idx_status`(`status` ASC) USING BTREE,
  INDEX `idx_task_status`(`task_id` ASC, `status` ASC) USING BTREE,
  INDEX `idx_node_code`(`node_code` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1549 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '任务节点表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for task_node_params
-- ----------------------------
DROP TABLE IF EXISTS `task_node_params`;
CREATE TABLE `task_node_params`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '参数ID',
  `task_id` bigint NOT NULL COMMENT '任务ID',
  `node_id` bigint NOT NULL COMMENT '计算节点ID',
  `type` tinyint(1) NOT NULL DEFAULT 0 COMMENT '参数类型：0-输入，1-输出',
  `name_cn` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '参数中文名称',
  `name_en` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '参数唯一标识（英文Key）',
  `param_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '参数编码',
  `alias` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '参数别名',
  `value` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '数据值（JSON格式存储）',
  `data_type` tinyint NOT NULL COMMENT '数据类型：0-整数，1-浮点，2-字符串，3-布尔',
  `format` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '文件格式（默认json）',
  `desc_cn` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '中文描述说明',
  `desc_en` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '英文描述说明',
  `required` tinyint(1) NULL DEFAULT NULL COMMENT '是否必填',
  `attached` tinyint(1) NULL DEFAULT NULL COMMENT '是否为端子可连接',
  `props` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '参数属性',
  `options` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '值域说明',
  `is_resolved` tinyint(1) NULL DEFAULT 0 COMMENT '是否需要解析',
  `order_by` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '排序属性',
  `is_asc` tinyint(1) NULL DEFAULT NULL COMMENT '是否升序',
  `default_value` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `version` int UNSIGNED NOT NULL DEFAULT 1 COMMENT '参数版本号',
  `is_encrypted` tinyint(1) NOT NULL DEFAULT 0 COMMENT '是否加密：0-明文，1-密文',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_task_node_type_param`(`task_id` ASC, `node_id` ASC, `param_code` ASC, `type` ASC) USING BTREE,
  INDEX `idx_node_id`(`node_id` ASC) USING BTREE,
  INDEX `idx_task_id`(`task_id` ASC) USING BTREE,
  INDEX `idx_param_code`(`param_code` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 26556 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '任务节点参数表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for task_node_relation
-- ----------------------------
DROP TABLE IF EXISTS `task_node_relation`;
CREATE TABLE `task_node_relation`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '关系ID',
  `task_id` bigint NOT NULL COMMENT '关联任务ID',
  `source_vo_id` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `source_id` bigint NULL DEFAULT NULL COMMENT '源节点ID',
  `source_param_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '源端点编码',
  `target_vo_id` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `target_id` bigint NULL DEFAULT NULL COMMENT '目标节点ID',
  `target_param_code` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '目标端点编码',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uk_source_target`(`source_id` ASC, `target_id` ASC, `source_param_code` ASC, `target_param_code` ASC) USING BTREE,
  INDEX `idx_task_id`(`task_id` ASC) USING BTREE,
  INDEX `idx_source_id`(`source_id` ASC) USING BTREE,
  INDEX `idx_target_id`(`target_id` ASC) USING BTREE,
  INDEX `idx_vo_ids`(`source_vo_id` ASC, `target_vo_id` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1555 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin COMMENT = '任务节点关系表' ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `jira` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bugid` int(11) DEFAULT NULL COMMENT '已解决状态bug的id',
  `bugname` varchar(255) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '已解决状态bug的名字',
  PRIMARY KEY (`id`),
  UNIQUE KEY `bugid` (`bugid`) USING HASH COMMENT '加快查询速度'
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
export type SkillGroup = {
  label: string
  options: string[]
}

export const skillGroups: SkillGroup[] = [
  {
    label: '编程语言与后端开发',
    options: [
      'Python',
      'Java',
      'JavaScript',
      'TypeScript',
      'Go',
      'C++',
      'C#',
      'PHP',
      'Rust',
      'Scala',
      'SQL',
      'FastAPI',
      'Flask',
      'Django',
      'Spring Boot',
      'Spring Cloud',
      'RESTful API',
      'OpenAPI',
      '微服务',
      '消息队列',
      '权限管理',
      '接口联调',
      '性能优化'
    ]
  },
  {
    label: '前端与可视化',
    options: [
      'Vue',
      'React',
      'Vite',
      'Element Plus',
      'Ant Design',
      'ECharts',
      'AntV G6',
      'Three.js',
      '数据可视化',
      '响应式布局',
      '组件化开发',
      '前端工程化',
      '可视化大屏',
      'WebGL',
      '低代码配置',
      'UI/UX 设计',
      'Figma',
      '交互设计',
      '设计系统'
    ]
  },
  {
    label: '人工智能与大模型',
    options: [
      '机器学习',
      '深度学习',
      'NLP',
      '计算机视觉',
      'RAG',
      'Prompt Engineering',
      'LangChain',
      '向量数据库',
      '知识图谱',
      '智能体编排',
      '工作流引擎',
      'LLMOps',
      '模型评估',
      '模型部署',
      '模型压缩',
      'ONNX',
      'PyTorch',
      'TensorFlow',
      'Scikit-learn',
      '特征工程',
      '推荐系统',
      '强化学习',
      'AIGC 应用设计',
      '模型安全',
      '幻觉评估',
      '多模态理解'
    ]
  },
  {
    label: '数据技术与分析',
    options: [
      '数据分析',
      '统计分析',
      'Pandas',
      'NumPy',
      'A/B 测试',
      '用户画像',
      'BI 分析',
      '数据仓库',
      '实时数仓',
      '湖仓一体',
      'ETL',
      'Airflow',
      'Hadoop',
      'Spark',
      'Flink',
      'Kafka',
      'Hive',
      'ClickHouse',
      'Elasticsearch',
      'Tableau',
      'Power BI',
      'FineBI',
      '指标体系',
      '经营分析',
      '数据建模'
    ]
  },
  {
    label: '数据治理与资产管理',
    options: [
      '数据治理',
      '数据血缘',
      '元数据管理',
      '数据质量',
      '主数据管理',
      '数据标准',
      '数据资产运营',
      '数据目录',
      '数据安全',
      '数据合规',
      '数据分级分类',
      '数据生命周期管理',
      '数据服务',
      '数据共享交换',
      '质量稽核',
      '问题整改闭环'
    ]
  },
  {
    label: '数据库与中间件',
    options: [
      'MySQL',
      'Redis',
      'PostgreSQL',
      'MongoDB',
      'Oracle',
      'Neo4j',
      'Milvus',
      'Faiss',
      '数据库运维',
      'SQL 优化',
      '索引优化',
      '备份恢复',
      '分库分表',
      '缓存设计',
      '高可用架构',
      'Nginx'
    ]
  },
  {
    label: '云计算与工程效能',
    options: [
      'Linux',
      'Git',
      'Docker',
      'Kubernetes',
      '云计算架构',
      'DevOps',
      'SRE',
      'CI/CD',
      'Prometheus',
      'Grafana',
      '容器编排',
      '服务网格',
      '自动化运维',
      '日志分析',
      '链路追踪',
      '容量规划',
      '故障复盘',
      '灰度发布',
      '蓝绿发布',
      '云成本优化'
    ]
  },
  {
    label: '网络安全与合规',
    options: [
      '网络协议',
      '云安全',
      '安全合规',
      '渗透测试',
      '漏洞扫描',
      '风险策略',
      '内容审核',
      '应急响应',
      '日志审计',
      '安全基线',
      '等保测评',
      '身份认证',
      '访问控制',
      '数据脱敏',
      '威胁建模',
      '安全运营',
      '攻防演练'
    ]
  },
  {
    label: '测试与质量保障',
    options: [
      '测试自动化',
      '性能测试',
      '接口测试',
      '单元测试',
      '集成测试',
      '回归测试',
      '测试用例设计',
      '缺陷管理',
      '测试数据管理',
      '质量度量',
      '兼容性测试',
      '稳定性测试',
      '压测分析'
    ]
  },
  {
    label: '产品、项目与交付',
    options: [
      '需求分析',
      '产品设计',
      '项目管理',
      '客户调研',
      '业务流程建模',
      '售前方案',
      '实施交付',
      'ERP 实施',
      'ITIL',
      'PRD 编写',
      '原型设计',
      '用户研究',
      '竞品分析',
      '版本规划',
      '验收测试',
      '培训交付',
      '招投标支持',
      '解决方案设计'
    ]
  },
  {
    label: '物联网与智能系统',
    options: [
      '物联网协议',
      'MQTT',
      '边缘计算',
      '传感器数据处理',
      '嵌入式 Linux',
      '设备接入',
      '网关配置',
      '工业数据采集',
      '智能制造',
      '设备状态监测',
      '数字孪生',
      'Modbus',
      'OPC UA',
      '现场实施',
      '硬件联调'
    ]
  },
  {
    label: '运营、标注与通用能力',
    options: [
      '数据标注',
      '数据标注管理',
      '内容安全',
      '运营分析',
      '流程优化',
      '文档编写',
      '沟通协调',
      '问题定位',
      '复盘总结',
      '学习能力',
      '跨团队协作',
      '汇报表达',
      '业务理解',
      '结构化思维'
    ]
  }
]

export const skillOptions = [...new Set(skillGroups.flatMap((group) => group.options))]

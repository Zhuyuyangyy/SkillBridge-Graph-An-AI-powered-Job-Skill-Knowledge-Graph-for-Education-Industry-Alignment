const http = require('http');

const TOKEN = 'mock-token';
const USERS = {};

function genCaptcha() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let s = '';
  for (let i = 0; i < 4; i++) s += chars[Math.floor(Math.random() * chars.length)];
  return s;
}

function makeUser(username, role, password) {
  const id = Object.keys(USERS).length + 1;
  USERS[username] = { id, username, role, password, name: username, email: `${username}@mock.dev` };
}

makeUser('admin', 'admin', '123456');
makeUser('hr', 'hr', '123456');
makeUser('candidate', 'candidate', '123456');

function send(req, code, data) {
  req.res.writeHead(code, { 'Content-Type': 'application/json' });
  req.res.end(JSON.stringify(data));
}

function auth(req) {
  const h = req.headers['authorization'] || '';
  const token = h.replace(/^Bearer\s+/, '');
  if (token !== TOKEN) {
    send(req, 401, { detail: 'unauthorized' });
    return null;
  }
  return true;
}

function currentUser(req) {
  const u = req.headers['x-user'];
  return USERS[u] || USERS['admin'];
}

const ROUTES = {
  'POST /api/auth/register': (req, body) => {
    const { username, password, role } = body;
    if (USERS[username]) return send(req, 400, { detail: '用户名已存在' });
    makeUser(username, role || 'candidate', password);
    send(req, 200, { id: USERS[username].id, username, role: USERS[username].role });
  },
  'GET /api/auth/captcha': (req) => send(req, 200, { captcha_id: 'cap-' + Date.now(), captcha_text: genCaptcha() }),
  'POST /api/auth/login': (req, body) => {
    const u = USERS[body.username];
    if (!u || u.password !== body.password) return send(req, 400, { detail: '用户名或密码错误' });
    send(req, 200, { token: TOKEN, user: { id: u.id, username: u.username, role: u.role, name: u.name } });
  },
  'POST /api/auth/logout': (req) => send(req, 200, { ok: true }),
  'GET /api/auth/me': (req) => {
    if (!auth(req)) return;
    const u = currentUser(req);
    send(req, 200, { id: u.id, username: u.username, role: u.role, name: u.name, email: u.email });
  },
  'POST /api/auth/change-password': (req) => send(req, 200, { ok: true }),
  'PUT /api/account': (req, body) => {
    if (!auth(req)) return;
    const u = currentUser(req);
    if (body.name) u.name = body.name;
    if (body.email) u.email = body.email;
    send(req, 200, { ok: true });
  },
  'GET /api/profile/me': (req) => {
    if (!auth(req)) return;
    send(req, 200, {
      id: 1, name: '示例候选人', phone: '13800000000', email: 'cand@mock.dev',
      education: '本科', school: '示例大学', major: '计算机科学与技术',
      graduation_year: 2024, experience_years: 2,
      skills: ['Python', 'Java', 'SQL', '机器学习'],
      certificates: ['PMP', 'AWS 认证'],
      resume_text: '示例简历正文...',
      avatar: '',
      intent_jobs: ['后端工程师', '算法工程师']
    });
  },
  'PUT /api/profile/me': (req) => send(req, 200, { ok: true }),
  'GET /api/hr/candidates': (req) => send(req, 200, [
    { id: 1, name: '张三', role: 'candidate', email: 'z3@mock.dev', applied_job: '后端工程师', match_score: 87, status: 'reviewing' },
    { id: 2, name: '李四', role: 'candidate', email: 'l4@mock.dev', applied_job: '算法工程师', match_score: 92, status: 'matched' },
    { id: 3, name: '王五', role: 'candidate', email: 'w5@mock.dev', applied_job: '前端工程师', match_score: 76, status: 'pending' }
  ]),
  'GET /api/overview/summary': (req) => send(req, 200, {
    total_jobs: 128, total_skills: 562, total_resumes: 43, total_candidates: 12,
    total_edges: 1820, communities: 8,
    job_trend: [
      { month: '1月', count: 12 }, { month: '2月', count: 18 }, { month: '3月', count: 25 },
      { month: '4月', count: 31 }, { month: '5月', count: 28 }, { month: '6月', count: 35 }
    ],
    skill_hot: [
      { name: 'Python', value: 95 }, { name: 'Java', value: 88 }, { name: '机器学习', value: 82 },
      { name: 'SQL', value: 78 }, { name: '大模型', value: 70 }, { name: 'Kubernetes', value: 65 }
    ],
    recent_matches: [
      { id: 1, candidate: '张三', job: '后端工程师', score: 87 },
      { id: 2, candidate: '李四', job: '算法工程师', score: 92 },
      { id: 3, candidate: '王五', job: '前端工程师', score: 76 }
    ]
  }),
  'GET /api/datasets': (req) => send(req, 200, [
    { id: 1, name: '招聘 JD 数据集 v1', source: '智联招聘', count: 1024, status: 'active', updated: '2026-06-01' },
    { id: 2, name: '简历语料 v2', source: '内部', count: 538, status: 'active', updated: '2026-06-15' },
    { id: 3, name: '能力图谱种子库', source: 'ESCO', count: 3200, status: 'archived', updated: '2026-05-10' }
  ]),
  'POST /api/jd/parse': (req, body) => send(req, 200, {
    title: '后端工程师', company: '示例科技', department: '技术部', location: '北京',
    salary: '25-45k', experience: '3-5年', education: '本科及以上',
    responsibilities: ['负责后端服务设计与开发', '优化系统性能', '参与系统架构设计'],
    requirements: ['熟练掌握 Python/Java', '熟悉 MySQL/Redis', '了解微服务架构'],
    skills: [
      { name: 'Python', level: 'advanced', required: true },
      { name: 'Java', level: 'intermediate', required: true },
      { name: 'MySQL', level: 'advanced', required: true },
      { name: 'Redis', level: 'intermediate', required: false },
      { name: 'Kubernetes', level: 'beginner', required: false }
    ]
  }),
  'GET /api/jobs': (req) => send(req, 200, [
    { id: 1, title: '后端工程师', department: '技术部', count: 5, status: 'active', required_skills: ['Python', 'MySQL', 'Redis'] },
    { id: 2, title: '算法工程师', department: '算法部', count: 3, status: 'active', required_skills: ['Python', '机器学习', 'PyTorch'] },
    { id: 3, title: '前端工程师', department: '技术部', count: 4, status: 'active', required_skills: ['Vue', 'TypeScript', 'CSS'] },
    { id: 4, title: '数据分析师', department: '数据部', count: 2, status: 'paused', required_skills: ['SQL', 'Python', 'Tableau'] }
  ]),
  'GET /api/emerging-jobs': (req) => send(req, 200, [
    { id: 1, title: 'AI Agent 工程师', first_seen: '2026-06', growth: 180, sample_count: 24, related_skills: ['LLM', 'LangChain', 'RAG'] },
    { id: 2, title: '大模型训练工程师', first_seen: '2026-05', growth: 150, sample_count: 18, related_skills: ['PyTorch', '分布式训练', 'CUDA'] },
    { id: 3, title: 'Prompt 工程师', first_seen: '2026-06', growth: 220, sample_count: 32, related_skills: ['Prompt', 'LLM', '评估'] }
  ]),
  'GET /api/job-evolution/1': (req) => send(req, 200, {
    job_id: 1, title: '后端工程师',
    timeline: [
      { version: '2024-Q1', skills: ['Java', 'MySQL', 'Spring'] },
      { version: '2024-Q4', skills: ['Java', 'MySQL', 'Spring', 'Redis', 'Docker'] },
      { version: '2025-Q2', skills: ['Python', 'MySQL', 'Redis', 'Docker', 'Kubernetes'] },
      { version: '2026-Q2', skills: ['Python', 'MySQL', 'Redis', 'Kubernetes', 'LLM 接入'] }
    ],
    added: ['LLM 接入', 'Kubernetes'], removed: ['Spring'], changed: ['Java → Python']
  }),
  'GET /api/skill-graph': (req) => send(req, 200, {
    nodes: [
      { id: 1, name: 'Python', category: 'language', value: 95 },
      { id: 2, name: 'Java', category: 'language', value: 88 },
      { id: 3, name: '机器学习', category: 'domain', value: 82 },
      { id: 4, name: 'MySQL', category: 'database', value: 78 }
    ],
    links: [
      { source: 1, target: 3, value: 5 },
      { source: 2, target: 3, value: 3 },
      { source: 1, target: 4, value: 4 }
    ]
  }),
  'GET /api/graph/full': (req) => send(req, 200, {
    nodes: [
      { id: 'j1', label: '后端工程师', type: 'job', community: 1 },
      { id: 'j2', label: '算法工程师', type: 'job', community: 2 },
      { id: 'j3', label: '前端工程师', type: 'job', community: 3 },
      { id: 's1', label: 'Python', type: 'skill', community: 1 },
      { id: 's2', label: 'Java', type: 'skill', community: 1 },
      { id: 's3', label: '机器学习', type: 'skill', community: 2 },
      { id: 's4', label: 'Vue', type: 'skill', community: 3 },
      { id: 's5', label: 'MySQL', type: 'skill', community: 1 }
    ],
    edges: [
      { source: 'j1', target: 's1' }, { source: 'j1', target: 's2' }, { source: 'j1', target: 's5' },
      { source: 'j2', target: 's1' }, { source: 'j2', target: 's3' },
      { source: 'j3', target: 's4' }
    ],
    stats: { nodes: 8, edges: 6, communities: 3 }
  }),
  'GET /api/graph/stats': (req) => send(req, 200, { nodes: 8, edges: 6, communities: 3, jobs: 3, skills: 5 }),
  'GET /api/graph/communities': (req) => send(req, 200, [
    { id: 1, label: '后端技术栈', size: 4, color: '#5470c6' },
    { id: 2, label: '算法/机器学习', size: 2, color: '#91cc75' },
    { id: 3, label: '前端技术栈', size: 2, color: '#fac858' }
  ]),
  'GET /api/graph/path': (req) => send(req, 200, {
    path: ['j1', 's1', 'j2'], length: 2,
    nodes: [
      { id: 'j1', label: '后端工程师', type: 'job' },
      { id: 's1', label: 'Python', type: 'skill' },
      { id: 'j2', label: '算法工程师', type: 'job' }
    ]
  }),
  'GET /api/graph/search': (req) => send(req, 200, [
    { id: 'j1', label: '后端工程师', type: 'job' },
    { id: 's1', label: 'Python', type: 'skill' }
  ]),
  'GET /api/evolution/timeline': (req) => send(req, 200, [
    { period: '2024-Q1', added: 8, removed: 2, changed: 4 },
    { period: '2024-Q4', added: 12, removed: 3, changed: 6 },
    { period: '2025-Q2', added: 15, removed: 5, changed: 8 },
    { period: '2026-Q2', added: 22, removed: 7, changed: 12 }
  ]),
  'GET /api/evolution/hotspot': (req) => send(req, 200, [
    { skill: 'LLM', growth: 320, mentions: 145 },
    { skill: 'Kubernetes', growth: 180, mentions: 98 },
    { skill: 'RAG', growth: 280, mentions: 76 },
    { skill: 'Vue 3', growth: 95, mentions: 65 }
  ]),
  'GET /api/evolution/compare': (req) => send(req, 200, {
    jobs: ['后端工程师', '算法工程师'],
    series: [
      { name: '后端工程师', data: [12, 18, 25, 31] },
      { name: '算法工程师', data: [8, 15, 22, 35] }
    ],
    periods: ['2024-Q1', '2024-Q4', '2025-Q2', '2026-Q2']
  }),
  'GET /api/evolution/version-compare': (req) => send(req, 200, {
    v1: '2024-Q1', v2: '2026-Q2',
    added: ['LLM 接入', 'Kubernetes', 'RAG'], removed: ['Spring', 'JSP'], changed: ['Java → Python']
  }),
  'GET /api/graph/evidence': (req) => send(req, 200, [
    { source: 'JD-1024', snippet: '熟练使用 Python 进行后端开发，熟悉 Flask/Django...', url: '#' },
    { source: '简历-23', snippet: '3 年 Python 后端经验，主导过微服务改造...', url: '#' }
  ]),
  'GET /api/evaluation/report': (req) => send(req, 200, {
    generated_at: '2026-07-22',
    metrics: [
      { task: 'JD 解析', precision: 0.92, recall: 0.88, f1: 0.90 },
      { task: '简历解析', precision: 0.89, recall: 0.85, f1: 0.87 },
      { task: '人岗匹配', precision: 0.86, recall: 0.82, f1: 0.84 }
    ]
  }),
  'POST /api/resume/parse': (req, body) => send(req, 200, {
    name: '张三', phone: '13800000000', email: 'z3@mock.dev',
    education: '本科', school: '示例大学', major: '计算机科学与技术', graduation_year: 2024,
    experience_years: 2,
    experience: [
      { company: '示例科技', role: '后端工程师', duration: '2024.07-至今', desc: '负责微服务后端开发与维护' }
    ],
    skills: [
      { name: 'Python', level: 'advanced' },
      { name: 'MySQL', level: 'advanced' },
      { name: 'Redis', level: 'intermediate' },
      { name: 'Docker', level: 'intermediate' }
    ],
    certificates: ['PMP']
  }),
  'POST /api/match-analysis': (req, body) => send(req, 200, {
    overall_score: 87,
    dimensions: [
      { name: '技能匹配', score: 90, detail: '核心技能命中 4/5' },
      { name: '经验匹配', score: 85, detail: '2 年经验，满足最低要求' },
      { name: '学历匹配', score: 100, detail: '本科及以上，已满足' },
      { name: '证书加分', score: 60, detail: 'PMP 部分加分' }
    ],
    matched: ['Python', 'MySQL', 'Redis', 'Docker'],
    missing: ['Kubernetes'],
    strengths: ['Python 经验丰富', '有微服务经验'],
    gaps: ['缺少 Kubernetes 实战经验'],
    suggestion: '建议补充 Kubernetes 相关项目经验，可考虑安排学习路径。'
  }),
  'GET /api/learning-path/1': (req) => send(req, 200, {
    target_role: '后端工程师',
    current_skills: ['Python', 'MySQL'],
    target_skills: ['Kubernetes', 'Redis', 'LLM 接入'],
    path: [
      { step: 1, skill: 'Redis', resource: 'Redis 设计与实现', estimated_hours: 20, difficulty: '中' },
      { step: 2, skill: 'Kubernetes', resource: 'K8s 官方教程', estimated_hours: 40, difficulty: '高' },
      { step: 3, skill: 'LLM 接入', resource: 'LangChain 实战', estimated_hours: 30, difficulty: '中' }
    ],
    total_hours: 90
  }),
  'GET /api/review-tasks': (req) => send(req, 200, [
    { id: 1, type: 'jd_parse', target: 'JD-1024', content: '后端工程师 JD', status: 'pending', created: '2026-07-20' },
    { id: 2, type: 'resume_parse', target: '简历-23', content: '张三简历', status: 'pending', created: '2026-07-21' },
    { id: 3, type: 'new_job', target: 'AI Agent 工程师', content: '新岗位发现待确认', status: 'pending', created: '2026-07-22' }
  ]),
  'GET /api/evaluation/metrics': (req) => send(req, 200, {
    tasks: [
      { name: 'JD 解析', precision: 0.92, recall: 0.88, f1: 0.90, samples: 50 },
      { name: '简历解析', precision: 0.89, recall: 0.85, f1: 0.87, samples: 50 },
      { name: '人岗匹配', precision: 0.86, recall: 0.82, f1: 0.84, samples: 30 }
    ],
    summary: { avg_f1: 0.87, total_samples: 130 }
  }),
  'GET /api/resumes': (req) => send(req, 200, [
    { id: 1, name: '张三', applied_job: '后端工程师', status: 'parsed', score: 87 },
    { id: 2, name: '李四', applied_job: '算法工程师', status: 'parsed', score: 92 },
    { id: 3, name: '王五', applied_job: '前端工程师', status: 'parsed', score: 76 }
  ]),
  'GET /api/ai/status': (req) => send(req, 200, {
    provider: 'mock', model: 'mock-llm', available: true, fallback_count: 0
  }),
  'POST /api/ai/analyze': (req, body) => send(req, 200, {
    result: `针对 ${body.task_type} 的分析结果（mock）`, fallback: false
  }),
  'POST /api/digital-interviewer/interview': (req, body) => send(req, 200, {
    stage: body.stage || 'opening',
    question: '请简要介绍一下您过往最有挑战的一个项目。',
    summary: '', finished: false
  })
};

const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  const path = url.pathname;
  const method = req.method;
  const key = `${method} ${path}`;
  const reqCtx = { req, res, headers: req.headers };
  reqCtx.res = res;

  // carry x-user from query? we just default admin
  reqCtx.headers['x-user'] = 'admin';

  const m = path.match(/^\/api\/review-tasks\/(\d+)\/(approve|reject)$/);
  if (m) return send(reqCtx, 200, { ok: true });

  const m2 = path.match(/^\/api\/job-evolution\/(\d+)$/);
  if (m2) return ROUTES['GET /api/job-evolution/1'](reqCtx);

  const m3 = path.match(/^\/api\/learning-path\/(\d+)$/);
  if (m3) return ROUTES['GET /api/learning-path/1'](reqCtx);

  if (ROUTES[key]) {
    if (method === 'GET') return ROUTES[key](reqCtx);
    let body = '';
    req.on('data', c => body += c);
    req.on('end', () => {
      try { body = body ? JSON.parse(body) : {}; } catch { body = {}; }
      ROUTES[key](reqCtx, body);
    });
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ detail: `mock: ${key} not found` }));
});

server.listen(8000, () => console.log('Mock backend on http://localhost:8000'));

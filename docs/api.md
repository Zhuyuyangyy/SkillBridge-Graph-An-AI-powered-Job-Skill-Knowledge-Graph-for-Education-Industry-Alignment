# API 清单

## 账号与权限

- `POST /api/auth/register` 创建账号，支持 `candidate` 和 `hr` 两种角色
- `GET /api/auth/captcha` 获取注册数学验证码
- `POST /api/auth/login` 登录并返回 Bearer Token
- `POST /api/auth/logout` 退出登录并删除当前会话
- `GET /api/auth/me` 获取当前登录用户
- `POST /api/auth/change-password` 修改密码，成功后清空当前用户所有会话
- `PUT /api/account` 更新账号资料

注册规则：

- 用户名：6-20 位，至少包含英文字母和数字，可使用下划线
- 密码：8-32 位，必须包含数字，并在大写字母、小写字母、特殊符号中至少包含一种
- 需要确认密码，两次密码必须一致
- 邮箱必填且需符合邮箱格式
- 真实姓名必填
- 注册前需通过数学验证码

## 求职者/学生

- `GET /api/profile/me` 获取个人画像
- `PUT /api/profile/me` 更新个人画像

个人画像维度包括基础信息、目标岗位、意向城市、期望薪资、技能、证书、项目经历、实习经历、竞赛奖项和自我总结。

## 企业 HR/管理者

- `GET /api/hr/candidates` 获取候选人列表、个人画像、简历数量和最近简历

该接口仅允许 `hr` 和 `admin` 角色访问。

## 业务接口

- `GET /api/overview/summary`
- `GET /api/datasets`
- `POST /api/jd/parse`
- `GET /api/jobs`
- `GET /api/emerging-jobs`
- `GET /api/job-evolution/{job_id}`
- `GET /api/skill-graph`
- `POST /api/resume/parse`
- `POST /api/match-analysis`
- `GET /api/learning-path/{report_id}`
- `GET /api/review-tasks`
- `POST /api/review-tasks/{id}/approve`
- `POST /api/review-tasks/{id}/reject`
- `GET /api/evaluation/metrics`
- `GET /api/resumes`

## AI 与数字人面试官

- `GET /api/ai/status`
- `POST /api/ai/analyze`
- `POST /api/digital-interviewer/interview`

启动后可访问 `http://localhost:8000/docs` 查看 Swagger 文档。

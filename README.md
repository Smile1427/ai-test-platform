# 在线教育平台AI辅助测试

[![Auto Test](https://github.com/Smile1427/ai-test-platform/actions/workflows/test.yml/badge.svg)](https://github.com/Smile1427/ai-test-platform/actions/workflows/test.yml)

集 **AI 辅助测试生成 + 接口自动化测试 + AI 功能测试 + 性能测试** 于一体的测试开发项目。

被测系统是一个自建的在线教育平台，包含用户、课程、订单、评论、AI 功能五大模块。


## 项目亮点

- **AI 辅助生成测试用例**：输入接口文档，AI 自动生成 52 条测试用例，覆盖正常、异常、边界场景
- **AI 生成测试数据**：自动生成边界值、异常值，覆盖更多测试场景
- **AI 辅助缺陷分析**：失败日志自动分类，输出根因建议，减少人工排查时间
- **AI 功能测试**：测试 AI 生成内容质量、推荐效果、对话逻辑，覆盖 21 条用例
- **接口自动化测试**：YAML 数据驱动 + 自研执行器，52 条用例全部通过
- **性能测试**：3 个场景（基准 50 并发、负载 200 并发、压力 500 并发），发现性能拐点
- **CI/CD 集成**：GitHub Actions 自动执行，每次 push 触发完整测试流水线


## 技术栈

| 层级 | 技术 |
|------|------|
| 被测系统后端 | FastAPI + SQLAlchemy + MySQL + Redis |
| 被测系统前端 | HTML + CSS + JavaScript |
| 接口测试 | Python + Requests + YAML + 自研执行器 |
| AI 功能测试 | Pytest |
| 性能测试 | Locust |
| AI 辅助 | 智谱 AI（glm-4-flash） |
| CI/CD | GitHub Actions |


## 测试数据

| 测试类型 | 用例数 | 通过率 |
|---------|--------|--------|
| 接口自动化测试 | 52 | 100% |
| AI 功能测试 | 21 | 100% |
| 性能测试 | 3 场景 | 全部通过 |


## 项目结构

```
ai-test-platform/
├── backend/                    # 被测系统后端
│   ├── main.py                 # FastAPI 入口
│   ├── database.py             # 数据库连接
│   ├── models.py               # 数据库模型
│   ├── init_data.py            # 初始化数据
│   ├── config.py               # AI API 配置
│   ├── routers/                # API 路由
│   │   ├── user.py             # 用户接口
│   │   ├── course.py           # 课程接口
│   │   ├── order.py            # 订单接口
│   │   ├── comment.py          # 评论接口
│   │   └── ai.py               # AI 功能接口
│   ├── services/               # 业务逻辑
│   │   ├── ai_service.py       # AI 功能实现
│   │   └── study_analysis.py   # AI 学习分析
│   └── requirements.txt
│
├── frontend/                   # 被测系统前端
│   ├── login.html              # 登录页
│   ├── register.html           # 注册页
│   ├── course_list.html        # 课程列表
│   ├── course_detail.html      # 课程详情（含评论）
│   ├── order.html              # 我的订单
│   ├── ai_chat.html            # AI 助手
│   ├── css/style.css
│   └── js/
│
├── ai_assist/                  # AI 辅助测试模块
│   ├── case_generator.py       # AI 生成测试用例
│   ├── data_generator.py       # AI 生成测试数据
│   ├── defect_analyzer.py      # AI 辅助缺陷分析
│   └── config.py
│
├── test_ai/                    # AI 功能测试
│   └── test_ai_features.py     # 21 条 AI 功能测试用例
│
├── tests/                      # 测试代码
│   ├── case_runner.py          # 接口用例执行器
│   ├── report_generator.py     # 测试报告生成
│   ├── fix_expectations.py     # 用例预期修正
│   └── performance/
│       └── locustfile.py       # 性能测试脚本
│
├── test_data/                  # 测试数据
│   ├── interface_doc.txt       # 接口文档（给 AI 读）
│   ├── cases.yaml              # AI 生成的测试用例
│   └── generated_data.json     # AI 生成的测试数据
│
├── reports/                    # 测试报告
│   ├── test_report.html        # 功能测试报告
│   ├── perf_baseline.html      # 基准测试报告
│   ├── perf_load.html          # 负载测试报告
│   └── perf_stress.html        # 压力测试报告
│
├── .github/workflows/test.yml  # CI/CD 配置
├── run_all_tests.py            # 一键测试脚本
└── README.md
```


## 快速开始

### 1. 环境准备

```bash
# MySQL 创建数据库
CREATE DATABASE edu_platform CHARACTER SET utf8mb4;

# 安装 Python 依赖
cd backend
pip install -r requirements.txt
```

### 2. 配置 AI API Key

在 `backend/config.py` 和 `ai_assist/config.py` 里填入智谱 API Key：

```python
import os
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "你的API Key")
```

### 3. 启动后端

```bash
cd backend
uvicorn main:app --reload --port 8000
```

### 4. 启动前端

```bash
cd frontend
python -m http.server 8080
```

浏览器访问 `http://127.0.0.1:8080/login.html`

### 5. 初始化数据

```bash
cd backend
python init_data.py
```

### 6. 一键运行所有测试

```bash
python run_all_tests.py
```


## 核心能力展示

### 1. AI 辅助生成测试用例

输入接口文档，AI 自动生成测试用例：

```bash
python ai_assist/case_generator.py
```

生成的用例保存在 `test_data/cases.yaml`，覆盖正常、异常、边界场景。

### 2. 接口自动化测试

```bash
python tests/case_runner.py
```

读取 YAML 用例，自动发请求、断言、生成报告。

### 3. AI 功能测试

```bash
python -m pytest test_ai/test_ai_features.py -v
```

测试 AI 生成内容质量、推荐效果、对话逻辑。

### 4. 性能测试

```bash
cd tests/performance

# 基准测试（50并发）
locust -f locustfile.py --headless -u 50 -r 5 --run-time 1m --host=http://127.0.0.1:8000 --html=../../reports/perf_baseline.html

# 负载测试（200并发）
locust -f locustfile.py --headless -u 200 -r 20 --run-time 2m --host=http://127.0.0.1:8000 --html=../../reports/perf_load.html

# 压力测试（500并发）
locust -f locustfile.py --headless -u 500 -r 50 --run-time 2m --host=http://127.0.0.1:8000 --html=../../reports/perf_stress.html
```


## 性能测试结果

| 场景 | 并发 | 平均响应 | 95分位 | 错误率 | RPS |
|------|------|---------|--------|--------|-----|
| 基准测试 | 50 | 15ms | 30ms | 0% | 23 |
| 负载测试 | 200 | 29ms | 65ms | 0% | 95 |
| 压力测试 | 500 | 844ms | 1100ms | 0% | 170 |

**结论**：系统性能拐点在 200-500 并发之间，500 并发时响应时间暴涨 29 倍，瓶颈可能在数据库连接池或单进程处理能力。


## CI/CD

项目集成了 GitHub Actions，每次 push 自动执行：

1. 安装依赖
2. 启动 MySQL 和 Redis
3. 初始化数据库
4. 启动后端服务
5. 运行接口测试（52条）
6. 运行 AI 功能测试（21条）
7. 生成测试报告
8. 上传报告为 Artifact


## 测试过程中发现的典型缺陷

| 缺陷 | 现象 | 修复 |
|------|------|------|
| 库存不足未校验 | 库存不足仍返回200 | 加库存校验，返回400 |
| 评论内容超长未校验 | 超长评论返回200 | 加长度校验，返回400 |
| AI空输入未校验 | 空主题返回200 | 加校验，返回400 |
| AI敏感词未过滤 | 敏感问题正常回答 | 加敏感词过滤 |
| 前端 userId 写死 | 多账号评论显示同一用户名 | 登录接口返回真实 user_id |
| 测试数据污染 | 测试评论污染真实数据 | 加清理接口，跑测试前自动清理 |


## 后续优化方向

- 接口测试框架封装成 RequestUtil（统一处理超时、重试、日志）
- 测试报告改用 Allure
- 增加接口依赖场景（多接口链式调用）
- 支持多环境切换（测试、预发布、生产）
- 增加更多性能测试场景（稳定性测试、长时间运行）


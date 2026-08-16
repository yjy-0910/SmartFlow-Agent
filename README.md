# AI Partner

一个基于 DeepSeek 大模型的智能对话伴侣应用，支持个性化设置、会话管理和多轮对话。

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)
![DeepSeek](https://img.shields.io/badge/DeepSeek-V4_Pro-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

##  功能特性

- **个性化 AI 伴侣**：自定义 AI 的昵称和性格，打造专属对话风格
- **会话管理**：自动保存对话历史，支持新建、加载、删除会话
- **智能标题生成**：根据首条消息自动生成会话标题
- **流式思考**：集成 DeepSeek 深度推理模式，提供更高质量的回答
- **本地存储**：会话数据以 JSON 格式保存在本地，隐私安全
- **云端部署**：支持一键部署到 Streamlit Cloud，随时随地访问

## 🛠️ 技术栈

| 类别 | 技术 |
|------|------|
| 前端框架 | Streamlit |
| AI 模型 | DeepSeek V4 Pro |
| API 客户端 | OpenAI Python SDK |
| 数据存储 | 本地 JSON 文件 |
| 部署平台 | Streamlit Community Cloud |

## 📁 项目结构

```
SmartFlow-Agent/
├── ai-partner.py      # 应用入口文件
├── app.py             # 主界面与交互逻辑
├── chat.py            # AI 对话模块（API 调用封装）
├── session.py         # 会话管理模块（增删改查）
├── config.py          # 配置与常量定义
── requirements.txt   # Python 依赖
── session_data/      # 会话数据存储目录（自动创建）
└── README.md          # 项目说明文档
```

##  快速开始

### 环境要求

- Python 3.10 或更高版本
- DeepSeek API Key（[申请地址](https://platform.deepseek.com/)）

### 本地运行

1. 克隆项目

```bash
git clone https://github.com/yjy-0910/SmartFlow-Agent.git
cd SmartFlow-Agent
```

2. 安装依赖

```bash
pip install -r requirements.txt
```

3. 设置 API Key

**方式一：环境变量（推荐）**

```bash
# Windows PowerShell
$env:DEEPSEEK_API_KEY="sk-your-api-key-here"

# macOS / Linux
export DEEPSEEK_API_KEY="sk-your-api-key-here"
```

**方式二：直接修改 config.py**

在 `config.py` 中填入你的 API Key（不推荐，容易泄露）

4. 启动应用

```bash
streamlit run ai-partner.py
```

浏览器会自动打开 `http://localhost:8501`，即可开始使用。

## ☁️ 云端部署

本项目已部署在 [Streamlit Community Cloud](https://share.streamlit.io/)，无需本地环境即可使用。

**在线体验**：[https://smartflow-agent-gn892a3xbvyi5f8aiukrpb.streamlit.app](https://smartflow-agent-gn892a3xbvyi5f8aiukrpb.streamlit.app)

### 自行部署步骤

1. Fork 本仓库到你的 GitHub 账号
2. 访问 [share.streamlit.io](https://share.streamlit.io/)，用 GitHub 账号登录
3. 点击 **New app**，填写：
   - Repository: 你的仓库名
   - Branch: `main`
   - Main file path: `ai-partner.py`
4. 在 **Advanced settings → Secrets** 中添加：

```
DEEPSEEK_API_KEY = "sk-your-api-key-here"
```

5. 点击 **Deploy**，等待部署完成

## 📸 界面预览

### 主界面
![主界面](docs/screenshots/main.png)

### 侧边栏设置
![侧边栏](docs/screenshots/sidebar.png)

### 历史会话管理
![历史会话](docs/screenshots/history.png)

> 📝 截图待补充：运行应用后截取实际界面图片，放入 `docs/screenshots/` 目录

## 🔧 开发指南

### 添加新功能

1. 如果是 UI 相关修改，编辑 `app.py`
2. 如果是对话逻辑修改，编辑 `chat.py`
3. 如果是会话管理修改，编辑 `session.py`
4. 如果是配置项修改，编辑 `config.py`

### 代码规范

- 使用类型注解（Type Hints）
- 每个公共函数添加 docstring
- 错误处理使用 try-except，给用户友好提示
- 遵循 PEP 8 代码风格

##  贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 [MIT License](LICENSE)。

##  联系方式

- GitHub: [@yjy-0910](https://github.com/yjy-0910)
- 邮箱: 2175998607@qq.com

---

**Made with ❤️ by yjy-0910**

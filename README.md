# AI Partner

一个基于 DeepSeek 大模型的智能对话伴侣应用，支持个性化设置、会话管理和多轮对话。

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Gradio](https://img.shields.io/badge/Gradio-6.x-orange.svg)
![DeepSeek](https://img.shields.io/badge/DeepSeek-V4_Pro-green.svg)
![Nginx](https://img.shields.io/badge/Nginx-Reverse_Proxy-009639.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 功能特性

- **个性化 AI 伴侣**：自定义 AI 的昵称和性格，打造专属对话风格
- **会话管理**：自动保存对话历史，支持新建、加载、删除会话
- **智能标题生成**：根据首条消息自动生成会话标题
- **深度推理**：集成 DeepSeek 深度推理模式，提供更高质量的回答
- **本地存储**：会话数据以 JSON 格式保存在本地，隐私安全
- **云服务器部署**：支持部署到阿里云 ECS，通过 Nginx 反向代理对外提供服务

## 技术栈

| 类别 | 技术 |
|------|------|
| 前端框架 | Gradio 6.x |
| AI 模型 | DeepSeek V4 Pro |
| API 客户端 | OpenAI Python SDK |
| 数据存储 | 本地 JSON 文件 |
| 反向代理 | Nginx |
| 部署平台 | 阿里云 ECS (Ubuntu 24.04) |

## 项目结构

```
SmartFlow-Agent/
├── ai-partner.py      # 应用入口文件
├── app.py             # 主界面与交互逻辑（Gradio Blocks）
├── chat.py            # AI 对话模块（API 调用封装）
├── session.py         # 会话管理模块（增删改查）
├── config.py          # 配置与常量定义
├── requirements.txt   # Python 依赖
├── session_data/      # 会话数据存储目录（自动创建）
└── README.md          # 项目说明文档
```

## 快速开始

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
python ai-partner.py
```

浏览器会自动打开 `http://localhost:7860`，即可开始使用。

## 云服务器部署（阿里云 ECS）

本项目支持部署到阿里云 ECS，通过 Nginx 反向代理对外提供 Web 服务。

### 部署架构

```
用户浏览器 → 阿里云安全组(端口80) → Nginx(反向代理) → Gradio应用(端口7860) → DeepSeek API
```

### 部署步骤

1. **创建 ECS 实例**：选择 Ubuntu 24.04，认证方式建议选择「自定义密码」

2. **配置安全组**：添加入方向规则，开放 80 端口（HTTP）和 22 端口（SSH）

3. **安装依赖**

```bash
# 安装 Python 和 Nginx
apt update && apt install -y python3 python3-venv nginx

# 创建项目目录
mkdir -p /opt/ai-partner/app
cd /opt/ai-partner
python3 -m venv venv
```

4. **上传代码**

```bash
# 从本地电脑执行
scp -r 本地项目路径/* root@服务器IP:/opt/ai-partner/app/
```

5. **安装 Python 依赖**

```bash
/opt/ai-partner/venv/bin/pip install -r /opt/ai-partner/app/requirements.txt
```

6. **配置 Nginx 反向代理**

```bash
cat > /etc/nginx/sites-available/ai-partner << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

ln -s /etc/nginx/sites-available/ai-partner /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

7. **启动应用**

```bash
export DEEPSEEK_API_KEY="sk-your-api-key-here"
cd /opt/ai-partner/app
nohup /opt/ai-partner/venv/bin/python ai-partner.py > /opt/ai-partner/app.log 2>&1 &
```

8. **验证部署**

```bash
# 检查进程
ps aux | grep python

# 检查端口
ss -tlnp | grep python

# 测试服务
curl -I http://127.0.0.1:7860
```

### 常用运维命令

```bash
# 查看应用日志
tail -f /opt/ai-partner/app.log

# 重启应用
kill $(ps aux | grep ai-partner | grep -v grep | awk '{print $2}')
export DEEPSEEK_API_KEY="sk-your-api-key-here"
cd /opt/ai-partner/app && nohup /opt/ai-partner/venv/bin/python ai-partner.py > /opt/ai-partner/app.log 2>&1 &

# 更新代码
scp 本地文件 root@服务器IP:/opt/ai-partner/app/文件名
```

## 开发指南

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

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

本项目采用 [MIT License](LICENSE)。

## 联系方式

- GitHub: [@yjy-0910](https://github.com/yjy-0910)
- 邮箱: 2175998607@qq.com

---

**Made with ❤️ by yjy-0910**

# 自动写网文 Agent (Auto-Novel-Writing Agent)

这是一个使用 Google Gemini API 驱动的自动化连载小说生成器。它不仅能创作故事章节，还能自动维护和更新人物关系网与关键剧情记忆。

本项目是一个功能完善的全栈 Web 应用，包含 FastAPI 后端和使用 Vite 构建的现代化前端。

## ✨ 功能特性

- **AI 驱动创作**: 利用 Google Gemini 的强大能力生成富有创意和连贯性的小说章节。
- **人物关系网**: 自动构建和可视化角色之间的关系，并以 JSON 格式输出。
- **长期记忆**: 通过文件（`memory.json`）记录关键的角色设定、剧情节点、线索和世界观，确保故事的长期一致性。
- **Web 用户界面**: 提供一个直观的 Web 界面，可以手动或自动生成章节，并实时查看故事状态。
- **自主写作模式**: Agent 能够根据当前故事上下文，自主提出下一章的主题并进行创作。
- **API 驱动**: 所有功能都通过 FastAPI 暴露为 API，易于集成。

## ⚙️ 安装指南

1.  **克隆仓库**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **安装后端依赖 (Python)**
    ```bash
    pip install -r requirements.txt
    ```

3.  **安装前端依赖 (Node.js & npm)**
    ```bash
    cd frontend
    npm install
    cd ..
    ```

## 🔑 配置

### Google Gemini API Key

本 Agent 需要一个 Google Gemini API 密钥才能工作。

1.  从 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取您的 API 密钥。
2.  将 API 密钥设置为一个环境变量。这是推荐的安全做法，可以避免将密钥硬编码到代码中。

    ```bash
    export GOOGLE_API_KEY='你的-API-密钥'
    ```

## 🚀 如何运行 (开发环境)

为了获得最佳的开发体验（包括前端热重载和 API 代理），请分别启动后端和前端服务器。

1.  **启动后端服务器** (在项目根目录运行):
    ```bash
    uvicorn main:app --reload
    ```
    后端服务将运行在 `http://127.0.0.1:8000`。

2.  **启动前端开发服务器** (在另一个终端中，从项目根目录运行):
    ```bash
    npm run dev --prefix frontend
    ```
    前端开发服务器将运行在 `http://localhost:5173` (或另一个可用端口)。

3.  在浏览器中打开前端显示的 URL (例如 `http://localhost:5173`) 即可开始使用。

## 🏗️ 项目结构

```
.
├── agent.py            # Agent 的核心逻辑 (被 main.py 调用)
├── main.py             # FastAPI 后端服务器
├── frontend/           # Vite 前端项目目录
│   ├── src/            # 前端源代码 (JS, CSS)
│   ├── index.html      # 前端主页
│   ├── package.json    # npm 依赖
│   └── vite.config.js  # Vite 配置文件 (含代理)
├── memory.json         # 长期记忆数据库
├── relations.json      # 人物关系网数据库
├── requirements.txt    # Python 依赖列表
└── README.md           # 本文档
```

## 💡 后续扩展

- **生产环境部署**: 运行 `npm run build --prefix frontend` 来打包前端。FastAPI 会自动从 `frontend/dist` 目录提供服务。
- **使用向量数据库**: 对于非常长的故事，可以将 `memory.json` 替换为真正的向量数据库（如 Faiss 或 ChromaDB），以实现更高效的语义记忆检索。
- **增强自主模式**: 实现更复杂的逻辑来让 Agent 连续创作多个章节，甚至在遇到创作瓶颈时进行自我反思。

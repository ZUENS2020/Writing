# 自动写网文 Agent (Auto-Novel-Writing Agent)

这是一个使用 Google Gemini API 驱动的自动化连载小说生成器。它不仅能创作故事章节，还能自动维护和更新人物关系网与关键剧情记忆。

## ✨ 功能特性

- **AI 驱动创作**: 利用 Google Gemini 的强大能力生成富有创意和连贯性的小说章节。
- **人物关系网**: 自动构建和可视化角色之间的关系，并以 JSON 格式输出。
- **长期记忆**: 通过文件（`memory.json`）记录关键的角色设定、剧情节点、线索和世界观，确保故事的长期一致性。
- **结构化输出**: 每次生成都返回一个包含章节正文、最新人物关系网和记忆更新的结构化 JSON，便于下游应用集成。
- **可扩展性**: 代码结构清晰，易于添加新的记忆类型、输出格式或集成其他服务。

## ⚙️ 安装指南

1.  **克隆仓库**

    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **安装依赖**

    项目使用 `pip` 管理依赖。运行以下命令安装所有必需的库：

    ```bash
    pip install -r requirements.txt
    ```

## 🔑 配置

### Google Gemini API Key

本 Agent 需要一个 Google Gemini API 密钥才能工作。

1.  从 [Google AI Studio](https://aistudio.google.com/app/apikey) 获取您的 API 密钥。
2.  将 API 密钥设置为一个环境变量。这是推荐的安全做法，可以避免将密钥硬编码到代码中。

    -   **Linux / macOS**:
        ```bash
        export GOOGLE_API_KEY='你的-API-密钥'
        ```
    -   **Windows (Command Prompt)**:
        ```bash
        set GOOGLE_API_KEY='你的-API-密钥'
        ```
    -   **Windows (PowerShell)**:
        ```bash
        $env:GOOGLE_API_KEY='你的-API-密钥'
        ```

    为了方便，您可以将此命令添加到您的 shell 配置文件中（如 `.bashrc`, `.zshrc`）。

## 🚀 如何运行

通过命令行直接运行 `agent.py` 即可启动 Agent。

```bash
python agent.py
```

Agent 将会执行一个内置的示例，生成小说的第一章，并将结构化的 JSON 结果打印到控制台。

### 示例输出

您将看到类似以下的 JSON 输出：

```json
{
  "chapter": "## 第一章：迷雾中的相遇",
  "content": "夜色如墨，艾拉独自走在湿漉漉的街道上，心中充满了不安...",
  "relationship_map": {
    "characters": [
      {
        "id": 1,
        "name": "艾拉",
        "role": "主角",
        "description": "一位勇敢但迷茫的年轻侦探。"
      }
    ],
    "relations": []
  },
  "memory_updates": [
    {
      "type": "角色设定",
      "id": 1,
      "key": "姓名",
      "value": "艾拉"
    },
    {
      "type": "剧情节点",
      "key": "故事开端",
      "value": "艾拉在雨夜的街道上感到不安。"
    }
  ]
}
```

## 🏗️ 项目结构

```
.
├── agent.py            # Agent 的主逻辑
├── memory.json         # 存储长期记忆的数据库文件
├── relations.json      # 存储人物关系网的数据库文件
├── requirements.txt    # Python 依赖列表
└── README.md           # 本文档
```

## 💡 后续扩展

- **集成 Web 框架**: 使用 FastAPI 或 Flask 将 Agent 包装成一个 API 服务，方便前端调用。
- **使用向量数据库**: 对于非常长的故事和复杂的记忆，可以将 `memory.json` 替换为真正的向量数据库（如 Faiss 或 ChromaDB），以实现更高效的语义记忆检索。
- **增强 Prompt 工程**: 优化传递给 Gemini 的 Prompt，以获得更特定风格或更具创意的输出。
- **前端可视化**: 创建一个简单的前端应用，以更友好的方式展示章节内容和人物关系图。

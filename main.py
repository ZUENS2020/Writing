import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# 从 agent 模块导入核心类和数据模型
from agent import NovelAgent, ChapterOutput, RelationshipMap

# --- FastAPI 应用设置 ---

app = FastAPI(
    title="自动写网文 Agent API",
    description="一个用于自动生成连载小说、管理人物关系和长期记忆的 API。",
    version="1.0.0",
)

# --- 应用启动时创建 Agent 单例 ---
# 使用 try-except 块来处理初始化时可能出现的错误（例如 API Key 未设置）
try:
    agent = NovelAgent()
except ValueError as e:
    # 如果 agent 初始化失败，我们可以在 API层面优雅地报告问题
    # 而不是让整个应用崩溃。
    agent = None
    print(f"严重警告: NovelAgent 初始化失败: {e}")
    print("API 将会运行，但所有端点都会返回错误。")


# --- API 请求/响应模型 ---

class ChapterRequest(BaseModel):
    """生成新章节的请求体"""
    topic: str = Field(..., description="新章节的故事主题或概要", example="主角发现了一把古老的钥匙，上面刻着神秘的符文。")

class AppState(BaseModel):
    """整个应用的状态"""
    memory: list
    relations: RelationshipMap


# --- API 端点 (Endpoints) ---

@app.on_event("startup")
async def startup_event():
    """应用启动事件。可以在这里添加额外的初始化逻辑。"""
    if agent is None:
        print("应用启动，但 Agent 未初始化。")
    else:
        print("应用启动，NovelAgent 已成功初始化。")

@app.post("/chapter", response_model=ChapterOutput, tags=["小说生成"])
async def create_chapter(request: ChapterRequest):
    """
    根据给定的主题生成一个新的小说章节。
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="服务不可用：NovelAgent 未能初始化。请检查服务器日志和配置。")

    try:
        chapter_data = agent.generate_chapter(request.topic)
        if chapter_data is None:
            raise HTTPException(status_code=500, detail="生成章节失败。可能是 Gemini API 或响应解析出现问题。")
        return chapter_data
    except Exception as e:
        # 捕获其他潜在的运行时错误
        raise HTTPException(status_code=500, detail=f"生成过程中发生未知错误: {str(e)}")

@app.get("/state", response_model=AppState, tags=["状态查询"])
async def get_current_state():
    """
    获取当前小说的完整状态，包括所有长期记忆和人物关系网。
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="服务不可用：NovelAgent 未能初始化。")

    memory = agent.load_memory()
    relations = agent.load_relations()
    return AppState(memory=memory, relations=relations)

@app.post("/autonomous_step", response_model=ChapterOutput, tags=["自主写作"])
async def run_autonomous_step():
    """
    执行一个完整的自主写作步骤：
    1. Agent 自主提出下一个章节的主题。
    2. Agent 根据该主题生成新的章节。
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="服务不可用：NovelAgent 未能初始化。")

    # 1. 提出主题
    topic = agent.propose_next_topic()
    if not topic:
        raise HTTPException(status_code=500, detail="未能生成下一个主题。")

    # 2. 生成章节
    chapter_data = agent.generate_chapter(topic)
    if chapter_data is None:
        raise HTTPException(status_code=500, detail="根据自主生成的主题未能成功生成章节。")

    return chapter_data

# --- 静态文件服务 ---
# 这部分用于生产环境。它将 'frontend/dist' 目录（由 `npm run build` 生成）挂载到根路径。
# 在开发环境中，Vite 开发服务器会处理前端文件的服务。
# 必须放在所有 API 路由之后
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static_root")

# --- 运行服务器 ---
# 如果直接运行此文件，则启动 uvicorn 服务器
# 推荐的生产环境启动方式是: uvicorn main:app --reload
if __name__ == "__main__":
    print("--- 通过 `python main.py` 启动开发服务器 ---")
    print("请注意：这主要用于快速测试。推荐使用 `uvicorn main:app --reload` 命令启动。")
    uvicorn.run(app, host="0.0.0.0", port=8000)

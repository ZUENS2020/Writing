import os
import json
from typing import List, Optional, Dict

import google.generativeai as genai
from pydantic import BaseModel, Field, ValidationError
from tinydb import TinyDB, Query

# --- Pydantic 数据模型定义 ---
# 用于强制 Gemini 输出的 JSON 结构，并进行数据验证

class Character(BaseModel):
    """角色模型"""
    id: int = Field(..., description="角色的唯一标识符")
    name: str = Field(..., description="角色姓名")
    role: str = Field(..., description="角色在故事中的主要身份或作用")
    description: str = Field(..., description="角色的简要描述")

class Relation(BaseModel):
    """关系模型"""
    # 使用别名 'from' 和 'to' 以匹配原始 JSON 格式，同时避免 Python 关键字冲突
    source: int = Field(..., alias="from", description="关系发起方的角色 ID")
    target: int = Field(..., alias="to", description="关系指向方的角色 ID")
    type: str = Field(..., description="关系类型（例如：朋友、敌人、家人、爱人）")

class RelationshipMap(BaseModel):
    """完整的人物关系图"""
    characters: List[Character]
    relations: List[Relation]

class MemoryUpdate(BaseModel):
    """长期记忆更新条目"""
    type: str = Field(..., description="记忆类型（例如：角色设定, 剧情节点, 线索, 世界观）")
    id: Optional[int] = Field(None, description="如果记忆与特定角色相关，则为该角色的 ID")
    key: str = Field(..., description="记忆条目的关键名")
    value: str = Field(..., description="记忆条目的具体内容")

class ChapterOutput(BaseModel):
    """最终输出的完整结构"""
    chapter: str = Field(..., description="新章节的标题，例如：'## 第一章：新的开始'")
    content: str = Field(..., description="新章节的正文内容")
    relationship_map: RelationshipMap = Field(..., description="更新后的人物关系网")
    memory_updates: List[MemoryUpdate] = Field(..., description="本次生成所带来的所有记忆更新")


# --- Agent 主逻辑 ---

class NovelAgent:
    """自动写网文 Agent"""

    def __init__(self, memory_db_path="memory.json", relations_db_path="relations.json"):
        """
        初始化 Agent.
        - 配置 API Key
        - 初始化 Gemini 模型
        - 连接到 TinyDB 数据库
        """
        # 1. 配置 API
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("未找到 GOOGLE_API_KEY 环境变量。请按照 README 设置 API Key。")
        genai.configure(api_key=self.api_key)

        # 2. 初始化 Gemini Pro 模型
        self.model = genai.GenerativeModel('gemini-pro')

        # 3. 连接到数据库
        self.memory_db = TinyDB(memory_db_path, indent=4, ensure_ascii=False)
        self.relations_db = TinyDB(relations_db_path, indent=4, ensure_ascii=False)

    def _call_gemini(self, prompt: str) -> str:
        """
        调用 Gemini API 并返回文本响应。
        包含基本的重试和错误处理。
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # 在 API 服务中，最好使用日志记录代替打印
            # import logging
            # logging.error(f"调用 Gemini API 时发生错误: {e}")
            print(f"调用 Gemini API 时发生错误: {e}") # 暂时保留 print 用于调试
            return ""

    def load_memory(self) -> List[Dict]:
        """从数据库加载所有长期记忆。"""
        return self.memory_db.all()

    def save_memory(self, updates: List[MemoryUpdate]):
        """将新的记忆更新保存到数据库。使用 upsert 逻辑。"""
        Memory = Query()
        for update in updates:
            # 基于 type, id, key 查找并更新/插入
            self.memory_db.upsert(
                update.model_dump(),
                (Memory.type == update.type) &
                (Memory.id == update.id) &
                (Memory.key == update.key)
            )

    def load_relations(self) -> RelationshipMap:
        """从数据库加载人物关系网。"""
        data = self.relations_db.all()
        if not data:
            return RelationshipMap(characters=[], relations=[])
        # 假设整个关系网存储为单个文档
        return RelationshipMap.model_validate(data[0])

    def save_relations(self, relation_map: RelationshipMap):
        """将更新后的人物关系网完整覆盖回数据库。"""
        self.relations_db.truncate()  # 清空旧数据
        self.relations_db.insert(relation_map.model_dump())

    def _build_prompt(self, topic: str, memory: List[dict], relations: RelationshipMap) -> str:
        """构建用于生成章节的详细 Prompt。"""

        # 将 Pydantic 模型转换为 JSON Schema 字符串，用于指导 Gemini
        json_schema = json.dumps(ChapterOutput.model_json_schema(), indent=2, ensure_ascii=False)

        # 将当前记忆和关系转换为易于阅读的字符串
        memory_str = "\n".join([f"- {m['type']} ({m['key']}): {m['value']}" for m in memory]) if memory else "无"
        relations_str = relations.model_dump_json(indent=2, ensure_ascii=False)

        prompt = f"""
你是一位富有创造力的小说家。你的任务是根据我提供的故事主题、长期记忆和人物关系，创作下一章节。
在创作时，你必须更新长期记忆和人物关系网，并将所有内容以一个严格的 JSON 格式返回。

**故事主题:**
{topic}

**当前的长期记忆:**
{memory_str}

**当前的人物关系网:**
{relations_str}

**你的任务:**
1.  根据上述所有信息，创作一个新的、引人入胜的章节。
2.  在创作过程中，如果引入了新角色或现有角色的关系发生了变化，请更新人物关系网。
3.  记录本次章节中出现的新的关键信息（如新角色设定、关键剧情节点、新线索等）作为记忆更新。
4.  将所有结果格式化为一个 JSON 对象，该对象必须严格遵守以下 JSON Schema。不要在 JSON 对象前后添加任何额外的解释或文本。

**输出 JSON Schema:**
```json
{json_schema}
```

请立即开始创作，并只返回符合上述 Schema 的 JSON 对象。
"""
        return prompt

    def generate_chapter(self, topic: str) -> Optional[ChapterOutput]:
        """
        生成新章节的主函数。
        """
        # 1. 加载当前状态
        current_memory = self.load_memory()
        current_relations = self.load_relations()

        # 2. 构建 Prompt
        prompt = self._build_prompt(topic, current_memory, current_relations)

        # 3. 调用 LLM
        response_text = self._call_gemini(prompt)
        if not response_text:
            # 可以在这里增加日志
            return None

        # 4. 解析和验证响应
        try:
            # 从返回的文本中提取 JSON 部分
            # 这种方式比简单的 split 更健壮
            start = response_text.find('```json') + len('```json')
            end = response_text.rfind('```')
            if start == -1 or end == -1:
                json_str = response_text
            else:
                json_str = response_text[start:end].strip()

            # 使用 Pydantic 模型进行验证
            output = ChapterOutput.model_validate_json(json_str)

        except (json.JSONDecodeError, ValidationError) as e:
            print(f"!!! Gemini 响应解析失败: {e}")
            print(f"--- 原始响应 ---\n{response_text}\n-----------------")
            return None

        # 5. 更新并保存状态
        self.save_relations(output.relationship_map)
        self.save_memory(output.memory_updates)

        # 6. 返回结果
        return output

    def propose_next_topic(self) -> Optional[str]:
        """
        让 LLM 根据当前故事状态，提出下一个章节的主题。
        """
        print("--- 正在请求下一个章节的主题建议 ---")
        current_memory = self.load_memory()
        current_relations = self.load_relations()

        if not current_memory:
            return "故事刚刚开始，请随意发挥。"

        memory_str = "\n".join([f"- {m['type']} ({m['key']}): {m['value']}" for m in current_memory])

        prompt = f"""
你是一位经验丰富的文学编辑和剧情规划师。
你的任务是根据下面提供的现有故事记忆，为小说的下一章想出一个简短、有悬念、且合乎逻辑的主题。

**现有故事记忆:**
{memory_str}

**你的任务:**
请只返回一个你认为最合适的下一章主题句，不需要任何额外的解释或修饰。
例如: "主角决定调查那个神秘符号的来源，却发现它与一个古老的秘密组织有关。"
"""

        try:
            response = self._call_gemini(prompt)
            # 清理一下返回的文本，移除可能的引号
            return response.strip().strip('"')
        except Exception as e:
            print(f"主题建议生成失败: {e}")
            return None

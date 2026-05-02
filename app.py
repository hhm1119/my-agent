"""笔记管理助手 - Gradio 聊天界面"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver
import gradio as gr

from notes_manager import (
    create_note as _create, read_note as _read,
    update_note as _update, delete_note as _delete,
    list_notes as _list, search_notes as _search,
)

load_dotenv()

# ========== 工具 ==========
@tool
def create_note(title: str, content: str, tags: str = "") -> str:
    """创建一条新笔记。title=标题, content=内容, tags=逗号分隔的标签（可选）"""
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
    return _create(title, content, tag_list)

@tool
def read_note(note_id: int) -> str:
    """根据笔记ID读取笔记内容"""
    return _read(note_id)

@tool
def update_note(note_id: int, title: str = "", content: str = "", tags: str = "") -> str:
    """更新笔记。只传需要修改的字段"""
    kwargs = {}
    if title:
        kwargs["title"] = title
    if content:
        kwargs["content"] = content
    if tags:
        kwargs["tags"] = [t.strip() for t in tags.split(",") if t.strip()]
    return _update(note_id, **kwargs) if kwargs else "请提供要修改的内容"

@tool
def delete_note(note_id: int) -> str:
    """根据笔记ID删除笔记"""
    return _delete(note_id)

@tool
def list_notes(tag: str = "") -> str:
    """列出所有笔记。可用 tag 参数按标签筛选"""
    return _list(tag if tag else None)

@tool
def search_notes(query: str) -> str:
    """搜索笔记标题和内容"""
    return _search(query)

tools = [create_note, read_note, update_note, delete_note, list_notes, search_notes]

# ========== Agent ==========
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
    temperature=0,
)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "你是个人笔记管理助手。你可以帮助用户创建、查看、修改、删除和搜索笔记。\n"
        "使用工具与用户交流时用中文回复。\n"
        "笔记有标题、内容和标签。\n"
        '如果用户问"有哪些笔记"用 list_notes；搜索用 search_notes。'
    ),
    checkpointer=MemorySaver(),
)


# ========== Chat 函数 ==========
def chat(message, history):
    # thread_id 固定为 default，同一会话内上下文持续累积
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config={"configurable": {"thread_id": "default"}},
    )
    return result["messages"][-1].content


# ========== Gradio 界面 ==========
gr.ChatInterface(
    fn=chat,
    title="个人笔记管理助手",
    description="创建、查看、修改、删除和搜索你的笔记。",
    examples=[
        "创建一篇笔记标题为学习计划内容为本周学习LangChain标签为学习",
        "列出所有笔记",
        "搜索笔记LangChain",
    ],
).launch()

"""个人笔记管理助手 - LangChain Agent"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver

from notes_manager import (
    create_note as _create,
    read_note as _read,
    update_note as _update,
    delete_note as _delete,
    list_notes as _list,
    search_notes as _search,
)

load_dotenv()

# ========== 1. 初始化 LLM ==========
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
    temperature=0,
)

# ========== 2. 定义工具 ==========
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
    """更新笔记。只传需要修改的字段，留空的字段保持不变"""
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

# ========== 3. 创建 Agent ==========
system_prompt = (
    "你是个人笔记管理助手。你可以帮助用户创建、查看、修改、删除和搜索笔记。\n"
    "使用工具与用户交流时用中文回复。\n"
    "笔记有标题、内容和标签。\n"
    '如果用户问"有哪些笔记"用 list_notes；搜索用 search_notes。'
)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    checkpointer=MemorySaver(),
    debug=True,
)


# ========== 4. 交互 CLI ==========
def main():
    print("个人笔记管理助手（输入 q 退出）")
    print("-" * 40)
    while True:
        user_input = input("\n你：").strip()
        if user_input.lower() in ("q", "quit", "exit"):
            print("再见！")
            break
        if not user_input:
            continue

        result = agent.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            config={"configurable": {"thread_id": "default"}},
        )
        print(f"\n助手：{result['messages'][-1].content}")


if __name__ == "__main__":
    main()

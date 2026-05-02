"""笔记存储层：基于 JSON 文件的 CRUD"""

import json
import os
from datetime import datetime
from typing import Optional

DATA_FILE = "notes.json"


def _load():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(notes):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)


def _next_id(notes):
    return max((n["id"] for n in notes), default=0) + 1


def create_note(title: str, content: str, tags: Optional[list[str]] = None) -> str:
    """创建一条新笔记"""
    notes = _load()
    note = {
        "id": _next_id(notes),
        "title": title,
        "content": content,
        "tags": tags or [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    notes.append(note)
    _save(notes)
    return f"[OK] 笔记已创建 (ID: {note['id']})"


def read_note(note_id: int) -> str:
    """根据 ID 读取笔记"""
    notes = _load()
    for n in notes:
        if n["id"] == note_id:
            tags = ", ".join(n["tags"]) if n["tags"] else "无"
            return (
                f"ID: {n['id']}\n"
                f"标题: {n['title']}\n"
                f"标签: {tags}\n"
                f"创建: {n['created_at']}\n"
                f"更新: {n['updated_at']}\n"
                f"---\n{n['content']}"
            )
    return f"[ERR] 未找到 ID 为 {note_id} 的笔记"


def update_note(note_id: int, title: str = None, content: str = None, tags: list[str] = None) -> str:
    """更新笔记内容"""
    notes = _load()
    for n in notes:
        if n["id"] == note_id:
            if title is not None:
                n["title"] = title
            if content is not None:
                n["content"] = content
            if tags is not None:
                n["tags"] = tags
            n["updated_at"] = datetime.now().isoformat()
            _save(notes)
            return f"[OK] 笔记 {note_id} 已更新"
    return f"[ERR] 未找到 ID 为 {note_id} 的笔记"


def delete_note(note_id: int) -> str:
    """删除一条笔记"""
    notes = _load()
    for i, n in enumerate(notes):
        if n["id"] == note_id:
            del notes[i]
            _save(notes)
            return f"[OK] 笔记 {note_id} 已删除"
    return f"[ERR] 未找到 ID 为 {note_id} 的笔记"


def list_notes(tag: str = None) -> str:
    """列出所有笔记，可按标签筛选"""
    notes = _load()
    if tag:
        notes = [n for n in notes if tag in n["tags"]]

    if not notes:
        return "[INFO] 暂无笔记"

    lines = [f"共 {len(notes)} 条笔记：\n"]
    for n in notes:
        tags = f"[{', '.join(n['tags'])}]" if n["tags"] else ""
        lines.append(f"  #{n['id']} {n['title']} {tags}")
    return "\n".join(lines)


def search_notes(query: str) -> str:
    """全文搜索笔记（标题和内容）"""
    notes = _load()
    q = query.lower()
    results = [
        n for n in notes
        if q in n["title"].lower() or q in n["content"].lower()
    ]

    if not results:
        return f"[INFO] 未找到包含「{query}」的笔记"

    lines = [f"找到 {len(results)} 条结果：\n"]
    for n in results:
        lines.append(f"  #{n['id']} {n['title']}")
    return "\n".join(lines)

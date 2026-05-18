#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""长期记忆管理模块"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import hashlib

class MemoryItem:
    """记忆项"""
    
    def __init__(self, id: str, content: str, metadata: Dict[str, Any], 
                 created_at: datetime = None, accessed_at: datetime = None):
        self.id = id
        self.content = content
        self.metadata = metadata
        self.created_at = created_at or datetime.now()
        self.accessed_at = accessed_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat()
        }

class MemoryManager:
    """长期记忆管理器 - 使用文件存储"""
    
    def __init__(self, file_path: str = "memory.json"):
        self.file_path = file_path
        self.memories: Dict[str, MemoryItem] = {}
        self._load_memories()
    
    def _load_memories(self):
        """从文件加载记忆"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for mem_id, mem_data in data.items():
                        self.memories[mem_id] = MemoryItem(
                            id=mem_id,
                            content=mem_data['content'],
                            metadata=mem_data['metadata'],
                            created_at=datetime.fromisoformat(mem_data['created_at']),
                            accessed_at=datetime.fromisoformat(mem_data['accessed_at'])
                        )
            except Exception as e:
                print(f"加载记忆失败: {e}")
                self.memories = {}
    
    def _save_memories(self):
        """保存记忆到文件"""
        data = {mem_id: mem.to_dict() for mem_id, mem in self.memories.items()}
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _generate_id(self, content: str) -> str:
        """生成记忆ID"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()[:16]
    
    def add_memory(self, content: str, metadata: Dict[str, Any] = None) -> str:
        """添加记忆"""
        memory_id = self._generate_id(content)
        metadata = metadata or {}
        now = datetime.now()
        
        self.memories[memory_id] = MemoryItem(
            id=memory_id,
            content=content,
            metadata=metadata,
            created_at=now,
            accessed_at=now
        )
        
        self._save_memories()
        return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[MemoryItem]:
        """获取单个记忆"""
        memory = self.memories.get(memory_id)
        if memory:
            memory.accessed_at = datetime.now()
            self._save_memories()
        return memory
    
    def search_memories(self, query: str, limit: int = 10, threshold: float = 0.1) -> List[MemoryItem]:
        """搜索相关记忆"""
        results = []
        
        for mem_id, memory in self.memories.items():
            if query in memory.content:
                score = self._calculate_similarity(query, memory.content)
                if score >= threshold:
                    memory.accessed_at = datetime.now()
                    results.append(memory)
        
        results.sort(key=lambda x: self._calculate_similarity(query, x.content), reverse=True)
        self._save_memories()
        
        return results[:limit]
    
    def _calculate_similarity(self, query: str, content: str) -> float:
        """计算简单的文本相似度"""
        query_chars = set(query)
        content_chars = set(content)
        
        if not query_chars:
            return 0.0
        
        intersection = query_chars & content_chars
        return len(intersection) / len(query_chars)
    
    def get_recent_memories(self, limit: int = 10) -> List[MemoryItem]:
        """获取最近的记忆"""
        results = sorted(self.memories.values(), key=lambda x: x.created_at, reverse=True)
        return results[:limit]
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
        if memory_id in self.memories:
            del self.memories[memory_id]
            self._save_memories()
            return True
        return False
    
    def clear_all_memories(self):
        """清空所有记忆"""
        self.memories = {}
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
    
    def get_memory_count(self) -> int:
        """获取记忆数量"""
        return len(self.memories)
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取记忆统计信息"""
        if not self.memories:
            return {"total_memories": 0, "first_memory": None, "last_memory": None}
        
        memories = sorted(self.memories.values(), key=lambda x: x.created_at)
        return {
            "total_memories": len(self.memories),
            "first_memory": memories[0].created_at.isoformat(),
            "last_memory": memories[-1].created_at.isoformat()
        }

# 创建全局实例
memory_manager = MemoryManager()

# 便捷函数
def add_memory(content: str, metadata: Dict[str, Any] = None) -> str:
    """添加记忆"""
    return memory_manager.add_memory(content, metadata)

def search_memories(query: str, limit: int = 10) -> List[MemoryItem]:
    """搜索记忆"""
    return memory_manager.search_memories(query, limit)

def get_recent_memories(limit: int = 10) -> List[MemoryItem]:
    """获取最近记忆"""
    return memory_manager.get_recent_memories(limit)

def get_memory_statistics() -> Dict[str, Any]:
    """获取记忆统计"""
    return memory_manager.get_statistics()

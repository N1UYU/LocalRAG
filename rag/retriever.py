"""
检索器模块
封装向量存储的检索逻辑，提供更高级的查询接口。
"""

import logging
from typing import List, Optional, Tuple

from rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """
    检索器，用于从向量库中检索相关文档块。
    """

    def __init__(self, vector_store: VectorStore, top_k: int = 5, score_threshold: Optional[float] = None):
        """
        初始化检索器。

        Args:
            vector_store (VectorStore): 已初始化的向量存储实例
            top_k (int): 默认返回的文档块数量
            score_threshold (Optional[float]): 相似度阈值，低于此值的结果将被过滤
        """
        self.vector_store = vector_store
        self.top_k = top_k
        self.score_threshold = score_threshold

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Tuple[str, float]]:
        """
        检索与查询最相关的文档块。

        Args:
            query (str): 查询文本
            top_k (Optional[int]): 覆盖默认的 top_k

        Returns:
            List[Tuple[str, float]]: 文档块和对应的相似度分数
        """
        if not query or not query.strip():
            logger.warning("查询文本为空，返回空结果")
            return []

        k = top_k if top_k is not None else self.top_k
        logger.info(f"检索查询: {query[:50]}... (top_k={k})")

        try:
            results = self.vector_store.search(query, top_k=k)

            # 应用相似度阈值过滤
            if self.score_threshold is not None:
                results = [(text, score) for text, score in results if score >= self.score_threshold]
                logger.info(f"应用阈值 {self.score_threshold} 过滤后剩余 {len(results)} 个结果")

            logger.info(f"检索完成，返回 {len(results)} 个结果")
            return results

        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []

    def retrieve_context(self, query: str, top_k: Optional[int] = None) -> str:
        """
        检索并将结果拼接为上下文字符串。

        Args:
            query (str): 查询文本
            top_k (Optional[int]): 覆盖默认的 top_k

        Returns:
            str: 拼接后的上下文字符串
        """
        results = self.retrieve(query, top_k)
        if not results:
            return ""

        # 将多个文档块用换行和分隔符拼接，便于 LLM 理解
        context_parts = []
        for i, (text, score) in enumerate(results):
            context_parts.append(f"[文档 {i+1}] (相关度: {score:.3f})\n{text}")

        return "\n\n---\n\n".join(context_parts)
"""
RAG 主流程模块
整合检索、提示构建和 LLM 调用，提供统一的查询接口。
"""

import logging
from typing import Dict, List, Optional, Any

from rag.retriever import Retriever
from rag.prompt import PromptTemplate
from rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


class RAG:
    """
    RAG 系统主控制器，提供端到端的问答能力。
    """

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        retriever: Optional[Retriever] = None,
        top_k: int = 5,
        score_threshold: Optional[float] = None,
        model_name: str = "all-MiniLM-L6-v2",
        llm: Any = None,  # 新增：接收 LLM 实例（如 LocalLLM）
    ):
        """
        初始化 RAG 系统。

        Args:
            vector_store (Optional[VectorStore]): 已初始化的向量存储，若不提供则自动创建
            retriever (Optional[Retriever]): 已初始化的检索器，若不提供则自动创建
            top_k (int): 检索返回的文档块数量
            score_threshold (Optional[float]): 相似度阈值
            model_name (str): 如果自动创建 VectorStore，使用的模型名称
            llm (Any): 可选的 LLM 实例，用于生成回答
        """
        # 初始化向量存储
        if vector_store is None:
            logger.info(f"自动创建 VectorStore，模型: {model_name}")
            self.vector_store = VectorStore(model_name=model_name)
        else:
            self.vector_store = vector_store

        # 初始化检索器
        if retriever is None:
            self.retriever = Retriever(
                self.vector_store,
                top_k=top_k,
                score_threshold=score_threshold
            )
        else:
            self.retriever = retriever

        # 保存 LLM
        self.llm = llm
        if self.llm:
            logger.info("LLM 已接入，将生成真实回答")
        else:
            logger.info("未配置 LLM，将使用占位回答")

        logger.info(f"RAG 系统初始化完成，top_k={top_k}, 阈值={score_threshold}")

    def add_documents(self, texts: List[str]) -> int:
        """
        向知识库添加文档块。

        Args:
            texts (List[str]): 文档块列表

        Returns:
            int: 添加的文档块数量
        """
        return self.vector_store.add_texts(texts)

    def query(self, question: str, top_k: Optional[int] = None) -> Dict[str, Any]:
        """
        执行 RAG 查询。

        Args:
            question (str): 用户问题
            top_k (Optional[int]): 覆盖默认的 top_k

        Returns:
            Dict[str, Any]: 包含以下字段：
                - question: 原始问题
                - context: 检索到的上下文（拼接字符串）
                - prompt: 生成的完整提示
                - results: 检索到的原始结果列表 [(text, score), ...]
                - answer: LLM 回答或占位文本
                - error: 错误信息（如有）
        """
        result = {
            "question": question,
            "context": "",
            "prompt": "",
            "results": [],
            "answer": "",
            "error": None
        }

        if not question or not question.strip():
            result["error"] = "问题不能为空"
            logger.warning(result["error"])
            return result

        try:
            # 1. 检索
            logger.info(f"执行 RAG 查询: {question[:50]}...")
            results = self.retriever.retrieve(question, top_k=top_k)
            result["results"] = results

            if not results:
                result["error"] = "未检索到相关文档，请确认知识库中是否有相关内容"
                logger.warning(result["error"])
                return result

            # 2. 拼接上下文
            context = self.retriever.retrieve_context(question, top_k=top_k)
            result["context"] = context

            # 3. 构建提示
            prompt = PromptTemplate.build_prompt(question, context)
            result["prompt"] = prompt

            # 4. 生成回答
            if self.llm:
                try:
                    logger.info("正在调用 LLM 生成回答...")
                    answer = self.llm.generate(prompt)
                    result["answer"] = answer
                    logger.info("LLM 回答生成成功")
                except Exception as e:
                    logger.error(f"LLM 生成失败: {e}", exc_info=True)
                    result["answer"] = f"LLM 生成失败: {e}"
                    result["error"] = str(e)
            else:
                # 占位回答
                result["answer"] = (
                    f"[占位] 基于以下上下文生成回答：\n{context[:200]}...\n"
                    "（请配置 LLM 后获取完整回答）"
                )

            logger.info(f"RAG 查询完成，检索到 {len(results)} 个结果")
            return result

        except Exception as e:
            result["error"] = f"查询失败: {str(e)}"
            logger.error(result["error"], exc_info=True)
            return result
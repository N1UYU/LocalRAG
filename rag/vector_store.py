"""
向量存储模块
基于 Sentence-Transformers 和 FAISS 实现本地向量索引。
"""

import os
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"   # 添加这一行

import logging
import pickle
from pathlib import Path
from typing import List, Optional, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
# ... 其余代码不变
logger = logging.getLogger(__name__)


class VectorStore:
    """
    本地向量存储，支持添加文本、检索和持久化。
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        index_path: Optional[str] = None,
        device: str = "cpu"
    ):
        """
        初始化向量存储。

        Args:
            model_name (str): Sentence-Transformer 模型名称
            index_path (Optional[str]): 若提供，则从该路径加载已保存的索引和文本
            device (str): "cpu" 或 "cuda"（若 GPU 可用）
        """
        logger.info(f"加载 embedding 模型: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"模型向量维度: {self.dimension}")

        # 存储文本列表，与向量索引一一对应
        self.texts: List[str] = []

        # FAISS 索引：使用内积（IP）或 L2 距离，这里用 IP 即余弦相似度（需要归一化）
        # 为了更接近余弦相似度，我们使用 IndexFlatIP，并在添加/搜索时归一化向量
        self.index = faiss.IndexFlatIP(self.dimension)

        # 如果提供了路径，尝试加载
        if index_path and Path(index_path).exists():
            self.load_index(index_path)

    def add_texts(self, texts: List[str]) -> int:
        """
        添加文本到向量库。

        Args:
            texts (List[str]): 文本列表

        Returns:
            int: 添加的文本数量
        """
        if not texts:
            logger.warning("添加的文本列表为空，跳过")
            return 0

        # 生成向量
        logger.info(f"正在为 {len(texts)} 个文本生成向量...")
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        # 归一化（余弦相似度）
        faiss.normalize_L2(embeddings)

        # 添加向量到索引
        self.index.add(embeddings)
        # 保存文本
        self.texts.extend(texts)

        logger.info(f"成功添加 {len(texts)} 个文本，当前索引总数: {self.index.ntotal}")
        return len(texts)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        搜索与查询最相似的 top_k 个文本。

        Args:
            query (str): 查询文本
            top_k (int): 返回结果数量

        Returns:
            List[Tuple[str, float]]: 列表，每个元素为 (文本, 相似度得分)
        """
        if self.index.ntotal == 0:
            logger.warning("索引为空，无法搜索")
            return []

        # 生成查询向量并归一化
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)

        # 搜索
        scores, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))
        # scores 和 indices 都是二维数组，取第一行
        scores = scores[0]
        indices = indices[0]

        # 组装结果
        results = []
        for idx, score in zip(indices, scores):
            if idx >= 0 and idx < len(self.texts):
                results.append((self.texts[idx], float(score)))
        return results

    def save_index(self, path: str) -> None:
        """
        将索引和文本列表保存到磁盘。

        Args:
            path (str): 保存目录路径（如果不存在则创建）
        """
        save_dir = Path(path)
        save_dir.mkdir(parents=True, exist_ok=True)

        # 保存 FAISS 索引
        index_file = save_dir / "faiss.index"
        faiss.write_index(self.index, str(index_file))

        # 保存文本列表（使用 pickle）
        texts_file = save_dir / "texts.pkl"
        with open(texts_file, "wb") as f:
            pickle.dump(self.texts, f)

        logger.info(f"索引已保存到 {save_dir}，共 {self.index.ntotal} 个向量")

    def load_index(self, path: str) -> None:
        """
        从磁盘加载索引和文本列表。

        Args:
            path (str): 保存目录路径
        """
        load_dir = Path(path)
        index_file = load_dir / "faiss.index"
        texts_file = load_dir / "texts.pkl"

        if not index_file.exists() or not texts_file.exists():
            logger.error(f"索引文件不完整，无法从 {path} 加载")
            return

        # 加载 FAISS 索引
        self.index = faiss.read_index(str(index_file))
        # 加载文本列表
        with open(texts_file, "rb") as f:
            self.texts = pickle.load(f)

        logger.info(f"从 {path} 加载索引成功，共 {self.index.ntotal} 个向量")
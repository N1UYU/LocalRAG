"""
文本切块模块
将长文本切分为适合向量化的小块，支持固定大小切分和重叠。
"""

import logging
from typing import List, Optional

# 配置日志（与 parser 保持一致）
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
    min_chunk_len: int = 10
) -> List[str]:
    """
    将文本按固定大小切分为多个块，并允许重叠。

    Args:
        text (str): 待切分的原始文本
        chunk_size (int): 每个块的最大字符数（默认 500）
        overlap (int): 前后块之间的重叠字符数（默认 50）
        min_chunk_len (int): 最小块长度，小于此值的块将被丢弃（默认 10）

    Returns:
        List[str]: 切分后的文本块列表

    Examples:
        >>> text = "A" * 600 + "B" * 600
        >>> chunks = chunk_text(text, 200, 20)
        >>> print(len(chunks))
        6
    """
    if not text or not isinstance(text, str):
        logger.warning("输入文本为空或非字符串，返回空列表")
        return []

    # 去除首尾空白，但保留内部换行（换行也算字符）
    text = text.strip()
    if len(text) < min_chunk_len:
        logger.info(f"文本长度 {len(text)} 小于最小块长度 {min_chunk_len}，不生成任何块")
        return []

    # 如果文本本身小于 chunk_size，直接返回一个块
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        # 计算当前块的结束位置
        end = start + chunk_size
        if end >= text_len:
            # 最后一块
            chunk = text[start:text_len]
            # 如果最后一块长度大于等于 min_chunk_len 则加入
            if len(chunk) >= min_chunk_len:
                chunks.append(chunk)
            break

        # 尝试在 end 处截断，但为了不切在单词中间（仅对英文有效），
        # 我们简单向后寻找最近的换行或空格（可选），这里为了通用不做复杂处理
        # 直接取 [start:end]
        chunk = text[start:end]
        chunks.append(chunk)

        # 移动到下一块：前进 chunk_size - overlap
        start += chunk_size - overlap

        # 防止死循环（当 overlap >= chunk_size 时）
        if overlap >= chunk_size:
            logger.warning("重叠大小不能大于等于块大小，自动调整为 chunk_size//2")
            overlap = chunk_size // 2

    # 过滤掉过短的块（可能由尾部产生）
    filtered = [c for c in chunks if len(c) >= min_chunk_len]

    logger.info(f"原始文本长度 {text_len} 切分为 {len(filtered)} 个块（平均块大小约 {chunk_size}）")
    return filtered
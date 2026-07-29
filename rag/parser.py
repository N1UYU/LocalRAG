"""
PDF 解析模块
提供从 PDF 文件中提取文本内容的功能。
"""

import logging
from pathlib import Path
from typing import List, Optional

from pypdf import PdfReader


# 配置日志（简单起见，先输出到控制台，后面会统一管理）
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_pdf(file_path: str) -> Optional[str]:
    """
    从 PDF 文件中提取所有页面的文本，合并为一个字符串。

    Args:
        file_path (str): PDF 文件的路径（绝对或相对路径）

    Returns:
        Optional[str]: 如果成功，返回合并后的文本；若出错，返回 None。
                      如果文件不存在或不是 PDF，也会返回 None 并记录错误日志。

    Raises:
        不主动抛出异常，由内部捕获并返回 None。
    """
    # 1. 将字符串转换为 Path 对象，便于操作
    pdf_path = Path(file_path)

    # 2. 检查文件是否存在
    if not pdf_path.exists():
        logger.error(f"文件不存在: {file_path}")
        return None

    # 3. 检查文件扩展名（简单判断）
    if pdf_path.suffix.lower() != ".pdf":
        logger.error(f"不是 PDF 文件: {file_path}")
        return None

    try:
        # 4. 创建 PdfReader 对象
        reader = PdfReader(pdf_path)

        # 5. 提取所有页面的文本
        text_pages = []
        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                text_pages.append(page_text)
            else:
                logger.warning(f"第 {page_num} 页没有提取到文本，可能为扫描件或空白页")

        # 6. 用换行符合并所有页面
        full_text = "\n".join(text_pages)

        # 7. 检查是否提取到内容
        if not full_text.strip():
            logger.warning(f"PDF 文件 {file_path} 提取后为空，可能为纯图片扫描件")
            return None

        logger.info(f"成功从 {file_path} 提取了 {len(text_pages)} 页文本，共 {len(full_text)} 个字符")
        return full_text

    except Exception as e:
        logger.error(f"读取 PDF 文件 {file_path} 时发生异常: {e}")
        return None
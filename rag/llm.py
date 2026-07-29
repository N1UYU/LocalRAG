"""
LLM 调用模块
使用 llama-cpp-python 加载本地 GGUF 模型（支持 Qwen2）。
"""

import logging
from pathlib import Path
from typing import Optional

from llama_cpp import Llama

logger = logging.getLogger(__name__)


class LocalLLM:
    """
    本地 LLM 封装，使用 llama-cpp-python 加载 GGUF 模型。
    """

    def __init__(
        self,
        model_path: str,
        n_ctx: int = 2048,
        n_threads: int = 4,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_tokens: int = 512,
    ):
        """
        初始化 LLM。

        Args:
            model_path (str): GGUF 模型文件路径
            n_ctx (int): 上下文窗口大小
            n_threads (int): CPU 线程数
            temperature (float): 温度参数
            top_p (float): 核采样参数
            max_tokens (int): 最大生成 token 数
        """
        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {model_path}")

        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens

        logger.info(f"加载 GGUF 模型: {model_path}")
        try:
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=False,
                n_gpu_layers=0,  # CPU 推理
            )
            logger.info("模型加载成功")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            raise

    def generate(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
    ) -> str:
        """
        生成回答。

        Args:
            prompt (str): 输入提示
            max_tokens (Optional[int]): 最大生成 token 数
            temperature (Optional[float]): 温度参数
            top_p (Optional[float]): 核采样参数

        Returns:
            str: 生成的回答文本
        """
        try:
            response = self.llm.create_completion(
                prompt=prompt,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                top_p=top_p or self.top_p,
                stop=["\n\n", "用户：", "User:"],
                echo=False
            )
            return response["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"生成失败: {e}")
            return f"生成回答时出错: {e}"
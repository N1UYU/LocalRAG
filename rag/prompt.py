"""
提示模板模块
定义用于 LLM 的提示模板，将上下文和问题组合成完整的指令。
"""

from typing import Optional


class PromptTemplate:
    """
    提示模板类，用于生成结构化的 LLM 提示。
    """

    # 系统提示：定义 LLM 的角色和行为
    SYSTEM_PROMPT = (
        "你是一个专业的技术助手，擅长回答关于云计算、容器化、DevOps 和编程技术的问题。\n"
        "请基于以下提供的上下文信息回答问题。如果上下文信息不足以回答，请明确说明。\n"
        "回答要准确、简洁、有条理。\n"
    )

    # 用户提示模板
    USER_TEMPLATE = """
上下文信息：
{context}

用户问题：
{question}

请基于上述上下文信息回答用户问题。
"""

    @classmethod
    def build_prompt(
        cls,
        question: str,
        context: str,
        system_prompt: Optional[str] = None,
        include_system: bool = True
    ) -> str:
        """
        构建完整的提示。

        Args:
            question (str): 用户问题
            context (str): 检索到的上下文（已拼接的文本）
            system_prompt (Optional[str]): 自定义系统提示，默认使用类变量
            include_system (bool): 是否包含系统提示

        Returns:
            str: 完整的提示字符串
        """
        # 构建用户部分
        user_part = cls.USER_TEMPLATE.format(
            context=context if context else "（未提供相关上下文）",
            question=question
        )

        # 如果包含系统提示
        if include_system:
            sys_prompt = system_prompt if system_prompt else cls.SYSTEM_PROMPT
            return f"{sys_prompt}\n\n{user_part}"
        else:
            return user_part

    @classmethod
    def build_chat_messages(
        cls,
        question: str,
        context: str,
        system_prompt: Optional[str] = None
    ) -> list:
        """
        构建对话消息格式（用于 OpenAI 兼容的 API）。

        Args:
            question (str): 用户问题
            context (str): 检索到的上下文
            system_prompt (Optional[str]): 自定义系统提示

        Returns:
            list: 消息列表，格式为 [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        """
        sys_prompt = system_prompt if system_prompt else cls.SYSTEM_PROMPT
        user_content = cls.USER_TEMPLATE.format(
            context=context if context else "（未提供相关上下文）",
            question=question
        )

        return [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_content}
        ]
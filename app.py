"""
Streamlit 界面
提供 RAG 系统的 Web 交互界面。
"""

import os
import sys
import time  # 新增：用于重试延迟
from pathlib import Path

import streamlit as st
import requests

# 添加项目根目录到 Python 路径（如果直接运行）
sys.path.insert(0, str(Path(__file__).parent))

# 页面配置（必须是第一个 Streamlit 命令）
st.set_page_config(
    page_title="Local RAG 助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API 地址（默认本地 8000 端口）
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def call_rag_api(question: str, top_k: int = 5) -> dict:
    """
    调用 RAG API 查询。

    Args:
        question (str): 用户问题
        top_k (int): 返回文档块数量

    Returns:
        dict: API 返回的 JSON 数据
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": question, "top_k": top_k},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ 无法连接到 API 服务，请确保已运行 `python api.py`")
        return {"error": "连接失败"}
    except requests.exceptions.Timeout:
        st.error("⏰ API 请求超时，请稍后重试")
        return {"error": "超时"}
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API 请求失败: {e}")
        return {"error": str(e)}


def fetch_stats(max_retries: int = 10, delay: int = 2) -> dict:
    """
    获取知识库统计信息，带自动重试机制。

    Args:
        max_retries (int): 最大重试次数
        delay (int): 每次重试间隔（秒）

    Returns:
        dict: 统计信息
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                # 如果 total_chunks > 0 或者有内容，说明 API 已就绪
                if data.get("total_chunks", 0) > 0:
                    return data
            # 如果响应成功但数据为空，也继续重试
        except Exception:
            # API 还没准备好，继续重试
            pass

        # 不是最后一次重试，等待后继续
        if attempt < max_retries - 1:
            time.sleep(delay)

    # 重试失败返回默认值
    return {"total_chunks": 0, "dimension": 0, "model_name": "未加载"}


# 页面标题
st.title("🤖 Local RAG 助手")
st.markdown("基于 FAISS + Sentence-Transformers 的本地知识库问答系统")
st.divider()

# 侧边栏 - 系统状态
with st.sidebar:
    st.header("📊 系统状态")

    # 加载统计信息（带自动重试）
    with st.spinner("正在连接后端服务..."):
        stats = fetch_stats()
    total_chunks = stats.get("total_chunks", 0)
    dimension = stats.get("dimension", 0)
    model_name = stats.get("model_name", "未加载")

    st.metric("📚 知识库文档块", total_chunks)
    st.metric("📐 向量维度", dimension)
    st.metric("🧠 嵌入模型", model_name.split("/")[-1] if "/" in model_name else model_name)

    st.divider()

    # 参数设置
    st.subheader("⚙️ 检索参数")
    top_k = st.slider("返回文档块数量 (top_k)", min_value=1, max_value=10, value=5)
    st.caption(f"检索时会返回最相似的 {top_k} 个文档块")

    st.divider()

    # 上传功能（可选）
    st.subheader("📤 上传文档")
    uploaded_file = st.file_uploader("选择 PDF 文件", type=["pdf"])
    if uploaded_file is not None:
        # 保存上传的文件
        temp_path = Path("knowledge") / uploaded_file.name
        temp_path.parent.mkdir(parents=True, exist_ok=True)

        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ 文件已保存: {uploaded_file.name}")

        # 调用上传 API
        if st.button("添加到知识库"):
            with st.spinner("正在处理文档..."):
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/upload",
                        json={"file_path": str(temp_path), "chunk_size": 500, "overlap": 50},
                        timeout=60
                    )
                    response.raise_for_status()
                    data = response.json()
                    if data.get("success"):
                        st.success(f"✅ {data['message']}")
                        st.rerun()
                    else:
                        st.error(f"❌ 添加失败: {data.get('message', '未知错误')}")
                except Exception as e:
                    st.error(f"❌ 上传失败: {e}")

    st.divider()
    st.caption("💡 提示：请先运行 `python api.py` 启动后端服务")

# 主界面 - 输入区
col1, col2 = st.columns([4, 1])

with col1:
    question = st.text_input(
        "请输入您的问题：",
        placeholder="例如：Docker 的核心概念有哪些？",
        key="question_input"
    )

with col2:
    st.write("")
    st.write("")
    ask_button = st.button("🚀 提问", type="primary", use_container_width=True)

# 处理提问
if ask_button and question.strip():
    with st.spinner("🔍 正在检索知识库并生成回答..."):
        result = call_rag_api(question, top_k=top_k)

    if result.get("error"):
        st.error(f"❌ 查询出错: {result['error']}")
    else:
        # 显示回答
        st.subheader("💬 回答")
        answer = result.get("answer", "暂无回答")
        st.markdown(answer)

        # 显示信息来源
        with st.expander("📖 查看检索到的上下文"):
            context = result.get("context", "")
            if context:
                st.markdown(context)
            else:
                st.info("未检索到相关上下文")

        with st.expander("🔍 查看生成的提示（Prompt）"):
            prompt = result.get("prompt", "")
            if prompt:
                st.code(prompt, language="text")
            else:
                st.info("未生成提示")

        # 显示统计信息
        results_count = result.get("results_count", 0)
        st.caption(f"📊 检索到 {results_count} 个相关文档块")

elif ask_button and not question.strip():
    st.warning("⚠️ 请输入问题")

# 如果用户按回车键（通过 on_change 触发）
if question and not ask_button:
    # 按回车不会触发按钮，所以我们用 session_state 来检测
    pass

# 底部
st.divider()
st.caption("🔒 所有数据均在本地处理，不会上传到互联网")
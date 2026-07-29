"""
FastAPI 服务
提供 RAG 系统的 HTTP API 接口，支持本地 LLM（通过 ctransformers 加载 GGUF）。
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from rag.parser import load_pdf
from rag.chunk import chunk_text
from rag.rag import RAG
from rag.llm import LocalLLM  # 新增：导入 LLM 封装

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 初始化 FastAPI
app = FastAPI(
    title="Local RAG API",
    description="基于 FAISS、Sentence-Transformers 和本地 LLM 的 RAG 系统",
    version="1.1.0"
)

# 全局 RAG 实例
rag_instance: Optional[RAG] = None


# ---------- Pydantic 模型 ----------
class QueryRequest(BaseModel):
    question: str = Field(..., description="用户问题", min_length=1, max_length=500)
    top_k: Optional[int] = Field(5, description="返回的文档块数量", ge=1, le=20)


class QueryResponse(BaseModel):
    question: str
    context: str
    prompt: str
    answer: str
    results_count: int
    error: Optional[str] = None


class UploadRequest(BaseModel):
    file_path: str = Field(..., description="PDF 文件路径")
    chunk_size: int = Field(500, description="切块大小", ge=100, le=2000)
    overlap: int = Field(50, description="重叠大小", ge=0, le=500)


class UploadResponse(BaseModel):
    success: bool
    message: str
    chunks_added: int = 0


class StatsResponse(BaseModel):
    total_chunks: int
    dimension: int
    model_name: str


# ---------- 启动事件 ----------
@app.on_event("startup")
async def startup_event():
    """
    应用启动时初始化 RAG 系统。
    自动加载向量索引，并尝试加载本地 LLM。
    """
    global rag_instance

    logger.info("正在启动 RAG 系统...")

    # 1. 加载或创建向量存储
    index_path = Path("vector_db")
    if index_path.exists() and (index_path / "faiss.index").exists():
        logger.info("发现已保存的索引，正在加载...")
        from rag.vector_store import VectorStore
        vector_store = VectorStore(model_name="all-MiniLM-L6-v2")
        vector_store.load_index("vector_db")
        logger.info(f"加载成功，知识库包含 {vector_store.index.ntotal} 个文档块")
    else:
        logger.info("未找到已保存的索引，创建空向量存储")
        from rag.vector_store import VectorStore
        vector_store = VectorStore(model_name="all-MiniLM-L6-v2")

    # 2. 初始化 LLM（如果模型文件存在）
    llm = LocalLLM(
        model_path="models/qwen2-1_5b-instruct-q8_0.gguf",
        n_ctx=2048,
        n_threads=4,
        temperature=0.7,
        top_p=0.9,
        max_tokens=512
    )
    rag_instance = RAG(
        vector_store=vector_store,
        top_k=5,
        score_threshold=0.3,
        llm=llm  # 传入
    )

    # 3. 创建 RAG 实例（传入 LLM）
    rag_instance = RAG(
        vector_store=vector_store,
        top_k=5,
        score_threshold=0.3,
        llm=llm  # 关键：将 LLM 实例传入 RAG
    )

    logger.info("RAG 系统启动完成")


# ---------- 路由 ----------
@app.get("/", tags=["根路径"])
async def root():
    return {
        "message": "Local RAG API 服务已启动",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": ["/query", "/upload", "/stats", "/health"]
    }


@app.get("/health", tags=["健康检查"])
async def health():
    return {"status": "healthy", "rag_initialized": rag_instance is not None}


@app.get("/stats", response_model=StatsResponse, tags=["统计信息"])
async def get_stats():
    if rag_instance is None:
        raise HTTPException(status_code=503, detail="RAG 系统未初始化")
    total = rag_instance.vector_store.index.ntotal
    dimension = rag_instance.vector_store.dimension
    model_name = rag_instance.vector_store.model._modules["0"].auto_model.config.name_or_path
    return StatsResponse(
        total_chunks=total,
        dimension=dimension,
        model_name=model_name
    )


@app.post("/query", response_model=QueryResponse, tags=["RAG 查询"])
async def query(request: QueryRequest):
    if rag_instance is None:
        raise HTTPException(status_code=503, detail="RAG 系统未初始化")
    try:
        result = rag_instance.query(question=request.question, top_k=request.top_k)
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        return QueryResponse(
            question=result["question"],
            context=result["context"],
            prompt=result["prompt"],
            answer=result["answer"],
            results_count=len(result["results"]),
            error=None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


@app.post("/upload", response_model=UploadResponse, tags=["文档管理"])
async def upload_pdf(request: UploadRequest):
    if rag_instance is None:
        raise HTTPException(status_code=503, detail="RAG 系统未初始化")
    try:
        logger.info(f"正在解析 PDF: {request.file_path}")
        text = load_pdf(request.file_path)
        if not text:
            raise HTTPException(status_code=400, detail="PDF 解析失败或内容为空")
        chunks = chunk_text(text, chunk_size=request.chunk_size, overlap=request.overlap)
        if not chunks:
            raise HTTPException(status_code=400, detail="切块后无有效文本块")
        added = rag_instance.add_documents(chunks)
        return UploadResponse(
            success=True,
            message=f"成功添加 {added} 个文档块",
            chunks_added=added
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
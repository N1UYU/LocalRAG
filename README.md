<<<<<<< HEAD
# 🤖 Local RAG 知识库问答系统
=======
🤖 Local RAG 知识库问答系统
>>>>>>> 97467270242068dbada14984a69cd2e91f65215a

基于 **FAISS + Sentence-Transformers + Qwen2** 构建的**完全本地化** RAG（检索增强生成）知识库问答系统。

所有数据均在本地处理，无需联网，保障数据隐私安全。

---

## 📸 效果截图

![界面截图](screenshot2.png)

## 🚀 功能特点

- 📄 **PDF 文档解析**：自动提取 PDF 文本内容
- ✂️ **智能文本切块**：支持重叠切块，避免语义断裂
- 🔍 **向量检索**：基于 FAISS 实现毫秒级相似度搜索
- 🧠 **本地 LLM 推理**：集成 Qwen2 模型，数据不出本地
- 🌐 **Web 交互界面**：Streamlit 构建的友好聊天界面
- 📡 **RESTful API**：FastAPI 提供标准接口，自动生成 Swagger 文档
- 💾 **索引持久化**：向量索引保存到本地，重启无需重建
- 📤 **动态扩展**：支持通过界面上传新文档到知识库
- 🚀 **一键启动**：双击 `start.vbs` 即可启动所有服务

---

## 🛠️ 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| 前端界面 | Streamlit |
| 向量检索 | FAISS |
| 文本向量化 | Sentence-Transformers (all-MiniLM-L6-v2) |
| 大语言模型 | llama-cpp-python + Qwen2-1.5B |
| 文档解析 | PyPDF |
| 部署方式 | 纯本地部署，数据不外传 |

---

## 📁 目录结构

```
LocalRAG/
│
├── app.py                 # Streamlit Web 界面
├── api.py                 # FastAPI 后端服务
├── config.yaml            # 配置文件
├── start.vbs              # 🚀 一键启动脚本（Windows）
├── stop.vbs               # 🛑 停止服务脚本
│
├── rag/                   # RAG 核心模块
│   ├── parser.py          # PDF 解析
│   ├── chunk.py           # 文本切块
│   ├── vector_store.py    # FAISS 向量存储
│   ├── retriever.py       # 检索器
│   ├── prompt.py          # 提示模板
│   ├── llm.py             # LLM 封装（llama-cpp-python）
│   └── rag.py             # RAG 主流程
│
├── knowledge/             # 📚 知识库文档（存放 PDF）
├── models/                # 🧠 大模型文件（存放 GGUF）
├── vector_db/             # 💾 FAISS 索引持久化
├── logs/                  # 📋 日志文件
│
├── requirements.txt       # Python 依赖清单
└── README.md              # 项目文档
```

---

## 📦 安装与运行

### 1. 克隆项目

```bash
git clone https://github.com/N1UYU/LocalRAG.git
cd LocalRAG
```

### 2. 创建虚拟环境

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 下载模型文件

将 Qwen2 GGUF 模型文件放入 `models/` 目录：

```
models/qwen2-1_5b-instruct-q8_0.gguf
```

> 可以从 Hugging Face 或国内镜像站下载 Qwen2 系列模型

### 5. 启动系统

**方式一：一键启动（推荐）**

右键打开！ `start.vbs` 即可自动启动所有服务，浏览器会自动打开 `http://localhost:8501`
（浏览器可能会打开两个8051网页，关闭一个即可，如果系统状态未加载出来刷新下网页就行了）

**方式二：手动启动**

```bash
# 终端1：启动 API 服务
python api.py

# 终端2：启动 Streamlit 界面
streamlit run app.py --server.port=8501
```

### 6. 访问系统

- **用户界面**：http://localhost:8501
- **API 文档**：http://localhost:8000/docs

---

## 📝 使用示例

在输入框中提问，例如：

- `Docker 的核心概念有哪些？`
- `Kubernetes 中 Pod 是什么？`
- `Python 如何实现面向对象编程？`
- `Linux 中如何管理文件权限？`

系统会从知识库中检索相关内容，并由 LLM 生成回答。

---

## 🧪 测试问题集

| 类别 | 示例问题 |
|------|---------|
| Docker | `Docker 的核心概念有哪些？` |
| Kubernetes | `Kubernetes 的 Deployment 和 Service 有什么区别？` |
| Linux | `Linux 中如何查看进程？` |
| Python | `Python 的虚拟环境有什么用？` |
| 跨文档 | `Docker 和 Kubernetes 是什么关系？` |

---

## 🎯 项目亮点

- ✅ **完全本地化**：所有数据在本地处理，无需联网，保障数据隐私
- ✅ **毫秒级检索**：FAISS 向量检索，响应迅速
- ✅ **模块化设计**：分层架构，符合企业级开发规范
- ✅ **可扩展性强**：支持动态添加文档，可切换不同 Embedding 模型和 LLM
- ✅ **开箱即用**：一键启动脚本，降低使用门槛

---

## 📄 License

MIT License

---

## 📧 联系方式

如有问题，欢迎提 Issue 或联系作者。

---

**✨ 如果这个项目对你有帮助，欢迎 Star！**
```

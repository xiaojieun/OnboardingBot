"""构建向量库脚本，支持多种文档格式"""

from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


# 配置参数
RAW_DATA_DIR = Path(__file__).parent / "data" / "raw"
VECTOR_STORE_DIR = Path(__file__).parent / "VectorStore"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "text-embedding-v4"


def get_loader(file_path: Path):
    """根据文件后缀选择合适的加载器"""
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return PyPDFLoader(str(file_path))
    elif suffix in (".txt", ".md"):
        return TextLoader(str(file_path), encoding="utf-8")
    elif suffix == ".docx":
        return Docx2txtLoader(str(file_path))
    else:
        raise ValueError(f"不支持的文件格式: {suffix}")


def load_documents(data_dir: Path) -> list[Document]:
    """从数据目录加载所有支持的文档"""
    documents: list[Document] = []
    supported_suffixes = {".pdf", ".txt", ".md", ".docx"}

    for file_path in data_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_suffixes:
            print(f"正在加载: {file_path.name}")
            loader = get_loader(file_path)
            docs = loader.load()
            documents.extend(docs)

    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    """将文档切片，并在metadata中写入source和page"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", " ", ""],
    )

    split_docs: list[Document] = []
    for doc in documents:
        chunks = text_splitter.split_documents([doc])
        for chunk in chunks:
            # 从source路径提取文件名
            source_path = chunk.metadata.get("source", "")
            filename = Path(source_path).name if source_path else "unknown"

            # 提取页码（PDF有页码，其他格式默认为0）
            page = chunk.metadata.get("page", 0)

            # 更新metadata
            chunk.metadata["source"] = filename
            chunk.metadata["page"] = page
            split_docs.append(chunk)

    return split_docs


def build_vector_store(documents: list[Document]) -> None:
    """构建并保存Chroma向量库"""
    # 初始化DashScope embeddings
    embeddings = DashScopeEmbeddings(model=EMBEDDING_MODEL)

    # 创建向量库目录
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

    # 构建Chroma向量库
    vector_store = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=str(VECTOR_STORE_DIR),
    )

    print(f"向量库构建成功: {VECTOR_STORE_DIR}")
    print(f"共索引 {len(documents)} 个文本块")


def main() -> None:
    """主函数：构建向量库"""
    print("=" * 50)
    print("构建向量库")
    print("=" * 50)

    # 第一步：加载文档
    print("\n[步骤1] 加载文档...")
    documents = load_documents(RAW_DATA_DIR)
    if not documents:
        print("未在 data/raw/ 目录找到文档")
        return
    print(f"已加载 {len(documents)} 个文档")

    # 第二步：切片文档
    print("\n[步骤2] 切片文档...")
    split_docs = split_documents(documents)
    print(f"生成 {len(split_docs)} 个文本块")

    # 第三步：构建向量库
    print("\n[步骤3] 构建向量库...")
    build_vector_store(split_docs)

    print("\n" + "=" * 50)
    print("完成!")


if __name__ == "__main__":
    main()

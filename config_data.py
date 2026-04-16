import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# config_data.py 中改回字符串
md5_path = str(BASE_DIR / "md5.text")
persist_directory = str(BASE_DIR / "chroma_db")
chat_history_dir = str(BASE_DIR / "chat_history")
SAMPLE_DATA_DIR = BASE_DIR / "data" / "sample"   # 这个可以保留 Path，便于遍历


# Chunk 相关配置
chunk_size = 1000
chunk_overlap = 100
separators = ["\n\n", "\n", " ", "，", "。", "？", "！", "、", "!", "?", ".", ","]
max_split_char_number = 100

# 检索配置
similarity_threshold = 2

# 模型配置（使用阿里云百炼）
embeddings_model_name = "text-embedding-v4"
chat_model_name = "qwen3-max"

# Session 配置（可改为从环境变量读取，避免硬编码 user_001）
session_config = {
    "configurable": {
        "session_id": "default_user"   # 改成通用名称，不要用 user_001
    }
}
"""
知识库
"""
from datetime import datetime   #这里不要import datetime
import os
import hashlib
from dotenv import load_dotenv
load_dotenv()
from cryptography.hazmat.primitives.hashes import MD5
from langchain_chroma import Chroma
from sqlalchemy.testing.suite.test_reflection import metadata

import config_data as config
from langchain_community.embeddings import DashScopeEmbeddings  #阿里云的模型
from langchain_text_splitters import RecursiveCharacterTextSplitter #递归文本分割器
# knowledge_base.py
import shutil
from pathlib import Path
# ... 保留原有导入，额外添加：



def check_md5(md5_str:str):
    """检查传入的md5字符串是否已经被处理过了
        return False(md5未处理过),  True(已经处理过,已有记录)
    """

    if not os.path.exists(config.md5_path):
        #if进入表示文件不存在,那肯定没有处理过这个md5了
        open(config.md5_path,'w',encoding="utf-8").close ()     #打开再关闭一下就创建成功了
        return False
    else:
        for line in open(config.md5_path,'r',encoding="utf-8").readlines():
            line = line.strip()     #处理字符串前后空格和回车
            if line==md5_str:
                return True     #已经处理,跳出整个循环,下面一行代码将不会被执行
        return False

def save_md5(md5_str:str):
    """将传入的md5字符串,传入到文件内保存"""
    with  open(config.md5_path,'a',encoding="utf-8") as f:
        f.write(md5_str+'\n')       #\n换行符

def get_string_md5(input_str:str,encoding="utf-8"):
    """将传入的字符串转化为md5字符串"""

    #将字符串转化为bytes字节数组
    str_bytes=input_str.encode(encoding=encoding)   #encoding=传进来的utf-8

    #创建md5对象
    md5_obj=hashlib.md5()   #得到md5对象
    md5_obj.update(str_bytes)       #更新内容(传入即将要转换的字节数组)
    md5_hex=md5_obj.hexdigest()     #得到md5的十六进制字符串(用hexdigest)

    return md5_hex                  #返回md5的十六进制字符串



class KnowledgeBaseService(object):
    def __init__(self, auto_load_sample=True):
        # 确保持久化目录存在
        os.makedirs(config.persist_directory, exist_ok=True)

        self.chroma = Chroma(
            collection_name=config.collection_name,
            embedding_function=DashScopeEmbeddings(model=config.embeddings_model_name),
            persist_directory=str(config.persist_directory)  # 转为字符串
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            length_function=len,
        )

        # 自动加载示例数据（如果向量库为空且 auto_load_sample 为 True）
        if auto_load_sample and self._is_vectorstore_empty():
            self._load_sample_data()

    def _is_vectorstore_empty(self):
        """检查向量库是否为空（通过尝试获取一个 collection 的计数）"""
        try:
            # Chroma 的 get() 方法返回所有文档，但可能很慢，这里简单通过检索空字符串判断
            results = self.chroma.similarity_search("任意测试文本", k=1)
            return len(results) == 0
        except Exception:
            return True

    def _load_sample_data(self):
        """加载 data/sample 目录下的所有文本文件到知识库"""
        if not config.SAMPLE_DATA_DIR.exists():
            print("示例数据目录不存在，跳过自动加载")
            return
        for file_path in config.SAMPLE_DATA_DIR.glob("*"):
            if file_path.suffix in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                # 使用上传逻辑，但不检查 MD5（因为初始为空）
                self._add_text(content, file_path.name, skip_md5_check=True)
        print("示例数据加载完成")

    def _add_text(self, data: str, filename: str, skip_md5_check=False):
        """内部添加文本方法，可选跳过 MD5 检查"""
        md5_hex = get_string_md5(data)
        if not skip_md5_check and check_md5(md5_hex):
            return "[跳过]内容已经在知识库中"

        if len(data) > config.max_split_char_number:
            knowledge_chunks = self.spliter.split_text(data)
        else:
            knowledge_chunks = [data]

        metadata = {
            "source": filename,
            "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "system" if skip_md5_check else "user"
        }
        self.chroma.add_texts(knowledge_chunks, metadatas=[metadata for _ in knowledge_chunks])

        if not skip_md5_check:
            save_md5(md5_hex)
        return "[成功]内容已保存"

    def upload_by_str(self, data: str, filename):
        """供外部调用的上传方法，会进行 MD5 去重"""
        return self._add_text(data, filename, skip_md5_check=False)

    def reset_knowledge_base(self):
        """重置知识库：删除向量库目录和 MD5 文件，重新加载示例数据"""
        # 关闭当前 chroma 连接（避免文件占用）
        self.chroma = None
        # 删除向量库目录
        if config.persist_directory.exists():
            shutil.rmtree(config.persist_directory)
        # 删除 MD5 记录文件
        if config.md5_path.exists():
            config.md5_path.unlink()
        # 重新初始化
        os.makedirs(config.persist_directory, exist_ok=True)
        self.chroma = Chroma(
            collection_name=config.collection_name,
            embedding_function=DashScopeEmbeddings(model=config.embeddings_model_name),
            persist_directory=str(config.persist_directory)
        )
        # 重新加载示例数据
        self._load_sample_data()
        return "知识库已重置为示例数据"














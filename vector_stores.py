from langchain_chroma import Chroma
import config_data as config


#向量存储服务
class VectorStoreService(object):
    def __init__ (self,embedding):
        """
        embedding:嵌入模型的传入
        """
        self.embedding=embedding
        self.vector_store=Chroma(
            collection_name=config.collection_name,  #数据库的表名
            embedding_function=self.embedding,      #嵌入的模型
            persist_directory=config.persist_directory  #chroma数据库的本地存储路径
        )
    def get_retriever(self):
        """返回向量检索器,方便加入链chain"""
        #as_retriever()方法,返回检索的结果
        #config.similarity_threshold是检索返回的向量数量
        return self.vector_store.as_retriever(search_kwargs={"k":config.similarity_threshold})

if __name__ =='__main__':
    from langchain_community.embeddings import DashScopeEmbeddings      #嵌入模型
    retriever=VectorStoreService(DashScopeEmbeddings(model="text-embedding-v4")).get_retriever() #得到检索对象

    print(retriever.invoke("我的体重180斤,给出尺码推荐"))













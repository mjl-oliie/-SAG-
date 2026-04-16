from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory, RunnableLambda

from file_history_store import get_history
from vector_stores import VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.documents import Document
from dotenv import load_dotenv
load_dotenv()

def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt

#核心链,包括聊天模型,向量数据库,prompt模板,最终执行链
class RagService(object):
    def __init__(self):

        self.vector_service=VectorStoreService(
            embedding=DashScopeEmbeddings(model=config.embeddings_model_name)

        )


        self.prompt_template=ChatPromptTemplate.from_messages(
            [
                ("system","以我提供的已知资料为主,"
                "简洁和专业的回答用户问题,参考资料{context}."),
                ("system","并且提供我用户的历史对话记录,如下:"),
                MessagesPlaceholder("history"),
                ("user","请回答用户的提问:{input}")
            ]
        )

        self.chat_model=ChatTongyi(model=config.chat_model_name)

        self.chain=self.__get_chain()


    def __get_chain(self):
        "获取最终执行链"
        retriever=self.vector_service.get_retriever()
        def format_document(docs: list[Document]):
            if not docs:
                return " 无相关参考内容"

            formatted_str=""
            for doc in docs:
                formatted_str+=f"文档片段{doc.page_content}\n文档原数据:{doc.metadata}\n\n"
            return formatted_str

        def format_for_retriever(value:dict)->str:
            return value["input"]

        def format_for_prompt_template(value):
            #提取input,context,history
            new_value={}
            new_value["input"]=value["input"]["input"]
            new_value["context"]=value["context"]
            new_value["history"]=value["input"]["history"]
            return new_value
        chain=(
            {
                "input":RunnablePassthrough (),
                "context":RunnableLambda(format_for_retriever) | retriever | format_document
            } | RunnableLambda(format_for_prompt_template)|self.prompt_template |print_prompt | self.chat_model | StrOutputParser()

        )

        conversation_chain=RunnableWithMessageHistory(
            chain,      #被增强的链
            get_history,
            input_messages_key="input",
            history_messages_key="history"
        )
        return  conversation_chain


if __name__ =='__main__':

    res=RagService().chain.invoke({"input":"春天适合穿什么衣服"}, config.session_config)
    print(res)

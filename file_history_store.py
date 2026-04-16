import os
from typing import Sequence

import json
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict

import config_data as config   # 新增

def get_history(session_id):
    return FileChatMessageHistory(session_id, config.chat_history_dir)

class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id, storage_path):
        self.session_id = session_id
        self.storage_path = storage_path
        self.file_path = os.path.join(self.storage_path, self.session_id)
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
    # 其他方法保持不变

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        # Sequence序列 类似一个列表,tuple
        all_messages = list(self.messages)        #已有的消息列表
        all_messages.extend(messages)           #新的和已有的融合成一个list

        #将数据同步写入到本地文件中
        #类对象写入文件 -> 一堆二进制
        #为了方便,将BaseMessage消息转为字典(借助json模块以json字符串写入文件)

        # message_to_dict:单个消息对象(BaseMessages类实例)-->字典

        new_messages = [message_to_dict(message) for message in all_messages]

       #也可以这样
        #for message in all_messages:
        #    d=message_to_dict(message)
        #    new_messages.append(d)

        #将数据写入文件
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(new_messages, f)

    @property
    def messages(self) -> list[BaseMessage]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                #打开文件,"r"表示读,"w"表示写,"a"表示追加,"x"表示创建,encoding="utf-8"表示使用utf-8编码,self.file_path是文件路径
                messages_data = json.load(f)
                return messages_from_dict(messages_data)

        except FileNotFoundError:
            return []

    def clear(self) -> None:
        with open(self.file_path, "w", encoding="utf-8") as f:
             json.dump([], f)








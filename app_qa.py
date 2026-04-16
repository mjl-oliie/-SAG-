import streamlit as st
import time
from rag import RagService
import config_data as config
from knowledge_base import KnowledgeBaseService

st.title("智能客服")
st.divider()

# 初始化 session_state
if "message" not in st.session_state:
    st.session_state["message"] = [{"role": "assistant", "content": "欢迎来到智能客服系统"}]

if "rag" not in st.session_state:
    # 注意：RagService 内部会创建 VectorStoreService，而 VectorStoreService 使用 Chroma
    # 我们需要确保知识库服务先初始化（用于上传和重置），但 RagService 也需要使用同一个向量库。
    # 为简化，让 RagService 和 KnowledgeBaseService 共享同一个 Chroma 实例。
    # 这里先创建 KnowledgeBaseService，并存入 session_state，供侧边栏使用。
    st.session_state["kb_service"] = KnowledgeBaseService(auto_load_sample=True)
    st.session_state["rag"] = RagService()  # RagService 内部会自己连接 Chroma，路径一致即可

# 侧边栏：知识库管理
with st.sidebar:
    st.header("📚 知识库管理")

    # 文件上传组件
    uploaded_file = st.file_uploader("上传 TXT 文件", type=["txt"])
    if uploaded_file is not None:
        content = uploaded_file.getvalue().decode("utf-8")
        if st.button("添加到知识库"):
            with st.spinner("正在处理..."):
                result = st.session_state["kb_service"].upload_by_str(content, uploaded_file.name)
                st.success(result)
                # 注意：上传后需要让 RagService 重新加载 retriever？因为 Chroma 是持久化的，retriever 会自动看到新数据
                # 但为了确保 prompt 中的 context 包含新文档，可以提示用户刷新或自动刷新。这里简单提示。
                st.info("知识库已更新，您可以继续提问。")

    # 重置按钮
    if st.button("🗑️ 重置为示例数据"):
        st.session_state["kb_service"].reset_knowledge_base()
        # 重置后需要重新创建 RagService，让它重新连接向量库
        st.session_state["rag"] = RagService()
        st.success("知识库已重置为示例数据！")
        # 可选：清空聊天记录
        st.session_state["message"] = [
            {"role": "assistant", "content": "知识库已重置，示例数据已加载。请问有什么可以帮助您？"}]
        st.rerun()

# 显示历史消息
for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 用户输入
prompt = st.chat_input()
if prompt:
    st.session_state["message"].append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    ai_res_list = []
    with st.spinner("思考中......"):
        time.sleep(1)  # 可保留，模拟思考
        # 注意：RagService 的 chain 需要传入 config.session_config
        res_stream = st.session_state["rag"].chain.stream(
            {"input": prompt},
            config.session_config
        )


        def capture(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)
                yield chunk


        st.chat_message("assistant").write_stream(capture(res_stream, ai_res_list))
        full_response = "".join(ai_res_list)
        st.session_state["message"].append({"role": "assistant", "content": full_response})
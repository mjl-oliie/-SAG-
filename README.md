## 环境变量配置

本项目使用阿里云百炼 API，需要配置 API Key。

1. 在 [阿里云百炼控制台](https://bailian.console.aliyun.com/) 获取 API Key。
2. 在项目根目录创建 `.env` 文件，内容如下：
DASHSCOPE_API_KEY=你的API_Key
3. 安装依赖：`pip install -r requirements.txt`
4. 运行：`streamlit run app_qa.py`

"""智谱AI配置"""
import os
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "c5033eaca6e049a9899f9f257ceb9116.7DL6kEMKh3zUJf85")
ZHIPU_MODEL = "glm-4-flash"

# 被测系统地址
BASE_URL = "http://127.0.0.1:8000"
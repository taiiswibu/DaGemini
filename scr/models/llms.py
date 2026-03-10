import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from scr.utils.utils import BaseLogger

load_dotenv()

def load_embedding_model(embedding_model_name: str = "google-genai", logger: BaseLogger = BaseLogger()):
    if embedding_model_name == "google-genai":
        embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        dimension = 768
        logger.info(f"Embedding: Using Google Generative AI with {dimension} dimensions.")
        return embedding
    else:
        raise ValueError("Unknown embedding model API. Please choose 'google-genai'.")

def load_llm(llm_name: str = "gemini-2.5-flash", logger: BaseLogger = BaseLogger()):
    """
    Load the specified Gemini 2.5 language model.
    """
    if "flash" in llm_name.lower():
        # Bản Flash 2.5: Nhanh, mượt, phù hợp làm Agent phân tích data
        model_id = "gemini-2.5-flash" 
    elif "pro" in llm_name.lower():
        # Bản Pro 2.5: Siêu thông minh, suy luận logic phức tạp cực tốt
        model_id = "gemini-2.5-pro"
    else:
        model_id = "gemini-2.5-flash"

    logger.info(f"INFO: Using Model: {model_id}")
    
    return ChatGoogleGenerativeAI(
        model=model_id, 
        temperature=0.0, # Giữ 0.0 để code sinh ra chính xác nhất
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
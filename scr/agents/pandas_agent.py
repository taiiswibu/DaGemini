import pandas as pd
from typing import Any
from langchain_experimental.agents import create_pandas_dataframe_agent

from scr.utils.utils import BaseLogger

logger = BaseLogger()

class DataAnalysisAgent:
    def __init__(
        self,
        llm: Any,
        df: pd.DataFrame,
        verbose: bool = True,
        **kwargs
    ):
        self.llm = llm
        self.df = df
        self.verbose = verbose

    def create_agent(self) -> Any:
        logger.info("INFO: Khởi tạo Pandas DataFrame Agent (Tool Calling Mode)...")
        
        return create_pandas_dataframe_agent(
            llm=self.llm,
            df=self.df,
            verbose=self.verbose,
            # TUYỆT CHIÊU Ở ĐÂY: Dùng tool-calling thay vì zero-shot-react-description
            agent_type="tool-calling", 
            return_intermediate_steps=True,
            handle_parsing_errors=True, # Vẫn giữ lại để phòng hờ LLM lỡ trớn
            allow_dangerous_code=True,
            max_iterations=10
        )
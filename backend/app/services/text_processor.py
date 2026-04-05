"""
文本处理服务
"""

from typing import List
from ..utils.file_parser import FileParser, split_text_into_chunks


class TextProcessor:
    """文本处理器"""
    
    @staticmethod
    def extract_from_files(file_paths: List[str]) -> str:
        """从多个文件提取文本"""
        return FileParser.extract_from_multiple(file_paths)
    
    @staticmethod
    def split_text(
        text: str,
        chunk_size: int = 500,
        overlap: int = 50
    ) -> List[str]:
        """
        分割文本
        
        Args:
            text: 原始文本
            chunk_size: 块大小
            overlap: 重叠大小
            
        Returns:
            文本块列表
        """
        return split_text_into_chunks(text, chunk_size, overlap)
    
    @staticmethod
    def preprocess_text(text: str) -> str:
        """
        预处理文本
        - 移除多余空白
        - 标准化换行
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        import re
        
        # 标准化换行
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # 移除连续空行（保留最多两个换行）
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 移除行首行尾空白
        lines = [line.strip() for line in text.split('\n')]
        text = '\n'.join(lines)
        
        return text.strip()
    
    @staticmethod
    def is_wenmo_format(text: str) -> bool:
        """判断是否为文墨天机导出的格式"""
        markers = ["文墨天机", "命盘ID", "公历", "农历", "五行局"]
        count = sum(1 for m in markers if m in text)
        return count >= 3

    @staticmethod
    def parse_wenmo_chart(text: str) -> dict:
        """
        解析文墨天机导出的命盘文本
        提取基本出生信息，用于快捷起卦
        """
        import re
        result = {}
        
        # 1. 提取姓名
        name_match = re.search(r"姓名：([^\n\s]+)", text)
        if name_match: result["name"] = name_match.group(1)
        
        # 2. 提取公历日期
        date_match = re.search(r"公历：(\d{4})年(\d{1,2})月(\d{1,2})日\s+(\d{1,2})[:：](\d{1,2})", text)
        if date_match:
            result["year"] = int(date_match.group(1))
            result["month"] = int(date_match.group(2))
            result["day"] = int(date_match.group(3))
            result["hour"] = int(date_match.group(4))
            result["minute"] = int(date_match.group(5))
            
        # 3. 提取性别
        if "性别：男" in text or "乾造" in text:
            result["gender"] = "male"
        elif "性别：女" in text or "坤造" in text:
            result["gender"] = "female"
            
        return result


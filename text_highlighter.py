"""文本高亮器类"""
import re
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor


class TextHighlighter(QSyntaxHighlighter):
    """文本高亮器，用于标记特殊符号"""
    
    def __init__(self, document):
        super().__init__(document)
        
        # 角色标记格式（蓝色）
        role_format = QTextCharFormat()
        role_format.setForeground(QColor(0, 0, 255))  # 蓝色
        role_format.setFontWeight(75)
        self.role_pattern = re.compile(r'\[[ABCD]\]')
        self.role_format = role_format
        
        # 停顿标记格式（红色）
        pause_format = QTextCharFormat()
        pause_format.setForeground(QColor(255, 0, 0))  # 红色
        pause_format.setFontWeight(75)
        self.pause_pattern = re.compile(r'\[\d+\]')
        self.pause_format = pause_format
        
        # 蜂鸣标记格式（绿色）
        beep_format = QTextCharFormat()
        beep_format.setForeground(QColor(0, 128, 0))  # 绿色
        beep_format.setFontWeight(75)
        self.beep_pattern = re.compile(r'\[R\]')
        self.beep_format = beep_format
    
    def highlightBlock(self, text):
        """高亮文本块"""
        for match in self.role_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.role_format)
        
        for match in self.pause_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.pause_format)
        
        for match in self.beep_pattern.finditer(text):
            self.setFormat(match.start(), match.end() - match.start(), self.beep_format)
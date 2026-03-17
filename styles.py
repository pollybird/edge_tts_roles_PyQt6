"""样式定义文件 - 基于 Tailwind CSS 设计理念"""

class Styles:
    """样式类，包含所有界面元素的样式定义"""
    
    # 颜色主题（基于 Tailwind CSS）
    PRIMARY_COLOR = "#3b82f6"  # 主色
    PRIMARY_HOVER = "#2563eb"  # 主色悬停
    SECONDARY_COLOR = "#64748b"  # 次要色
    SUCCESS_COLOR = "#10b981"  # 成功色
    WARNING_COLOR = "#f59e0b"  # 警告色
    DANGER_COLOR = "#ef4444"  # 危险色
    BACKGROUND_COLOR = "#f8fafc"  # 背景色
    CARD_COLOR = "#ffffff"  # 卡片背景
    BORDER_COLOR = "#e2e8f0"  # 边框色
    TEXT_COLOR = "#1e293b"  # 文本色
    TEXT_SECONDARY = "#64748b"  # 次要文本色
    
    # 主窗口样式
    MAIN_WINDOW = ""
    MAIN_WINDOW += "QMainWindow {"
    MAIN_WINDOW += "    background-color: " + BACKGROUND_COLOR + ";"
    MAIN_WINDOW += "}"
    
    # 标签样式
    LABEL = ""
    LABEL += "QLabel {"
    LABEL += "    color: " + TEXT_COLOR + ";"
    LABEL += "    font-size: 13px;"
    LABEL += "}"
    
    # 标题标签样式
    HEADER_LABEL = ""
    HEADER_LABEL += "QLabel {"
    HEADER_LABEL += "    color: " + TEXT_COLOR + ";"
    HEADER_LABEL += "    font-size: 14px;"
    HEADER_LABEL += "    font-weight: bold;"
    HEADER_LABEL += "}"
    
    # 提示标签样式
    NOTE_LABEL = ""
    NOTE_LABEL += "QLabel {"
    NOTE_LABEL += "    color: " + TEXT_SECONDARY + ";"
    NOTE_LABEL += "    font-size: 11px;"
    NOTE_LABEL += "}"
    
    # 文本编辑框样式
    TEXT_EDIT = ""
    TEXT_EDIT += "QTextEdit {"
    TEXT_EDIT += "    background-color: " + CARD_COLOR + ";"
    TEXT_EDIT += "    color: " + TEXT_COLOR + ";"
    TEXT_EDIT += "    border: 1px solid " + BORDER_COLOR + ";"
    TEXT_EDIT += "    border-radius: 6px;"
    TEXT_EDIT += "    padding: 8px;"
    TEXT_EDIT += "    font-size: 13px;"
    TEXT_EDIT += "}"
    TEXT_EDIT += "QTextEdit:focus {"
    TEXT_EDIT += "    border: 2px solid " + PRIMARY_COLOR + ";"
    TEXT_EDIT += "    outline: none;"
    TEXT_EDIT += "}"
    
    # 主按钮样式
    PRIMARY_BUTTON = ""
    PRIMARY_BUTTON += "QPushButton {"
    PRIMARY_BUTTON += "    background-color: " + PRIMARY_COLOR + ";"
    PRIMARY_BUTTON += "    color: white;"
    PRIMARY_BUTTON += "    border: none;"
    PRIMARY_BUTTON += "    border-radius: 6px;"
    PRIMARY_BUTTON += "    padding: 8px 16px;"
    PRIMARY_BUTTON += "    font-size: 13px;"
    PRIMARY_BUTTON += "    font-weight: 500;"
    PRIMARY_BUTTON += "}"
    PRIMARY_BUTTON += "QPushButton:hover {"
    PRIMARY_BUTTON += "    background-color: " + PRIMARY_HOVER + ";"
    PRIMARY_BUTTON += "}"
    PRIMARY_BUTTON += "QPushButton:pressed {"
    PRIMARY_BUTTON += "    background-color: #1d4ed8;"
    PRIMARY_BUTTON += "}"
    PRIMARY_BUTTON += "QPushButton:disabled {"
    PRIMARY_BUTTON += "    background-color: #93c5fd;"
    PRIMARY_BUTTON += "    color: #eff6ff;"
    PRIMARY_BUTTON += "}"
    
    # 次要按钮样式
    SECONDARY_BUTTON = ""
    SECONDARY_BUTTON += "QPushButton {"
    SECONDARY_BUTTON += "    background-color: " + CARD_COLOR + ";"
    SECONDARY_BUTTON += "    color: " + TEXT_COLOR + ";"
    SECONDARY_BUTTON += "    border: 1px solid " + BORDER_COLOR + ";"
    SECONDARY_BUTTON += "    border-radius: 6px;"
    SECONDARY_BUTTON += "    padding: 8px 16px;"
    SECONDARY_BUTTON += "    font-size: 13px;"
    SECONDARY_BUTTON += "}"
    SECONDARY_BUTTON += "QPushButton:hover {"
    SECONDARY_BUTTON += "    background-color: #f1f5f9;"
    SECONDARY_BUTTON += "}"
    SECONDARY_BUTTON += "QPushButton:pressed {"
    SECONDARY_BUTTON += "    background-color: #e2e8f0;"
    SECONDARY_BUTTON += "}"
    SECONDARY_BUTTON += "QPushButton:disabled {"
    SECONDARY_BUTTON += "    background-color: " + CARD_COLOR + ";"
    SECONDARY_BUTTON += "    color: #94a3b8;"
    SECONDARY_BUTTON += "}"
    
    # 危险按钮样式
    DANGER_BUTTON = ""
    DANGER_BUTTON += "QPushButton {"
    DANGER_BUTTON += "    background-color: " + DANGER_COLOR + ";"
    DANGER_BUTTON += "    color: white;"
    DANGER_BUTTON += "    border: none;"
    DANGER_BUTTON += "    border-radius: 6px;"
    DANGER_BUTTON += "    padding: 8px 16px;"
    DANGER_BUTTON += "    font-size: 13px;"
    DANGER_BUTTON += "}"
    DANGER_BUTTON += "QPushButton:hover {"
    DANGER_BUTTON += "    background-color: #dc2626;"
    DANGER_BUTTON += "}"
    DANGER_BUTTON += "QPushButton:pressed {"
    DANGER_BUTTON += "    background-color: #b91c1c;"
    DANGER_BUTTON += "}"
    
    # 成功按钮样式
    SUCCESS_BUTTON = ""
    SUCCESS_BUTTON += "QPushButton {"
    SUCCESS_BUTTON += "    background-color: " + SUCCESS_COLOR + ";"
    SUCCESS_BUTTON += "    color: white;"
    SUCCESS_BUTTON += "    border: none;"
    SUCCESS_BUTTON += "    border-radius: 6px;"
    SUCCESS_BUTTON += "    padding: 8px 16px;"
    SUCCESS_BUTTON += "    font-size: 13px;"
    SUCCESS_BUTTON += "}"
    SUCCESS_BUTTON += "QPushButton:hover {"
    SUCCESS_BUTTON += "    background-color: #059669;"
    SUCCESS_BUTTON += "}"
    SUCCESS_BUTTON += "QPushButton:pressed {"
    SUCCESS_BUTTON += "    background-color: #047857;"
    SUCCESS_BUTTON += "}"
    
    # 组合框样式
    COMBO_BOX = ""
    COMBO_BOX += "QComboBox {"
    COMBO_BOX += "    background-color: " + CARD_COLOR + ";"
    COMBO_BOX += "    color: " + TEXT_COLOR + ";"
    COMBO_BOX += "    border: 1px solid " + BORDER_COLOR + ";"
    COMBO_BOX += "    border-radius: 6px;"
    COMBO_BOX += "    padding: 8px 12px;"
    COMBO_BOX += "    font-size: 13px;"
    COMBO_BOX += "}"
    COMBO_BOX += "QComboBox:hover {"
    COMBO_BOX += "    border: 1px solid " + PRIMARY_COLOR + ";"
    COMBO_BOX += "}"
    COMBO_BOX += "QComboBox:focus {"
    COMBO_BOX += "    border: 2px solid " + PRIMARY_COLOR + ";"
    COMBO_BOX += "    outline: none;"
    COMBO_BOX += "}"
    COMBO_BOX += "QComboBox::drop-down {"
    COMBO_BOX += "    border-left: 1px solid " + BORDER_COLOR + ";"
    COMBO_BOX += "    border-top-right-radius: 6px;"
    COMBO_BOX += "    border-bottom-right-radius: 6px;"
    COMBO_BOX += "}"
    COMBO_BOX += "QComboBox::down-arrow {"
    COMBO_BOX += "    width: 16px;"
    COMBO_BOX += "    height: 16px;"
    COMBO_BOX += "}"
    
    # 滑块样式
    SLIDER = ""
    SLIDER += "QSlider::groove:horizontal {"
    SLIDER += "    border: 1px solid " + BORDER_COLOR + ";"
    SLIDER += "    height: 6px;"
    SLIDER += "    border-radius: 3px;"
    SLIDER += "    background: #f1f5f9;"
    SLIDER += "}"
    SLIDER += "QSlider::handle:horizontal {"
    SLIDER += "    background: " + PRIMARY_COLOR + ";"
    SLIDER += "    border: 1px solid " + PRIMARY_COLOR + ";"
    SLIDER += "    width: 18px;"
    SLIDER += "    height: 18px;"
    SLIDER += "    border-radius: 9px;"
    SLIDER += "    margin: -6px 0;"
    SLIDER += "}"
    SLIDER += "QSlider::handle:horizontal:hover {"
    SLIDER += "    background: " + PRIMARY_HOVER + ";"
    SLIDER += "    border: 1px solid " + PRIMARY_HOVER + ";"
    SLIDER += "}"
    
    # 进度条样式
    PROGRESS_BAR = ""
    PROGRESS_BAR += "QProgressBar {"
    PROGRESS_BAR += "    background-color: #f1f5f9;"
    PROGRESS_BAR += "    border: 1px solid " + BORDER_COLOR + ";"
    PROGRESS_BAR += "    border-radius: 6px;"
    PROGRESS_BAR += "    text-align: center;"
    PROGRESS_BAR += "    font-size: 12px;"
    PROGRESS_BAR += "    color: " + TEXT_SECONDARY + ";"
    PROGRESS_BAR += "}"
    PROGRESS_BAR += "QProgressBar::chunk {"
    PROGRESS_BAR += "    background-color: " + PRIMARY_COLOR + ";"
    PROGRESS_BAR += "    border-radius: 5px;"
    PROGRESS_BAR += "}"
    
    # 分组框样式
    GROUP_BOX = ""
    GROUP_BOX += "QGroupBox {"
    GROUP_BOX += "    background-color: " + CARD_COLOR + ";"
    GROUP_BOX += "    color: " + TEXT_COLOR + ";"
    GROUP_BOX += "    border: 1px solid " + BORDER_COLOR + ";"
    GROUP_BOX += "    border-radius: 6px;"
    GROUP_BOX += "    margin-top: 0px;"
    GROUP_BOX += "    padding: 10px;"
    GROUP_BOX += "    min-height: 120px;"
    GROUP_BOX += "}"
    GROUP_BOX += "QGroupBox::title {"
    GROUP_BOX += "    subcontrol-origin: margin;"
    GROUP_BOX += "    subcontrol-position: top left;"
    GROUP_BOX += "    padding: 0 10px;"
    GROUP_BOX += "    top: 17px;"
    GROUP_BOX += "    left: 10px;"
    GROUP_BOX += "    background-color: " + CARD_COLOR + ";"
    GROUP_BOX += "    font-size: 14px;"
    GROUP_BOX += "    font-weight: 700;"
    GROUP_BOX += "    font-style: normal;"
    GROUP_BOX += "    text-decoration: none;"
    GROUP_BOX += "}"
    
    # 选项卡样式
    TAB_WIDGET = ""
    TAB_WIDGET += "QTabWidget::pane {"
    TAB_WIDGET += "    background-color: " + CARD_COLOR + ";"
    TAB_WIDGET += "    border: 1px solid " + BORDER_COLOR + ";"
    TAB_WIDGET += "    border-radius: 6px;"
    TAB_WIDGET += "    margin-top: 8px;"
    TAB_WIDGET += "}"
    TAB_WIDGET += "QTabBar::tab {"
    TAB_WIDGET += "    background-color: #f1f5f9;"
    TAB_WIDGET += "    color: " + TEXT_SECONDARY + ";"
    TAB_WIDGET += "    border: 1px solid " + BORDER_COLOR + ";"
    TAB_WIDGET += "    border-bottom: none;"
    TAB_WIDGET += "    border-top-left-radius: 6px;"
    TAB_WIDGET += "    border-top-right-radius: 6px;"
    TAB_WIDGET += "    padding: 10px 20px;"
    TAB_WIDGET += "    font-size: 13px;"
    TAB_WIDGET += "    margin-right: 2px;"
    TAB_WIDGET += "}"
    TAB_WIDGET += "QTabBar::tab:selected {"
    TAB_WIDGET += "    background-color: " + CARD_COLOR + ";"
    TAB_WIDGET += "    color: " + TEXT_COLOR + ";"
    TAB_WIDGET += "    border-bottom: 1px solid " + CARD_COLOR + ";"
    TAB_WIDGET += "}"
    TAB_WIDGET += "QTabBar::tab:hover {"
    TAB_WIDGET += "    background-color: #e2e8f0;"
    TAB_WIDGET += "}"
    
    # 分割器样式
    SPLITTER = ""
    SPLITTER += "QSplitter::handle {"
    SPLITTER += "    background-color: " + BORDER_COLOR + ";"
    SPLITTER += "}"
    SPLITTER += "QSplitter::handle:hover {"
    SPLITTER += "    background-color: " + SECONDARY_COLOR + ";"
    SPLITTER += "}"
    
    # 状态标签样式
    STATUS_LABEL = ""
    STATUS_LABEL += "QLabel {"
    STATUS_LABEL += "    color: " + TEXT_SECONDARY + ";"
    STATUS_LABEL += "    font-size: 12px;"
    STATUS_LABEL += "    padding: 4px 0;"
    STATUS_LABEL += "}"
    
    # 按钮容器布局
    BUTTON_LAYOUT = ""
    
    @classmethod
    def get_button_style(cls, button_type="primary") -> str:
        """
        获取按钮样式
        
        Args:
            button_type: 按钮类型 (primary, secondary, success, danger)
            
        Returns:
            按钮样式字符串
        """
        styles = {
            "primary": cls.PRIMARY_BUTTON,
            "secondary": cls.SECONDARY_BUTTON,
            "success": cls.SUCCESS_BUTTON,
            "danger": cls.DANGER_BUTTON
        }
        return styles.get(button_type, cls.SECONDARY_BUTTON)

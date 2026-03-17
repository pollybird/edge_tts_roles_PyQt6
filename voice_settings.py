"""语音设置相关类"""
from dataclasses import dataclass
import asyncio

import edge_tts
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QSlider, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

# 导入样式
from styles import Styles


@dataclass
class VoiceSettings:
    """角色语音设置"""
    role: str
    voice: str = "zh-CN-XiaoxiaoNeural"
    rate: int = 0
    volume: int = 0
    pitch: int = 0


class VoiceSettingsWidget(QWidget):
    """单个角色的语音设置控件"""
    
    def __init__(self, role: str, parent=None):
        super().__init__(parent)
        self.role = role
        self.voices = []
        self.init_ui()
        # 不立即加载语音列表，改为在需要时加载
        self.voices_loaded = False
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 角色标签
        self.role_label = QLabel(f"角色 {self.role}")
        self.role_label.setStyleSheet(Styles.HEADER_LABEL)
        layout.addWidget(self.role_label)
        
        # 发音人选择
        voice_label = QLabel("发音人:")
        voice_label.setStyleSheet(Styles.LABEL)
        layout.addWidget(voice_label)
        self.voice_combo = QComboBox()
        self.voice_combo.setStyleSheet(Styles.COMBO_BOX)
        layout.addWidget(self.voice_combo)
        
        # 添加一些常用语音作为默认选项
        self.add_default_voices()
        
        # 加载语音按钮
        self.load_voices_btn = QPushButton("加载语音列表")
        self.load_voices_btn.setStyleSheet(Styles.get_button_style("secondary"))
        # 添加图标
        self.load_voices_btn.setText("🔄 加载语音列表")
        self.load_voices_btn.clicked.connect(self.load_voices)
        layout.addWidget(self.load_voices_btn)
        
        # 语速调整
        rate_label = QLabel("语速:")
        rate_label.setStyleSheet(Styles.LABEL)
        layout.addWidget(rate_label)
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setStyleSheet(Styles.SLIDER)
        self.rate_slider.setRange(-100, 100)
        self.rate_slider.setValue(0)
        self.rate_label = QLabel("0%")
        self.rate_label.setStyleSheet(Styles.LABEL)
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(self.rate_slider)
        rate_layout.addWidget(self.rate_label)
        layout.addLayout(rate_layout)
        
        # 音量调整
        volume_label = QLabel("音量:")
        volume_label.setStyleSheet(Styles.LABEL)
        layout.addWidget(volume_label)
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setStyleSheet(Styles.SLIDER)
        self.volume_slider.setRange(-100, 100)
        self.volume_slider.setValue(0)
        self.volume_label = QLabel("0%")
        self.volume_label.setStyleSheet(Styles.LABEL)
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(self.volume_label)
        layout.addLayout(volume_layout)
        
        # 语调调整
        pitch_label = QLabel("语调:")
        pitch_label.setStyleSheet(Styles.LABEL)
        layout.addWidget(pitch_label)
        self.pitch_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_slider.setStyleSheet(Styles.SLIDER)
        self.pitch_slider.setRange(-100, 100)
        self.pitch_slider.setValue(0)
        self.pitch_label = QLabel("0Hz")
        self.pitch_label.setStyleSheet(Styles.LABEL)
        pitch_layout = QHBoxLayout()
        pitch_layout.addWidget(self.pitch_slider)
        pitch_layout.addWidget(self.pitch_label)
        layout.addLayout(pitch_layout)
        
        # 连接信号
        self.rate_slider.valueChanged.connect(
            lambda v: self.rate_label.setText(f"{v:+d}%"))
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_label.setText(f"{v:+d}%"))
        self.pitch_slider.valueChanged.connect(
            lambda v: self.pitch_label.setText(f"{v:+d}Hz"))
        
        self.setLayout(layout)
    
    def add_default_voices(self):
        """添加默认语音选项"""
        self.voice_combo.clear()
        
        # 添加常用中文语音
        default_voices = [
            ("zh-CN-XiaoxiaoNeural", "晓晓 (中文)"),
            ("zh-CN-XiaoyiNeural", "晓伊 (中文)"),
            ("zh-CN-YunjianNeural", "云健 (中文)"),
            ("zh-CN-YunxiNeural", "云希 (中文)"),
            ("zh-CN-YunxiaNeural", "云夏 (中文)"),
            ("zh-CN-YunyangNeural", "云扬 (中文)"),
            ("en-US-JennyNeural", "Jenny (英文)"),
            ("en-US-GuyNeural", "Guy (英文)"),
            ("en-GB-SoniaNeural", "Sonia (英式英文)"),
            ("ja-JP-NanamiNeural", "七海 (日语)"),
            ("ko-KR-SunHiNeural", "선히 (韩语)"),
        ]
        
        for voice_id, voice_name in default_voices:
            self.voice_combo.addItem(f"{voice_name} - {voice_id}", voice_id)
        
        # 设置默认选择
        self.voice_combo.setCurrentIndex(0)
    
    def load_voices(self):
        """加载语音列表"""
        self.load_voices_btn.setEnabled(False)
        self.load_voices_btn.setText("正在加载...")
        QApplication.processEvents()  # 更新UI
        
        try:
            # 在新线程中加载语音列表
            asyncio.run(self.load_voices_async())
        except Exception as e:
            print(f"加载语音列表失败: {e}")
            self.load_voices_btn.setText("加载失败，点击重试")
            self.load_voices_btn.setEnabled(True)
    
    async def load_voices_async(self):
        """异步加载语音列表"""
        try:
            voices = await edge_tts.list_voices()
            self.voices = voices
            
            # 在主线程中更新UI
            self.update_voices_list()
            self.load_voices_btn.setText("语音列表已加载")
            self.voices_loaded = True
            
        except Exception as e:
            print(f"加载语音列表失败: {e}")
            self.load_voices_btn.setText("加载失败，点击重试")
            self.load_voices_btn.setEnabled(True)
    
    def update_voices_list(self):
        """更新语音列表到下拉框"""
        if not self.voices:
            return
        
        # 备份当前选择的语音
        current_voice = self.voice_combo.currentData()
        
        # 清空并重新添加默认语音
        self.voice_combo.clear()
        
        # 分离中文和英文语音
        chinese_voices = []
        english_voices = []
        other_voices = []
        
        for voice in self.voices:
            short_name = voice.get('ShortName', '')
            if 'zh-CN' in short_name or 'zh-TW' in short_name or 'zh-HK' in short_name:
                chinese_voices.append(voice)
            elif 'en-' in short_name:
                english_voices.append(voice)
            else:
                other_voices.append(voice)
        
        # 添加中文语音
        if chinese_voices:
            self.voice_combo.addItem("--- 中文语音 ---")
            for voice in chinese_voices:
                short_name = voice.get('ShortName', 'Unknown')
                friendly_name = voice.get('FriendlyName', voice.get('LocalName', short_name))
                gender = voice.get('Gender', '')
                locale = voice.get('Locale', '')
                
                display_name = f"{friendly_name} - {short_name}"
                if gender:
                    display_name += f" ({gender})"
                
                self.voice_combo.addItem(display_name, short_name)
        
        # 添加英文语音
        if english_voices:
            self.voice_combo.addItem("--- 英文语音 ---")
            for voice in english_voices:
                short_name = voice.get('ShortName', 'Unknown')
                friendly_name = voice.get('FriendlyName', voice.get('LocalName', short_name))
                gender = voice.get('Gender', '')
                locale = voice.get('Locale', '')
                
                display_name = f"{friendly_name} - {short_name}"
                if gender:
                    display_name += f" ({gender})"
                
                self.voice_combo.addItem(display_name, short_name)
        
        # 添加其他语音
        if other_voices:
            self.voice_combo.addItem("--- 其他语音 ---")
            for voice in other_voices:
                short_name = voice.get('ShortName', 'Unknown')
                friendly_name = voice.get('FriendlyName', voice.get('LocalName', short_name))
                gender = voice.get('Gender', '')
                locale = voice.get('Locale', '')
                
                display_name = f"{friendly_name} - {short_name}"
                if gender:
                    display_name += f" ({gender})"
                
                self.voice_combo.addItem(display_name, short_name)
        
        # 恢复之前选择的语音
        if current_voice:
            index = self.voice_combo.findData(current_voice)
            if index >= 0:
                self.voice_combo.setCurrentIndex(index)
        else:
            # 设置默认选择
            self.voice_combo.setCurrentIndex(0)
    
    def get_settings(self) -> VoiceSettings:
        """获取当前设置"""
        voice = self.voice_combo.currentData() or "zh-CN-XiaoxiaoNeural"
        return VoiceSettings(
            role=self.role,
            voice=voice,
            rate=self.rate_slider.value(),
            volume=self.volume_slider.value(),
            pitch=self.pitch_slider.value()
        )
    
    def set_settings(self, settings: VoiceSettings):
        """应用设置"""
        index = self.voice_combo.findData(settings.voice)
        if index >= 0:
            self.voice_combo.setCurrentIndex(index)
        self.rate_slider.setValue(settings.rate)
        self.volume_slider.setValue(settings.volume)
        self.pitch_slider.setValue(settings.pitch)
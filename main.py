"""主程序入口- Edge-TTS多角色音频生成器"""
import sys
import os
import re
import asyncio
import json
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QComboBox, QSpinBox,
    QGroupBox, QFileDialog, QMessageBox, QTabWidget,
    QProgressBar, QSplitter
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont, QIcon

# 导入样式
from styles import Styles

# 导入模块
from voice_settings import VoiceSettingsWidget, VoiceSettings
from text_highlighter import TextHighlighter
from preview_dialog import PreviewDialog
from tts_workers import TTSWorker, PreviewWorker


class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.preview_worker = None
        self.preview_dialog = None
        self.settings = QSettings("EdgeTTS", "MultiRoleAudioGenerator")
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("Edge-TTS 多角色音频生成器")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置窗口图标
        from PyQt6.QtGui import QIcon
        self.setWindowIcon(QIcon('app_icon.ico'))
        
        # 应用主窗口样式
        self.setStyleSheet(Styles.MAIN_WINDOW)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建分割器，将文本编辑区和角色设置区分隔开
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet(Styles.SPLITTER)
        
        # 左侧：文本编辑区
        left_widget = self.create_left_panel()
        splitter.addWidget(left_widget)
        
        # 右侧：角色设置区
        right_widget = self.create_right_panel()
        splitter.addWidget(right_widget)
        
        # 设置分割器比例，增加右侧宽度
        splitter.setSizes([600, 600])
        main_layout.addWidget(splitter)
    
    def create_left_panel(self) -> QWidget:
        """创建左侧面板（文本编辑区）"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 标题标签
        title_label = QLabel("文本编辑区（使用[A][B][C][D]切换角色，[数字]停顿，[R]蜂鸣声）:")
        title_label.setStyleSheet(Styles.HEADER_LABEL)
        left_layout.addWidget(title_label)
        
        # 文本编辑�?
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("微软雅黑", 11))
        self.text_edit.setStyleSheet(Styles.TEXT_EDIT)
        self.text_edit.setPlaceholderText(
            "输入要转换为语音的文本..\n\n"
            "标记说明：\n"
            "[A] [B] [C] [D] - 切换角色\n"
            "[数字] - 停顿指定毫秒数（如[1000]表示1秒）\n"
            "[R] - 添加蜂鸣声\n\n"
            "示例：\n"
            "[A]你好，我是角色A。[B]我是角色B。[1000][C]停顿1秒后，我是角色C。[R]"
        )
        
        # 设置高亮�?
        self.highlighter = TextHighlighter(self.text_edit.document())
        left_layout.addWidget(self.text_edit)
        
        # 文本操作按钮
        self.create_text_buttons(left_layout)
        
        # 试听按钮
        self.create_preview_buttons(left_layout)
        
        # 蜂鸣声设�?
        self.create_beep_settings(left_layout)
        
        # 版权信息标签
        copyright_note = QLabel("© 2026 泰州姜堰钟毓信息技术有限公司")
        copyright_note.setStyleSheet(Styles.NOTE_LABEL)
        left_layout.addWidget(copyright_note)
        
        return left_widget
    
    def create_text_buttons(self, layout: QVBoxLayout):
        """创建文本操作按钮"""
        button_layout = QHBoxLayout()
        
        # 角色标记按钮
        role_buttons = [
            ("插入[A]", "[A]"),
            ("插入[B]", "[B]"),
            ("插入[C]", "[C]"),
            ("插入[D]", "[D]"),
        ]
        
        for label, tag in role_buttons:
            btn = QPushButton(label)
            btn.setStyleSheet(Styles.get_button_style("secondary"))
            # 添加角色图标
            icon_char = "👤"  # 人物图标
            btn.setText(f"{icon_char} {label}")
            btn.clicked.connect(lambda checked, t=tag: self.insert_tag(t))
            button_layout.addWidget(btn)
        
        # 停顿设置部分
        pause_container = QWidget()
        pause_layout = QHBoxLayout(pause_container)
        pause_layout.setContentsMargins(0, 0, 0, 0)
        
        self.insert_pause_btn = QPushButton("插入停顿")
        self.insert_pause_btn.setStyleSheet(Styles.get_button_style("secondary"))
        # 添加图标
        self.insert_pause_btn.setText("⏱️ 插入停顿")
        self.insert_pause_btn.clicked.connect(self.insert_pause)
        pause_layout.addWidget(self.insert_pause_btn)
        
        # 停顿时间输入�?
        pause_input_layout = QHBoxLayout()
        pause_label = QLabel("时间(ms):")
        pause_label.setStyleSheet(Styles.LABEL)
        pause_input_layout.addWidget(pause_label)
        self.pause_spinbox = QSpinBox()
        self.pause_spinbox.setRange(10, 10000)  # 10毫秒到10秒
        self.pause_spinbox.setValue(1000)  # 默认1秒
        self.pause_spinbox.setSuffix(" ms")
        self.pause_spinbox.setMaximumWidth(120)
        pause_input_layout.addWidget(self.pause_spinbox)
        
        pause_layout.addLayout(pause_input_layout)
        button_layout.addWidget(pause_container)
        
        # 蜂鸣按钮
        self.insert_beep_btn = QPushButton("插入蜂鸣[R]")
        self.insert_beep_btn.setStyleSheet(Styles.get_button_style("secondary"))
        # 添加图标
        self.insert_beep_btn.setText("🔊 插入蜂鸣[R]")
        self.insert_beep_btn.clicked.connect(lambda: self.insert_tag("[R]"))
        button_layout.addWidget(self.insert_beep_btn)
        
        layout.addLayout(button_layout)
        
        # 快速停顿按�?
        quick_pause_layout = QHBoxLayout()
        quick_pause_label = QLabel("快速停顿:")
        quick_pause_label.setStyleSheet(Styles.LABEL)
        quick_pause_layout.addWidget(quick_pause_label)
        
        quick_pause_buttons = [
            ("0.5秒", 500),
            ("1秒", 1000),
            ("2秒", 2000),
            ("3秒", 3000),
            ("5秒", 5000),
        ]
        
        for label, duration in quick_pause_buttons:
            btn = QPushButton(label)
            btn.setStyleSheet(Styles.get_button_style("secondary"))
            # 添加图标
            btn.setText(f"⏱️ {label}")
            btn.clicked.connect(lambda checked, d=duration: self.insert_quick_pause(d))
            btn.setMaximumWidth(90)
            quick_pause_layout.addWidget(btn)
        
        layout.addLayout(quick_pause_layout)
        
        # 文本文件操作按钮
        file_layout = QHBoxLayout()
        
        open_btn = QPushButton("打开文本")
        open_btn.setStyleSheet(Styles.get_button_style("secondary"))
        # 添加图标
        open_btn.setText("📂 打开文本")
        open_btn.clicked.connect(self.open_text)
        file_layout.addWidget(open_btn)
        
        save_btn = QPushButton("保存文本")
        save_btn.setStyleSheet(Styles.get_button_style("secondary"))
        # 添加图标
        save_btn.setText("💾 保存文本")
        save_btn.clicked.connect(self.save_text)
        file_layout.addWidget(save_btn)
        
        layout.addLayout(file_layout)
    
    def create_preview_buttons(self, layout: QVBoxLayout):
        """创建试听按钮"""
        preview_layout = QHBoxLayout()
        preview_label = QLabel("试听功能:")
        preview_label.setStyleSheet(Styles.LABEL)
        preview_layout.addWidget(preview_label)
        
        self.preview_selection_btn = QPushButton("试听选中文本")
        self.preview_selection_btn.setStyleSheet(Styles.get_button_style("primary"))
        # 添加图标
        self.preview_selection_btn.setText("🎧 试听选中文本")
        self.preview_selection_btn.clicked.connect(lambda: self.preview_audio(True))
        self.preview_selection_btn.setToolTip("试听当前选中的文本（支持多角色）")
        preview_layout.addWidget(self.preview_selection_btn)
        
        self.preview_all_btn = QPushButton("试听全部文本")
        self.preview_all_btn.setStyleSheet(Styles.get_button_style("primary"))
        # 添加图标
        self.preview_all_btn.setText("🔊 试听全部文本")
        self.preview_all_btn.clicked.connect(lambda: self.preview_audio(False))
        self.preview_all_btn.setToolTip("试听所有文本内容（支持多角色）")
        preview_layout.addWidget(self.preview_all_btn)
        
        layout.addLayout(preview_layout)
    
    def create_beep_settings(self, layout: QVBoxLayout):
        """创建蜂鸣声设置"""
        beep_layout = QHBoxLayout()
        beep_label = QLabel("蜂鸣声文本:")
        beep_label.setStyleSheet(Styles.LABEL)
        beep_layout.addWidget(beep_label)
        self.beep_file_edit = QTextEdit()
        self.beep_file_edit.setStyleSheet(Styles.TEXT_EDIT)
        self.beep_file_edit.setMaximumHeight(30)
        beep_layout.addWidget(self.beep_file_edit, 1)
        self.beep_browse_btn = QPushButton("浏览")
        self.beep_browse_btn.setStyleSheet(Styles.get_button_style("secondary"))
        # 添加图标
        self.beep_browse_btn.setText("📁 浏览")
        self.beep_browse_btn.clicked.connect(self.browse_beep_file)
        beep_layout.addWidget(self.beep_browse_btn)
        layout.addLayout(beep_layout)
    
    def create_right_panel(self) -> QWidget:
        """创建右侧面板（角色设置和输出设置）"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(Styles.TAB_WIDGET)
        
        # 角色设置
        self.role_a_widget = VoiceSettingsWidget('A')
        self.role_b_widget = VoiceSettingsWidget('B')
        self.role_c_widget = VoiceSettingsWidget('C')
        self.role_d_widget = VoiceSettingsWidget('D')
        
        tab_widget.addTab(self.role_a_widget, "角色 A")
        tab_widget.addTab(self.role_b_widget, "角色 B")
        tab_widget.addTab(self.role_c_widget, "角色 C")
        tab_widget.addTab(self.role_d_widget, "角色 D")
        
        right_layout.addWidget(tab_widget)
        
        # 输出设置
        self.create_output_settings(right_layout)
        
        # 进度�?
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(Styles.PROGRESS_BAR)
        right_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet(Styles.STATUS_LABEL)
        right_layout.addWidget(self.status_label)
        
        # 控制按钮
        self.create_control_buttons(right_layout)
        
        return right_widget
    
    def create_output_settings(self, layout: QVBoxLayout):
        """创建输出设置"""
        output_group = QGroupBox("输出设置")
        output_group.setStyleSheet(Styles.GROUP_BOX)
        output_layout = QVBoxLayout()
        
        # 文件选择
        file_layout = QHBoxLayout()
        file_label = QLabel("输出文件:")
        file_label.setStyleSheet(Styles.LABEL)
        file_layout.addWidget(file_label)
        self.output_file_edit = QTextEdit()
        self.output_file_edit.setStyleSheet(Styles.TEXT_EDIT)
        self.output_file_edit.setMaximumHeight(40)  # 增加高度
        self.output_file_edit.setText("output.wav")  # 默认使用WAV格式
        file_layout.addWidget(self.output_file_edit, 1)
        self.browse_btn = QPushButton("浏览")
        self.browse_btn.setStyleSheet(Styles.get_button_style("secondary"))
        # 添加图标
        self.browse_btn.setText("💾 浏览")
        self.browse_btn.clicked.connect(self.browse_output_file)
        file_layout.addWidget(self.browse_btn)
        output_layout.addLayout(file_layout)
        
        # 格式选择
        format_layout = QHBoxLayout()
        format_label = QLabel("输出格式:")
        format_label.setStyleSheet(Styles.LABEL)
        format_layout.addWidget(format_label)
        self.format_combo = QComboBox()
        self.format_combo.setStyleSheet(Styles.COMBO_BOX)
        self.format_combo.addItems(["WAV", "MP3", "OGG", "FLAC"])
        self.format_combo.setCurrentText("WAV")
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo)
        output_layout.addLayout(format_layout)
        
        # 降低输出设置区域的高�?
        output_group.setMinimumHeight(120)
        
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
    
    def create_control_buttons(self, layout: QVBoxLayout):
        """创建控制按钮"""
        control_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("生成音频")
        self.generate_btn.setStyleSheet(Styles.get_button_style("primary"))
        # 添加图标
        self.generate_btn.setText("🎵 生成音频")
        self.generate_btn.clicked.connect(self.generate_audio)
        control_layout.addWidget(self.generate_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setStyleSheet(Styles.get_button_style("danger"))
        # 添加图标
        self.stop_btn.setText("⏹️ 停止")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_generation)
        control_layout.addWidget(self.stop_btn)
        
        layout.addLayout(control_layout)
    
    def insert_tag(self, tag):
        """插入标记到文本"""
        cursor = self.text_edit.textCursor()
        cursor.insertText(tag)
    
    def insert_pause(self):
        """插入停顿标记，使用输入框中的数值"""
        cursor = self.text_edit.textCursor()
        pause_time = self.pause_spinbox.value()
        cursor.insertText(f"[{pause_time}]")
    
    def insert_quick_pause(self, duration_ms):
        """插入快速停顿标记"""
        cursor = self.text_edit.textCursor()
        cursor.insertText(f"[{duration_ms}]")
    
    def save_text(self):
        """保存文本到文本文件"""
        from PyQt6.QtWidgets import QFileDialog
        
        # 打开文件保存对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存文本文件", "", "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_edit.toPlainText())
                # 可以添加保存成功的提示
                QMessageBox.information(self, "成功", "文本已成功保存！")
            except Exception as e:
                print(f"保存文件失败: {e}")
    
    def open_text(self):
        """从文件打开文本"""
        from PyQt6.QtWidgets import QFileDialog
        
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开文本文件", "", "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.text_edit.setPlainText(content)
                # 可以添加打开成功的提示
                QMessageBox.information(self, "成功", "文本已成功打开！")
            except Exception as e:
                print(f"打开文件失败: {e}")
    
    def preview_audio(self, selection_only: bool = False):
        """试听音频（支持多角色）"""
        from PyQt6.QtWidgets import QMessageBox
        import re
        import os
        
        text = ""
        
        if selection_only:
            # 获取选中的文本
            cursor = self.text_edit.textCursor()
            if cursor.hasSelection():
                text = cursor.selectedText()
            else:
                QMessageBox.warning(self, "警告", "请先选中要试听的文本！")
                return
        else:
            # 获取全部文本
            text = self.text_edit.toPlainText().strip()
            if not text:
                QMessageBox.warning(self, "警告", "请输入文本！")
                return
        
        # 获取所有角色的语音设置
        voice_settings = self.get_voice_settings()
        
        # 获取蜂鸣声文本
        beep_file = self.beep_file_edit.toPlainText().strip()
        if beep_file and not os.path.exists(beep_file):
            beep_file = None  # 如果文件不存在，使用默认蜂鸣�?
        
        # 检查文本中是否有角色标记
        has_role_markers = bool(re.search(r'\[[ABCD]\]', text))
        
        if not has_role_markers:
            # 如果没有角色标记，添加一个默认标记以确保使用角色A
            text = f"[A]{text}"
        
        # 显示试听状态
        self.status_label.setText("正在生成试听音频...")
        
        # 如果之前有试听工作线程在运行，先停止
        if self.preview_worker and self.preview_worker.isRunning():
            self.preview_worker.stop()
            self.preview_worker.wait()
        
        # 创建试听工作线程（支持多角色）
        self.preview_worker = PreviewWorker(
            text=text,
            voice_settings=voice_settings,
            is_selection=selection_only,
            beep_file=beep_file if beep_file else None
        )
        
        self.preview_worker.progress.connect(self.update_preview_progress)
        self.preview_worker.finished.connect(self.on_preview_finished)
        self.preview_worker.error.connect(self.on_preview_error)
        
        self.preview_worker.start()
    
    def update_preview_progress(self, value: int, message: str):
        """更新试听进度"""
        self.status_label.setText(f"试听: {message}")
        self.progress_bar.setValue(value)
    
    def on_preview_finished(self, audio_file: str, success: bool):
        """试听生成完成"""
        if success:
            self.status_label.setText("试听音频已生成！")
            self.progress_bar.setValue(100)
            
            # 创建或显示试听对话框
            if not self.preview_dialog:
                self.preview_dialog = PreviewDialog(self)
                self.preview_dialog.finished.connect(self.on_preview_dialog_closed)
            
            # 加载音频文件
            self.preview_dialog.load_audio(audio_file)
            
            # 显示对话框
            self.preview_dialog.show()
            self.preview_dialog.raise_()
            self.preview_dialog.activateWindow()
        else:
            self.status_label.setText("试听生成失败")
            self.progress_bar.setValue(0)
    
    def on_preview_dialog_closed(self, result):
        """试听对话框关闭事件"""
        if result == QDialog.DialogCode.Accepted:
            # 用户点击了播放按钮，播放音频
            self.preview_dialog.play_audio()
        else:
            # 用户点击了取消按钮，清理临时文件
            self.preview_dialog.cleanup()
        # 清理试听工作线程的临时文件
        if self.preview_worker:
            self.preview_worker.cleanup()
        self.progress_bar.setValue(0)
    
    def on_preview_error(self, error_message: str):
        """试听生成出错"""
        self.status_label.setText(f"试听错误: {error_message}")
        self.progress_bar.setValue(0)
        QMessageBox.critical(self, "试听错误", error_message)
    
    def browse_output_file(self):
        """浏览输出文件"""
        current_format = self.format_combo.currentText().lower()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "选择输出文件", "", 
            f"音频文件 (*.{current_format} *.wav *.mp3 *.ogg *.flac)"
        )
        if file_path:
            self.output_file_edit.setText(file_path)
            # 根据文件扩展名更新格式选择
            ext = Path(file_path).suffix[1:].upper()
            if ext and ext in ["WAV", "MP3", "OGG", "FLAC"]:
                self.format_combo.setCurrentText(ext)
    
    def on_format_changed(self, format_name):
        """格式改变时更新文件扩展名"""
        current_file = self.output_file_edit.toPlainText().strip()
        if current_file:
            # 替换文件扩展名
            new_file = Path(current_file).with_suffix(f".{format_name.lower()}")
            self.output_file_edit.setText(str(new_file))
    
    def browse_beep_file(self):
        """浏览蜂鸣声文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择蜂鸣声文件", "", "音频文件 (*.wav *.mp3 *.ogg *.flac)"
        )
        if file_path:
            self.beep_file_edit.setText(file_path)
    
    def get_voice_settings(self) -> dict:
        """获取所有角色的语音设置"""
        return {
            'A': self.role_a_widget.get_settings(),
            'B': self.role_b_widget.get_settings(),
            'C': self.role_c_widget.get_settings(),
            'D': self.role_d_widget.get_settings(),
        }
    
    def generate_audio(self):
        """生成音频"""
        text = self.text_edit.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "警告", "请输入文本！")
            return
        
        output_path = self.output_file_edit.toPlainText().strip()
        if not output_path:
            QMessageBox.warning(self, "警告", "请选择输出文件路径！")
            return
        
        beep_file = self.beep_file_edit.toPlainText().strip()
        if beep_file and not os.path.exists(beep_file):
            QMessageBox.warning(self, "警告", "蜂鸣声文件不存在！")
            return
        
        # 创建并启动工作线程（支持多角色）
        self.worker = TTSWorker(
            text=text,
            voice_settings=self.get_voice_settings(),
            output_path=output_path,
            beep_file=beep_file if beep_file else None
        )
        
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_generation_finished)
        self.worker.error.connect(self.on_generation_error)
        
        # 更新UI状态
        self.generate_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在生成音频...")
        
        self.worker.start()
    
    def stop_generation(self):
        """停止生成"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
            self.status_label.setText("已停止生成！")
            self.progress_bar.setValue(0)
    
    def update_progress(self, value: int, message: str):
        """更新进度"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def on_generation_finished(self, output_path: str, success: bool):
        """生成完成"""
        self.generate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        if success:
            self.status_label.setText(f"音频已生成！ {output_path}")
            QMessageBox.information(self, "成功", f"音频已生成到:\n{output_path}")
            self.save_settings()
        self.progress_bar.setValue(100)
    
    def on_generation_error(self, error_message: str):
        """生成出错"""
        self.generate_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText(f"错误: {error_message}")
        self.progress_bar.setValue(0)
        QMessageBox.critical(self, "错误", error_message)
    
    def save_settings(self):
        """保存设置到配置文件"""
        settings_data = {
            'A': self.role_a_widget.get_settings().__dict__,
            'B': self.role_b_widget.get_settings().__dict__,
            'C': self.role_c_widget.get_settings().__dict__,
            'D': self.role_d_widget.get_settings().__dict__,
        }
        self.settings.setValue('voice_settings', json.dumps(settings_data))
        # 保存停顿时间设置
        self.settings.setValue('pause_duration', self.pause_spinbox.value())
    
    def load_settings(self):
        """从配置文件加载设置"""
        settings_json = self.settings.value('voice_settings')
        if settings_json:
            try:
                settings_data = json.loads(settings_json)
                from voice_settings import VoiceSettings
                for role, data in settings_data.items():
                    voice_settings = VoiceSettings(**data)
                    if role == 'A':
                        self.role_a_widget.set_settings(voice_settings)
                    elif role == 'B':
                        self.role_b_widget.set_settings(voice_settings)
                    elif role == 'C':
                        self.role_c_widget.set_settings(voice_settings)
                    elif role == 'D':
                        self.role_d_widget.set_settings(voice_settings)
            except Exception as e:
                print(f"加载设置失败: {e}")
                pass  # 如果加载失败，使用默认设置
        
        # 加载停顿时间设置
        pause_duration = self.settings.value('pause_duration')
        if pause_duration:
            try:
                self.pause_spinbox.setValue(int(pause_duration))
            except:
                pass
    
    def closeEvent(self, event):
        """关闭窗口事件"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        
        if self.preview_worker and self.preview_worker.isRunning():
            self.preview_worker.stop()
            self.preview_worker.wait()
            if hasattr(self.preview_worker, 'cleanup'):
                self.preview_worker.cleanup()
        
        # 关闭试听对话框
        if self.preview_dialog:
            self.preview_dialog.close()
        
        self.save_settings()
        event.accept()


def check_network_connection():
    """检查网络连接是否正常"""
    try:
        # 尝试连接到一个可靠的公共 DNS 服务器
        import socket
        socket.create_connection(('8.8.8.8', 53), timeout=5)
        return True
    except OSError:
        return False

def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 检查网络连接
    if not check_network_connection():
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(None, "网络连接异常", "检测到网络连接异常，程序将退出。")
        sys.exit(1)
    
    window = MainWindow()
    window.showMaximized()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    # 确保asyncio事件循环在Windows上正常工作
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    main()

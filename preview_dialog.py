"""试听对话框类"""
from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QSlider, QPushButton
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

# 导入样式
from styles import Styles


class PreviewDialog(QDialog):
    """试听对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("音频试听")
        self.setGeometry(200, 200, 500, 200)
        self.init_ui()
        self.media_player = None
        self.audio_output = None
        self.current_file = None
        
    def init_ui(self):
        # 应用对话框样式
        self.setStyleSheet(Styles.MAIN_WINDOW)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("音频试听")
        title_label.setStyleSheet(Styles.HEADER_LABEL)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 进度条
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setStyleSheet(Styles.SLIDER)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderMoved.connect(self.seek_position)
        
        progress_label = QLabel("播放进度:")
        progress_label.setStyleSheet(Styles.LABEL)
        layout.addWidget(progress_label)
        layout.addWidget(self.progress_slider)
        
        # 时间标签
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setStyleSheet(Styles.LABEL)
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.time_label)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.play_btn = QPushButton("播放")
        self.play_btn.setStyleSheet(Styles.get_button_style("primary"))
        self.play_btn.setText("▶️ 播放")
        self.play_btn.clicked.connect(self.play_audio)
        control_layout.addWidget(self.play_btn)
        
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.setStyleSheet(Styles.get_button_style("secondary"))
        self.pause_btn.setText("⏸️ 暂停")
        self.pause_btn.clicked.connect(self.pause_audio)
        self.pause_btn.setEnabled(False)
        control_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setStyleSheet(Styles.get_button_style("danger"))
        self.stop_btn.setText("⏹️ 停止")
        self.stop_btn.clicked.connect(self.stop_audio)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        layout.addLayout(control_layout)
        
        # 音量控制
        volume_layout = QHBoxLayout()
        volume_label = QLabel("音量:")
        volume_label.setStyleSheet(Styles.LABEL)
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setStyleSheet(Styles.SLIDER)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self.set_volume)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("80%")
        self.volume_label.setStyleSheet(Styles.LABEL)
        volume_layout.addWidget(self.volume_label)
        layout.addLayout(volume_layout)
        
        # 状态标签
        self.status_label = QLabel("准备播放")
        self.status_label.setStyleSheet(Styles.STATUS_LABEL)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 关闭按钮
        self.close_btn = QPushButton("关闭")
        self.close_btn.setStyleSheet(Styles.get_button_style("secondary"))
        self.close_btn.setText("❌ 关闭")
        self.close_btn.clicked.connect(self.close)
        layout.addWidget(self.close_btn)
        
        self.setLayout(layout)
        
        # 连接音量滑块信号
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_label.setText(f"{v}%"))
        
        # 初始化媒体播放器
        self.init_media_player()
    
    def init_media_player(self):
        """初始化媒体播放器"""
        try:
            self.media_player = QMediaPlayer()
            self.audio_output = QAudioOutput()
            self.media_player.setAudioOutput(self.audio_output)
            
            # 连接信号
            self.media_player.positionChanged.connect(self.update_position)
            self.media_player.durationChanged.connect(self.update_duration)
            self.media_player.playbackStateChanged.connect(self.update_playback_state)
            self.media_player.errorOccurred.connect(self.on_player_error)
            
            # 设置初始音量
            self.set_volume(self.volume_slider.value())
            
        except Exception as e:
            print(f"初始化媒体播放器失败: {e}")
            self.status_label.setText("媒体播放器初始化失败")
    
    def load_audio(self, file_path: str):
        """加载音频文件"""
        self.current_file = file_path
        
        if not self.media_player:
            self.init_media_player()
        
        if self.media_player:
            try:
                # 将文件路径转换为QUrl
                url = QUrl.fromLocalFile(file_path)
                self.media_player.setSource(url)
                
                self.status_label.setText(f"已加载音频: {Path(file_path).name}")
                self.play_btn.setEnabled(True)
            except Exception as e:
                print(f"加载音频失败: {e}")
                self.status_label.setText(f"加载音频失败: {e}")
                self.play_btn.setEnabled(False)
        else:
            self.status_label.setText("媒体播放器不可用")
            self.play_btn.setEnabled(False)
    
    def play_audio(self):
        """播放音频"""
        if self.media_player:
            self.media_player.play()
            self.status_label.setText("正在播放...")
    
    def pause_audio(self):
        """暂停音频"""
        if self.media_player:
            self.media_player.pause()
            self.status_label.setText("已暂停")
    
    def stop_audio(self):
        """停止音频"""
        if self.media_player:
            self.media_player.stop()
            self.status_label.setText("已停止")
    
    def seek_position(self, position):
        """跳转到指定位置"""
        if self.media_player and self.media_player.duration() > 0:
            new_position = int((position / 100.0) * self.media_player.duration())
            self.media_player.setPosition(new_position)
    
    def set_volume(self, volume: int):
        """设置音量"""
        if self.audio_output:
            # 转换为线性音量（0.0-1.0）
            self.audio_output.setVolume(volume / 100.0)
    
    def update_position(self, position):
        """更新播放位置"""
        if self.media_player and self.media_player.duration() > 0:
            # 更新进度条
            progress = int((position / self.media_player.duration()) * 100)
            self.progress_slider.setValue(progress)
            
            # 更新时间标签
            current_time = self.format_time(position)
            total_time = self.format_time(self.media_player.duration())
            self.time_label.setText(f"{current_time} / {total_time}")
    
    def update_duration(self, duration):
        """更新音频总时长"""
        if duration > 0:
            total_time = self.format_time(duration)
            self.time_label.setText(f"00:00 / {total_time}")
    
    def update_playback_state(self, state):
        """更新播放状态"""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
        elif state == QMediaPlayer.PlaybackState.PausedState:
            self.play_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
        elif state == QMediaPlayer.PlaybackState.StoppedState:
            self.play_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
    
    def on_player_error(self, error, error_string):
        """处理播放器错误"""
        self.status_label.setText(f"播放错误: {error_string}")
        print(f"媒体播放器错误: {error_string}")
    
    def format_time(self, ms: int) -> str:
        """格式化时间（毫秒转分:秒）"""
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def closeEvent(self, event):
        """关闭对话框事件"""
        if self.media_player:
            self.media_player.stop()
        event.accept()
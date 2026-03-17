"""TTS工作线程类"""
import os
import re
import asyncio
import tempfile
from typing import List, Dict, Optional, Tuple

import edge_tts
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from voice_settings import VoiceSettings
from audio_processor import AudioProcessor


class PreviewWorker(QThread):
    """试听工作线程（支持多角色）"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str, bool)
    error = pyqtSignal(str)
    
    def __init__(self, text: str, voice_settings: Dict[str, VoiceSettings], 
                 is_selection: bool = False, beep_file: Optional[str] = None):
        super().__init__()
        self.text = text
        self.voice_settings = voice_settings
        self.is_selection = is_selection
        self.beep_file = beep_file
        self._stop_flag = False
        self.audio_processor = AudioProcessor()
        self._temp_file = None
        
    def stop(self):
        self._stop_flag = True
    
    async def _generate_audio_segment(self, text: str, voice_settings: VoiceSettings, 
                                     index: int) -> Optional[Tuple[np.ndarray, int]]:
        """生成单个音频片段"""
        try:
            # 验证文本不为空
            if not text or not text.strip():
                self.error.emit(f"片段 {index} 的文本为空，跳过")
                return None
            
            # 清理文本，移除多余空格
            text = text.strip()
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                temp_file = tmp.name
            
            # 构建communicate对象
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice_settings.voice,
                rate=f'{voice_settings.rate:+d}%',
                volume=f'{voice_settings.volume:+d}%',
                pitch=f'{voice_settings.pitch:+d}Hz'
            )
            
            # 保存音频到临时文件
            await communicate.save(temp_file)
            
            # 加载音频
            audio_data, samplerate = self.audio_processor.load_audio(temp_file)
            
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass
            
            self.progress.emit(index, f"已生成片段 {index}")
            return audio_data, samplerate
            
        except Exception as e:
            self.error.emit(f"生成音频片段失败: {str(e)}")
            return None
    
    def run(self):
        try:
            self.progress.emit(0, "正在解析试听文本...")
            
            # 解析文本
            segments = self._parse_text(self.text)
            
            if not segments:
                self.error.emit("未找到有效文本")
                return
            
            self.progress.emit(10, f"共发现 {len(segments)} 个片段")
            
            # 生成所有音频片段
            audio_segments = []
            samplerate = 24000  # 默认采样率
            
            for i, (segment_type, content, role) in enumerate(segments):
                if self._stop_flag:
                    return
                    
                progress_value = 10 + int((i / len(segments)) * 80)
                
                if segment_type == 'text':
                    # 获取对应角色的语音设置
                    voice = self.voice_settings.get(role, self.voice_settings['A'])
                    self.progress.emit(progress_value, f"正在生成角色 {role} 的语音...")
                    
                    result = asyncio.run(self._generate_audio_segment(content, voice, i+1))
                    if result:
                        audio_data, sr = result
                        audio_segments.append((audio_data, sr))
                        samplerate = sr  # 使用第一个片段的采样率
                        
                elif segment_type == 'pause':
                    duration = int(content)  # 毫秒
                    silence = self.audio_processor.create_silence(duration, samplerate)
                    audio_segments.append((silence, samplerate))
                    self.progress.emit(progress_value, f"已添加停顿: {duration}ms")
                    
                elif segment_type == 'beep':
                    if self.beep_file and os.path.exists(self.beep_file):
                        try:
                            beep_data, sr = self.audio_processor.load_audio(self.beep_file)
                            audio_segments.append((beep_data, sr))
                        except:
                            beep_data = self.audio_processor.create_beep(samplerate=samplerate)
                            audio_segments.append((beep_data, samplerate))
                    else:
                        beep_data = self.audio_processor.create_beep(samplerate=samplerate)
                        audio_segments.append((beep_data, samplerate))
                    self.progress.emit(progress_value, "已添加蜂鸣声")
            
            # 合并所有音频片段
            if audio_segments:
                self.progress.emit(95, "正在合并音频片段...")
                combined_data, combined_sr = self.audio_processor.concatenate_audios(audio_segments)
                
                # 保存到临时文件
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                    temp_file = tmp.name
                    self._temp_file = temp_file
                
                self.audio_processor.save_audio(combined_data, combined_sr, temp_file)
                
                self.finished.emit(temp_file, True)
                self.progress.emit(100, "试听音频生成完成！")
            else:
                self.error.emit("没有生成任何音频")
                
        except Exception as e:
            self.error.emit(f"试听生成时出错: {str(e)}")
    
    def _parse_text(self, text: str) -> List[tuple]:
        """解析文本，分割成片段（支持角色切换）"""
        segments = []
        current_role = 'A'
        current_text = []
        
        # 使用正则表达式匹配标记
        pattern = r'(\[[ABCD]\])|(\[\d+\])|(\[R\])'
        parts = re.split(pattern, text)
        
        for part in parts:
            if not part:
                continue
                
            # 检查是否是标记
            if part.startswith('[') and part.endswith(']'):
                # 如果有累积的文本，先添加
                if current_text:
                    segments.append(('text', ''.join(current_text), current_role))
                    current_text = []
                
                # 处理标记
                if part in ['[A]', '[B]', '[C]', '[D]']:
                    current_role = part[1]
                elif part == '[R]':
                    segments.append(('beep', '', ''))
                else:  # 数字停顿
                    try:
                        duration = int(part[1:-1])
                        segments.append(('pause', str(duration), ''))
                    except ValueError:
                        pass
            else:
                current_text.append(part)
        
        # 添加最后一段文本
        if current_text:
            segments.append(('text', ''.join(current_text), current_role))
        
        return segments
    
    def cleanup(self):
        """清理临时文件"""
        if self._temp_file and os.path.exists(self._temp_file):
            try:
                os.unlink(self._temp_file)
            except:
                pass


class TTSWorker(QThread):
    """TTS工作线程"""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str, bool)
    error = pyqtSignal(str)
    
    def __init__(self, text: str, voice_settings: Dict[str, VoiceSettings], 
                 output_path: str, beep_file: Optional[str] = None):
        super().__init__()
        self.text = text
        self.voice_settings = voice_settings
        self.output_path = output_path
        self.beep_file = beep_file
        self._stop_flag = False
        self.audio_processor = AudioProcessor()
        
    def stop(self):
        self._stop_flag = True
    
    async def _generate_audio_segment(self, text: str, voice_settings: VoiceSettings, 
                                     index: int) -> Optional[Tuple[np.ndarray, int]]:
        """生成单个音频片段"""
        try:
            # 验证文本不为空
            if not text or not text.strip():
                self.error.emit(f"片段 {index} 的文本为空，跳过")
                return None
            
            # 清理文本，移除多余空格
            text = text.strip()
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
                temp_file = tmp.name
            
            # 构建communicate对象
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice_settings.voice,
                rate=f'{voice_settings.rate:+d}%',
                volume=f'{voice_settings.volume:+d}%',
                pitch=f'{voice_settings.pitch:+d}Hz'
            )
            
            # 保存音频到临时文件
            await communicate.save(temp_file)
            
            # 加载音频
            audio_data, samplerate = self.audio_processor.load_audio(temp_file)
            
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass
            
            self.progress.emit(index, f"已生成片段 {index}")
            return audio_data, samplerate
            
        except Exception as e:
            self.error.emit(f"生成音频片段失败: {str(e)}")
            return None
    
    def run(self):
        try:
            # 解析文本
            segments = self._parse_text(self.text)
            
            if not segments:
                self.error.emit("未找到有效文本")
                return
            
            # 生成所有音频片段
            audio_segments = []
            samplerate = 24000  # 默认采样率
            
            for i, (segment_type, content, role) in enumerate(segments):
                if self._stop_flag:
                    return
                    
                if segment_type == 'text':
                    voice = self.voice_settings.get(role, self.voice_settings['A'])
                    result = asyncio.run(self._generate_audio_segment(content, voice, i+1))
                    if result:
                        audio_data, sr = result
                        audio_segments.append((audio_data, sr))
                        samplerate = sr  # 使用第一个片段的采样率
                        
                elif segment_type == 'pause':
                    duration = int(content)  # 毫秒
                    silence = self.audio_processor.create_silence(duration, samplerate)
                    audio_segments.append((silence, samplerate))
                    self.progress.emit(i+1, f"已添加停顿: {duration}ms")
                    
                elif segment_type == 'beep':
                    if self.beep_file and os.path.exists(self.beep_file):
                        try:
                            beep_data, sr = self.audio_processor.load_audio(self.beep_file)
                            audio_segments.append((beep_data, sr))
                        except:
                            beep_data = self.audio_processor.create_beep(samplerate=samplerate)
                            audio_segments.append((beep_data, samplerate))
                    else:
                        beep_data = self.audio_processor.create_beep(samplerate=samplerate)
                        audio_segments.append((beep_data, samplerate))
                    self.progress.emit(i+1, "已添加蜂鸣声")
            
            # 合并所有音频片段
            if audio_segments:
                combined_data, combined_sr = self.audio_processor.concatenate_audios(audio_segments)
                
                # 保存最终文件
                self.audio_processor.save_audio(combined_data, combined_sr, self.output_path)
                
                self.finished.emit(self.output_path, True)
                self.progress.emit(100, "音频生成完成！")
            else:
                self.error.emit("没有生成任何音频")
                
        except Exception as e:
            self.error.emit(f"生成音频时出错: {str(e)}")
    
    def _parse_text(self, text: str) -> List[tuple]:
        """解析文本，分割成片段"""
        segments = []
        current_role = 'A'
        current_text = []
        
        # 使用正则表达式匹配标记
        pattern = r'(\[[ABCD]\])|(\[\d+\])|(\[R\])'
        parts = re.split(pattern, text)
        
        for part in parts:
            if not part:
                continue
                
            # 检查是否是标记
            if part.startswith('[') and part.endswith(']'):
                # 如果有累积的文本，先添加
                if current_text:
                    segments.append(('text', ''.join(current_text), current_role))
                    current_text = []
                
                # 处理标记
                if part in ['[A]', '[B]', '[C]', '[D]']:
                    current_role = part[1]
                elif part == '[R]':
                    segments.append(('beep', '', ''))
                else:  # 数字停顿
                    try:
                        duration = int(part[1:-1])
                        segments.append(('pause', str(duration), ''))
                    except ValueError:
                        pass
            else:
                current_text.append(part)
        
        # 添加最后一段文本
        if current_text:
            segments.append(('text', ''.join(current_text), current_role))
        
        return segments

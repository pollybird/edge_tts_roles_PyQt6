import numpy as np
import soundfile as sf
from scipy import signal
from pathlib import Path
from typing import List, Tuple, Optional


class AudioProcessor:
    
    @staticmethod
    def load_audio(file_path: str) -> Tuple[np.ndarray, int]:
        """加载音频文件"""
        try:
            data, samplerate = sf.read(file_path)
            # 确保是二维数组（立体声）
            if len(data.shape) == 1:
                data = np.column_stack((data, data))
            return data, samplerate
        except Exception as e:
            print(f"加载音频文件失败 {file_path}: {e}")
            # 返回空的音频数据
            return np.zeros((1000, 2), dtype=np.float32), 24000
    
    @staticmethod
    def save_audio(data: np.ndarray, samplerate: int, file_path: str):
        """保存音频文件"""
        try:
            # 确定格式
            format_map = {
                '.wav': 'WAV',
                '.mp3': 'MP3',
                '.ogg': 'OGG',
                '.flac': 'FLAC'
            }
            
            ext = Path(file_path).suffix.lower()
            file_format = format_map.get(ext, 'WAV')
            
            sf.write(file_path, data, samplerate, format=file_format)
        except Exception as e:
            print(f"保存音频文件失败 {file_path}: {e}")
            raise
    
    @staticmethod
    def create_silence(duration_ms: int, samplerate: int = 24000) -> np.ndarray:
        """创建静音片段"""
        duration_samples = int(samplerate * duration_ms / 1000)
        return np.zeros((duration_samples, 2), dtype=np.float32)
    
    @staticmethod
    def create_beep(duration_ms: int = 500, frequency: int = 1000, 
                    samplerate: int = 24000) -> np.ndarray:
        """创建蜂鸣声"""
        try:
            duration_samples = int(samplerate * duration_ms / 1000)
            t = np.linspace(0, duration_ms / 1000, duration_samples, endpoint=False)
            
            # 生成正弦波
            beep_wave = 0.3 * np.sin(2 * np.pi * frequency * t)
            
            # 添加淡入淡出
            fade_samples = int(0.05 * samplerate)  # 50ms淡入淡出
            if fade_samples * 2 > duration_samples:
                fade_samples = duration_samples // 4
                
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            
            if len(beep_wave) > 2 * fade_samples:
                beep_wave[:fade_samples] *= fade_in
                beep_wave[-fade_samples:] *= fade_out
            
            # 转换为立体声
            beep_stereo = np.column_stack((beep_wave, beep_wave))
            return beep_stereo.astype(np.float32)
        except Exception as e:
            print(f"创建蜂鸣声失败: {e}")
            # 返回静音作为后备
            return AudioProcessor.create_silence(duration_ms, samplerate)
    
    @staticmethod
    def concatenate_audios(audio_segments: List[Tuple[np.ndarray, int]], 
                          crossfade_ms: int = 0) -> Tuple[np.ndarray, int]:
        """拼接多个音频片段"""
        if not audio_segments:
            raise ValueError("没有音频片段可拼接")
        
        # 获取采样率（假设所有音频采样率相同）
        samplerate = audio_segments[0][1]
        
        # 检查所有音频采样率是否相同
        for i, (_, sr) in enumerate(audio_segments):
            if sr != samplerate:
                print(f"警告: 音频片段 {i} 的采样率 {sr} 与第一个片段的采样率 {samplerate} 不匹配")
        
        # 拼接音频数据
        all_data = []
        for i, (data, _) in enumerate(audio_segments):
            # 确保是立体声
            if len(data.shape) == 1:
                data = np.column_stack((data, data))
            elif data.shape[1] > 2:
                # 如果通道数多于2，取前两个通道
                data = data[:, :2]
            elif data.shape[1] == 1:
                # 如果是单声道，转换为立体声
                data = np.column_stack((data[:, 0], data[:, 0]))
            
            all_data.append(data)
        
        # 应用交叉淡化
        if crossfade_ms > 0 and len(audio_segments) > 1:
            crossfade_samples = int(samplerate * crossfade_ms / 1000)
            result = all_data[0]
            
            for next_data in all_data[1:]:
                if len(result) >= crossfade_samples and len(next_data) >= crossfade_samples:
                    # 交叉淡化
                    fade_out = np.linspace(1, 0, crossfade_samples)
                    fade_in = np.linspace(0, 1, crossfade_samples)
                    
                    result_end = result[-crossfade_samples:] * fade_out[:, np.newaxis]
                    next_start = next_data[:crossfade_samples] * fade_in[:, np.newaxis]
                    
                    # 拼接
                    result = np.vstack([
                        result[:-crossfade_samples],
                        result_end + next_start,
                        next_data[crossfade_samples:]
                    ])
                else:
                    result = np.vstack([result, next_data])
            
            return result, samplerate
        else:
            return np.vstack(all_data), samplerate
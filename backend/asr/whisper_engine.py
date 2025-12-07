import whisper
import numpy as np
from loguru import logger
import config
import torch

class WhisperASR:
    """Whisper-based speech recognition engine"""
    
    def __init__(self):
        logger.info(f"Loading Whisper model: {config.WHISPER_MODEL}")
        self.model = whisper.load_model(
            config.WHISPER_MODEL,
            device=config.WHISPER_DEVICE
        )
        logger.info("Whisper model loaded successfully")
    
    def transcribe(self, audio_data):
        """
        Transcribe audio data (numpy array)
        
        Args:
            audio_data: numpy array of audio samples
            
        Returns:
            str: Transcribed text
        """
        try:
            # Ensure audio is float32
            if audio_data.dtype != np.float32:
                audio_data = audio_data.astype(np.float32)
            
            # Normalize audio
            audio_data = audio_data / np.max(np.abs(audio_data))
            
            # Transcribe
            result = self.model.transcribe(
                audio_data,
                language=config.WHISPER_LANGUAGE,
                fp16=False if config.WHISPER_DEVICE == "cpu" else True
            )
            
            text = result["text"].strip()
            logger.debug(f"Transcribed: {text}")
            
            return text
            
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    def transcribe_file(self, audio_file):
        """
        Transcribe audio from file
        
        Args:
            audio_file: Path to audio file
            
        Returns:
            str: Transcribed text
        """
        try:
            result = self.model.transcribe(
                audio_file,
                language=config.WHISPER_LANGUAGE,
                fp16=False if config.WHISPER_DEVICE == "cpu" else True
            )
            
            text = result["text"].strip()
            logger.info(f"Transcribed from file: {text}")
            
            return text
            
        except Exception as e:
            logger.error(f"File transcription error: {e}")
            return ""
    
    def detect_language(self, audio_data):
        """Detect language from audio"""
        try:
            # Load audio
            audio = whisper.pad_or_trim(audio_data)
            
            # Make log-Mel spectrogram
            mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
            
            # Detect language
            _, probs = self.model.detect_language(mel)
            detected_lang = max(probs, key=probs.get)
            
            logger.info(f"Detected language: {detected_lang} (confidence: {probs[detected_lang]:.2f})")
            
            return detected_lang
            
        except Exception as e:
            logger.error(f"Language detection error: {e}")
            return config.WHISPER_LANGUAGE

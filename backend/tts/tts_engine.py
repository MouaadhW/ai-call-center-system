import subprocess
import os
from loguru import logger
import config
from pathlib import Path
import hashlib
import numpy as np

class PiperTTS:
    """Piper-based text-to-speech engine"""
    
    def __init__(self):
        self.cache_dir = config.DATA_DIR / "tts_cache"
        self.cache_dir.mkdir(exist_ok=True)
        logger.info("Piper TTS engine initialized")
    
    def synthesize(self, text):
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            
        Returns:
            numpy array: Audio data
        """
        try:
            # For now, use a simple implementation
            # In production, integrate actual Piper TTS
            audio_file = self.synthesize_to_file(text)
            
            # Load and return audio data
            import soundfile as sf
            audio_data, sample_rate = sf.read(audio_file)
            
            return audio_data
            
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            return None
    
    def synthesize_to_file(self, text):
        """
        Synthesize speech and save to file
        
        Args:
            text: Text to synthesize
            
        Returns:
            str: Path to audio file
        """
        try:
            # Create cache key from text
            cache_key = hashlib.md5(text.encode()).hexdigest()
            audio_file = self.cache_dir / f"{cache_key}.wav"
            
            # Return cached file if exists
            if audio_file.exists():
                logger.debug(f"Using cached TTS: {text[:50]}...")
                return str(audio_file)
            
            # Use espeak as fallback (available on most systems)
            # In production, replace with actual Piper TTS
            cmd = [
                "espeak",
                "-v", "en-us",
                "-s", "150",  # Speed
                "-w", str(audio_file),
                text
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            logger.info(f"Generated TTS audio: {text[:50]}...")
            return str(audio_file)
            
        except subprocess.CalledProcessError as e:
            logger.error(f"TTS command failed: {e}")
            # Create silent audio as fallback
            return self.create_silent_audio()
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return self.create_silent_audio()
    
    def create_silent_audio(self):
        """Create a silent audio file as fallback"""
        try:
            import soundfile as sf
            
            silent_file = self.cache_dir / "silent.wav"
            
            if not silent_file.exists():
                # Create 1 second of silence
                silence = np.zeros(config.SAMPLE_RATE, dtype=np.float32)
                sf.write(str(silent_file), silence, config.SAMPLE_RATE)
            
            return str(silent_file)
            
        except Exception as e:
            logger.error(f"Error creating silent audio: {e}")
            return ""
    
    def set_voice(self, voice_name):
        """Set TTS voice (for future Piper integration)"""
        logger.info(f"Voice setting requested: {voice_name}")
        # TODO: Implement when integrating actual Piper TTS
        pass
    
    def set_speed(self, speed):
        """Set TTS speed (for future Piper integration)"""
        logger.info(f"Speed setting requested: {speed}")
        # TODO: Implement when integrating actual Piper TTS
        pass

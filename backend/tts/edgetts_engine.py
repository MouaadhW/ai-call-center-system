import edge_tts
import asyncio
import os
from pathlib import Path
import hashlib
from loguru import logger

class EdgeTTSEngine:
    """
    Edge-TTS engine for human-like voice synthesis
    FREE and sounds very natural!
    """
    
    def __init__(self):
        self.cache_dir = Path("data/tts_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Best voices for natural conversation
        self.voices = {
            'female': 'en-US-AriaNeural',      # Natural, friendly female
            'male': 'en-US-GuyNeural',         # Natural, professional male
            'female_alt': 'en-US-JennyNeural', # Warm, conversational
            'male_alt': 'en-GB-RyanNeural'     # British, clear
        }
        
        self.current_voice = self.voices['female']
        logger.info(f"Edge-TTS initialized with voice: {self.current_voice}")
    
    async def synthesize_async(self, text, voice=None):
        """
        Synthesize speech asynchronously
        
        Args:
            text: Text to synthesize
            voice: Voice to use (optional)
            
        Returns:
            Path to audio file
        """
        try:
            # Use cache
            cache_key = hashlib.md5(f"{text}{voice or self.current_voice}".encode()).hexdigest()
            audio_file = self.cache_dir / f"{cache_key}.mp3"
            
            if audio_file.exists():
                logger.debug(f"Using cached TTS: {text[:50]}...")
                return str(audio_file)
            
            # Generate speech
            voice_to_use = voice or self.current_voice
            communicate = edge_tts.Communicate(text, voice_to_use)
            await communicate.save(str(audio_file))
            
            logger.info(f"Generated TTS: {text[:50]}...")
            return str(audio_file)
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None
    
    def synthesize(self, text, voice=None):
        """
        Synchronous wrapper for synthesize_async
        """
        return asyncio.run(self.synthesize_async(text, voice))
    
    def set_voice(self, voice_type='female'):
        """
        Change voice
        
        Args:
            voice_type: 'female', 'male', 'female_alt', 'male_alt'
        """
        if voice_type in self.voices:
            self.current_voice = self.voices[voice_type]
            logger.info(f"Voice changed to: {self.current_voice}")
        else:
            logger.warning(f"Unknown voice type: {voice_type}")
    
    def clear_cache(self):
        """Clear TTS cache"""
        try:
            import shutil
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info("TTS cache cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")


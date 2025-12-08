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
        # Use absolute path to avoid issues
        base_dir = Path(__file__).parent.parent
        self.cache_dir = base_dir / "data" / "tts_cache"
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
        logger.info(f"TTS cache directory: {self.cache_dir}")
    
    async def synthesize_async(self, text, voice=None, rate="+15%"):
        """
        Synthesize speech asynchronously
        
        Args:
            text: Text to synthesize
            voice: Voice to use (optional)
            rate: Speech rate (default "+15%" for faster speech)
                  Can be: "+X%" (faster), "-X%" (slower), or "X%" (absolute)
            
        Returns:
            Path to audio file (absolute path)
        """
        try:
            if not text or len(text.strip()) == 0:
                logger.warning("Empty text provided to TTS")
                return None
            
            # Clean text (remove special characters that might cause issues)
            text = text.strip()
            
            # Use cache with rate included
            cache_key = hashlib.md5(f"{text}{voice or self.current_voice}{rate}".encode()).hexdigest()
            audio_file = self.cache_dir / f"{cache_key}.mp3"
            
            if audio_file.exists() and audio_file.stat().st_size > 0:
                logger.debug(f"Using cached TTS: {text[:50]}...")
                return str(audio_file.absolute())
            
            # Generate speech with retry logic and rate control
            voice_to_use = voice or self.current_voice
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    # Use SSML to control speech rate for faster speech
                    ssml_text = f'<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US"><prosody rate="{rate}">{text}</prosody></speak>'
                    communicate = edge_tts.Communicate(ssml_text, voice_to_use)
                    await communicate.save(str(audio_file))
                    
                    # Verify file was created and has content
                    if audio_file.exists() and audio_file.stat().st_size > 0:
                        logger.info(f"Generated TTS: {text[:50]}... ({audio_file.stat().st_size} bytes)")
                        return str(audio_file.absolute())
                    else:
                        logger.warning(f"TTS file created but empty, attempt {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(0.5)
                            continue
                        
                except Exception as e:
                    logger.warning(f"TTS generation attempt {attempt + 1} failed: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                    else:
                        raise
            
            logger.error("TTS generation failed after all retries")
            return None
            
        except Exception as e:
            logger.error(f"TTS error: {e}", exc_info=True)
            return None
    
    def synthesize(self, text, voice=None, rate="+15%"):
        """
        Synchronous wrapper for synthesize_async
        """
        return asyncio.run(self.synthesize_async(text, voice, rate))
    
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


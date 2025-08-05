#!/usr/bin/env python3
"""
Test script for Audio Transcription Service
"""

import asyncio
import os
from dotenv import load_dotenv
from app.services.audio_transcription_service import AudioTranscriptionService

# Load environment variables
load_dotenv()

async def test_audio_transcription():
    """Test the audio transcription service"""
    print("🧪 Testing Audio Transcription Service...")
    
    # Initialize service
    service = AudioTranscriptionService()
    
    # Check availability
    print(f"✅ Service available: {service.is_available()}")
    print(f"📋 Supported formats: {service.get_supported_formats()}")
    
    if not service.is_available():
        print("❌ Service not available - check HUGGINGFACE_API_TOKEN environment variable")
        return
    
    # Test with a sample audio file (if available)
    test_file = "test_audio.mp3"
    if os.path.exists(test_file):
        print(f"🎵 Testing with file: {test_file}")
        try:
            result = await service.transcribe_audio_file(test_file)
            print(f"✅ Transcription successful:")
            print(f"   Text: {result['transcription']}")
            print(f"   Language: {result['language']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Duration: {result['duration']:.2f}s")
            print(f"   Sample Rate: {result['sample_rate']}Hz")
        except Exception as e:
            print(f"❌ Transcription failed: {e}")
    else:
        print("ℹ️ No test audio file found. Create a test_audio.wav file to test transcription.")

if __name__ == "__main__":
    asyncio.run(test_audio_transcription()) 
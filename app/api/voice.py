"""
Voice API endpoints for Krishi Sahayak AI
Provides real-time voice communication with the AI assistant
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse
import logging
import json
import asyncio
import base64
import io
from typing import Optional
import wave
import numpy as np

from app.services.agentic_core import get_response
from app.models.api_models import ChatRequest
from app.services import language_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Store active voice sessions
active_sessions = {}


class VoiceSession:
    """Manages a voice conversation session"""
    
    def __init__(self, websocket: WebSocket, session_id: str):
        self.websocket = websocket
        self.session_id = session_id
        self.language = "hi"  # Default to Hindi for Indian farmers
        self.is_speaking = False
        self.audio_buffer = []
        
    async def send_message(self, message_type: str, data: dict):
        """Send a message to the client"""
        try:
            await self.websocket.send_text(json.dumps({
                "type": message_type,
                "data": data,
                "session_id": self.session_id
            }))
        except Exception as e:
            logger.error(f"Error sending message: {e}")


@router.websocket("/voice/call")
async def voice_call_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice communication
    
    Expected message format:
    {
        "type": "audio_chunk" | "start_session" | "end_session" | "text_message",
        "data": {
            "audio": base64_encoded_audio (for audio_chunk),
            "language": "hi|en|bn|ta|etc" (for start_session),
            "message": "text message" (for text_message)
        },
        "session_id": "unique_session_id"
    }
    """
    await websocket.accept()
    session = None
    
    try:
        # Wait for session initialization
        init_message = await websocket.receive_text()
        init_data = json.loads(init_message)
        
        if init_data.get("type") != "start_session":
            await websocket.close(code=4000, reason="Session must be initialized first")
            return
            
        session_id = init_data.get("session_id", f"voice_session_{id(websocket)}")
        language = init_data.get("data", {}).get("language", "hi")
        
        # Create session
        session = VoiceSession(websocket, session_id)
        session.language = language
        active_sessions[session_id] = session
        
        # Send session started confirmation
        await session.send_message("session_started", {
            "session_id": session_id,
            "language": language,
            "status": "ready"
        })
        
        logger.info(f"Voice session started: {session_id} (Language: {language})")
        
        # Main message loop
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                message_type = data.get("type")
                
                if message_type == "audio_chunk":
                    await handle_audio_chunk(session, data.get("data", {}))
                    
                elif message_type == "text_message":
                    await handle_text_message(session, data.get("data", {}))
                    
                elif message_type == "end_session":
                    await handle_end_session(session)
                    break
                    
                elif message_type == "ping":
                    await session.send_message("pong", {"timestamp": data.get("data", {}).get("timestamp")})
                    
                else:
                    logger.warning(f"Unknown message type: {message_type}")
                    
            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await session.send_message("error", {"message": "Invalid JSON format"})
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await session.send_message("error", {"message": str(e)})
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if session:
            await session.send_message("error", {"message": "Server error occurred"})
    finally:
        # Cleanup
        if session and session.session_id in active_sessions:
            del active_sessions[session.session_id]
            logger.info(f"Voice session ended: {session.session_id}")


async def handle_audio_chunk(session: VoiceSession, data: dict):
    """Handle incoming audio chunk"""
    try:
        audio_data = data.get("audio")
        if not audio_data:
            return
            
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_data)
        session.audio_buffer.append(audio_bytes)
        
        # Check if this is the end of speech
        is_final = data.get("is_final", False)
        
        if is_final and session.audio_buffer:
            # Process the complete audio
            complete_audio = b''.join(session.audio_buffer)
            session.audio_buffer.clear()
            
            # Convert speech to text (placeholder - you'll need to implement actual STT)
            text = await speech_to_text(complete_audio, session.language)
            
            if text:
                # Send transcription to client
                await session.send_message("transcription", {
                    "text": text,
                    "language": session.language
                })
                
                # Get AI response
                await process_voice_query(session, text)
            
    except Exception as e:
        logger.error(f"Error handling audio chunk: {e}")
        await session.send_message("error", {"message": "Audio processing error"})


async def handle_text_message(session: VoiceSession, data: dict):
    """Handle text message (for testing or text fallback)"""
    try:
        message = data.get("message", "")
        if message:
            await process_voice_query(session, message)
    except Exception as e:
        logger.error(f"Error handling text message: {e}")
        await session.send_message("error", {"message": "Text processing error"})


async def handle_end_session(session: VoiceSession):
    """Handle session termination"""
    await session.send_message("session_ended", {
        "session_id": session.session_id,
        "status": "terminated"
    })


async def process_voice_query(session: VoiceSession, user_message: str):
    """Process user query and send AI response"""
    try:
        from app.main import krishi_agent
        
        if krishi_agent is None:
            await session.send_message("error", {"message": "AI agent not available"})
            return
            
        # Send processing status
        await session.send_message("processing", {
            "message": "AI is thinking...",
            "user_query": user_message
        })
        
        # Get AI response
        ai_response = get_response(
            krishi_agent,
            user_message,
            language_code=session.language
        )
        
        # Send text response
        await session.send_message("ai_response", {
            "text": ai_response,
            "language": session.language
        })
        
        # Convert to speech and send audio
        audio_data = await text_to_speech(ai_response, session.language)
        if audio_data:
            # Send audio in chunks
            await send_audio_stream(session, audio_data)
            
    except Exception as e:
        logger.error(f"Error processing voice query: {e}")
        error_message = language_service.get_template(session.language, "error")
        await session.send_message("ai_response", {
            "text": error_message,
            "language": session.language
        })


async def send_audio_stream(session: VoiceSession, audio_data: bytes):
    """Send audio data in chunks"""
    try:
        # Send audio start signal
        await session.send_message("audio_start", {
            "total_size": len(audio_data),
            "format": "wav"
        })
        
        # Send audio in chunks
        chunk_size = 4096
        for i in range(0, len(audio_data), chunk_size):
            chunk = audio_data[i:i + chunk_size]
            encoded_chunk = base64.b64encode(chunk).decode('utf-8')
            
            await session.send_message("audio_chunk", {
                "audio": encoded_chunk,
                "chunk_index": i // chunk_size,
                "is_final": i + chunk_size >= len(audio_data)
            })
            
            # Small delay to avoid overwhelming the client
            await asyncio.sleep(0.01)
            
        # Send audio end signal
        await session.send_message("audio_end", {
            "status": "complete"
        })
        
    except Exception as e:
        logger.error(f"Error sending audio stream: {e}")
        await session.send_message("error", {"message": "Audio streaming error"})


async def speech_to_text(audio_data: bytes, language: str) -> Optional[str]:
    """
    Convert speech to text
    This is a placeholder - you'll need to implement actual STT
    using services like Google Speech-to-Text, Azure Speech, or OpenAI Whisper
    """
    try:
        # Placeholder implementation
        # In a real implementation, you would:
        # 1. Send audio_data to a speech recognition service
        # 2. Handle different audio formats
        # 3. Return the transcribed text
        
        logger.info(f"Processing speech-to-text for {len(audio_data)} bytes (Language: {language})")
        
        # For now, return a placeholder
        return "आपका ऑडियो संदेश प्राप्त हुआ है।" if language == "hi" else "Your audio message was received."
        
    except Exception as e:
        logger.error(f"Speech-to-text error: {e}")
        return None


async def text_to_speech(text: str, language: str) -> Optional[bytes]:
    """
    Convert text to speech
    This is a placeholder - you'll need to implement actual TTS
    using services like Google Text-to-Speech, Azure Speech, or ElevenLabs
    """
    try:
        # Placeholder implementation
        # In a real implementation, you would:
        # 1. Send text to a TTS service
        # 2. Specify voice, language, and other parameters
        # 3. Return the audio data as bytes
        
        logger.info(f"Processing text-to-speech: '{text[:50]}...' (Language: {language})")
        
        # For now, generate a simple tone sequence to represent speech
        # This creates a valid WAV file that browsers can play
        import numpy as np
        
        sample_rate = 16000
        duration = min(len(text) * 0.08, 8.0)  # Max 8 seconds, roughly 0.08s per character
        duration = max(duration, 1.0)  # Minimum 1 second
        
        # Generate a simple tone pattern that sounds like speech
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Create a varying tone to simulate speech patterns
        # Use multiple frequencies to make it sound more speech-like
        frequency_base = 200 if language == "hi" else 180  # Slightly different for different languages
        
        # Create speech-like pattern with multiple harmonics
        audio_wave = np.zeros_like(t)
        for i, char in enumerate(text[:20]):  # Use first 20 chars to vary the pattern
            freq = frequency_base + (ord(char) % 100)  # Vary frequency based on character
            phase_offset = i * 0.5
            char_wave = 0.3 * np.sin(2 * np.pi * freq * t + phase_offset)
            
            # Add harmonics for richer sound
            char_wave += 0.1 * np.sin(2 * np.pi * freq * 2 * t + phase_offset)
            char_wave += 0.05 * np.sin(2 * np.pi * freq * 3 * t + phase_offset)
            
            # Apply envelope to make it sound more natural
            envelope = np.exp(-2 * t) * (1 + 0.3 * np.sin(10 * t))
            char_wave *= envelope
            
            audio_wave += char_wave / len(text[:20])
        
        # Apply overall envelope to make it sound more like speech
        overall_envelope = np.concatenate([
            np.linspace(0, 1, int(sample_rate * 0.1)),  # Fade in
            np.ones(max(1, int(sample_rate * (duration - 0.2)))),  # Sustain
            np.linspace(1, 0, int(sample_rate * 0.1))   # Fade out
        ])
        
        # Ensure lengths match
        min_len = min(len(audio_wave), len(overall_envelope))
        audio_wave = audio_wave[:min_len] * overall_envelope[:min_len]
        
        # Convert to 16-bit PCM
        wave_int16 = (audio_wave * 32767).astype(np.int16)
        
        # Create WAV file
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(wave_int16.tobytes())
        
        logger.info(f"Generated {len(wav_buffer.getvalue())} bytes of audio for text: '{text[:30]}...'")
        return wav_buffer.getvalue()
        
    except Exception as e:
        logger.error(f"Text-to-speech error: {e}")
        # Fallback: create a simple beep
        try:
            sample_rate = 16000
            duration = 1.0
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            beep = 0.3 * np.sin(2 * np.pi * 440 * t)  # 440 Hz tone
            beep_int16 = (beep * 32767).astype(np.int16)
            
            wav_buffer = io.BytesIO()
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(beep_int16.tobytes())
            
            return wav_buffer.getvalue()
        except:
            return None


@router.get("/voice/status")
async def voice_status():
    """Get the status of voice functionality"""
    return {
        "status": "enabled",
        "active_sessions": len(active_sessions),
        "supported_languages": ["hi", "en", "bn", "ta", "te", "ml", "kn", "gu", "pa", "mr"],
        "features": {
            "speech_to_text": "placeholder_implemented",
            "text_to_speech": "placeholder_implemented", 
            "real_time_streaming": True,
            "websocket_support": True
        },
        "endpoints": {
            "websocket": "/api/voice/call",
            "status": "/api/voice/status"
        }
    }


@router.post("/voice/test")
async def test_voice_pipeline(request: dict):
    """Test the voice pipeline with text input"""
    try:
        text = request.get("text", "")
        language = request.get("language", "hi")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Process through the voice pipeline
        from app.main import krishi_agent
        
        if krishi_agent is None:
            raise HTTPException(status_code=500, detail="AI agent not initialized")
        
        # Get AI response
        ai_response = get_response(krishi_agent, text, language_code=language)
        
        # Convert to speech (placeholder)
        audio_data = await text_to_speech(ai_response, language)
        
        return {
            "input_text": text,
            "ai_response": ai_response,
            "language": language,
            "audio_generated": audio_data is not None,
            "audio_size": len(audio_data) if audio_data else 0
        }
        
    except Exception as e:
        logger.error(f"Voice test error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

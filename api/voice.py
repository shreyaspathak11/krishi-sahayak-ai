"""
Real-time Voice Conversation API for Krishi Sahayak AI
Provides phone call-like experience with streaming audio
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import asyncio
import json
import logging
import tempfile
import os
import io
import base64
from typing import AsyncGenerator, Dict, Any
import uuid
from datetime import datetime

# Voice processing imports
import speech_recognition as sr
from gtts import gTTS
import pygame
from pydub import AudioSegment
import numpy as np
import pyaudio
import wave
import threading
import queue

from app.services.agentic_core import get_response
from app.models.api_models import ChatRequest, ChatResponse
from app.services import language_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Voice call session management
active_voice_sessions: Dict[str, Dict[str, Any]] = {}

# Audio configuration
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
SILENCE_THRESHOLD = 500
SILENCE_DURATION = 1.5  # seconds

class VoiceCallSession:
    """Manages a real-time voice conversation session"""
    
    def __init__(self, session_id: str, websocket: WebSocket, language: str = "hi"):
        self.session_id = session_id
        self.websocket = websocket
        self.language = language
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = 1
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        
        self.is_active = True
        self.audio_queue = queue.Queue()
        self.response_queue = queue.Queue()
        self.is_speaking = False
        self.conversation_history = []
        
    async def start_conversation(self):
        """Start the voice conversation loop"""
        try:
            # Send initial greeting
            greeting = "नमस्ते! मैं कृषि सहायक हूँ। आप अपनी खेती की समस्या बता सकते हैं।" if self.language == "hi" else "Hello! I'm Krishi Sahayak. How can I help you with farming today?"
            
            await self.send_ai_response(greeting)
            
            # Start listening for audio
            await self.listen_and_respond()
            
        except Exception as e:
            logger.error(f"Voice conversation error: {e}")
            await self.send_error("Voice conversation failed")
    
    async def listen_and_respond(self):
        """Main conversation loop"""
        while self.is_active:
            try:
                # Wait for audio data from client
                message = await asyncio.wait_for(
                    self.websocket.receive_text(),
                    timeout=30.0
                )
                
                data = json.loads(message)
                
                if data.get("type") == "audio_chunk":
                    await self.process_audio_chunk(data.get("audio"))
                elif data.get("type") == "end_speech":
                    await self.process_complete_speech()
                elif data.get("type") == "ping":
                    await self.websocket.send_text(json.dumps({"type": "pong"}))
                elif data.get("type") == "end_call":
                    break
                    
            except asyncio.TimeoutError:
                await self.send_message("timeout", "No audio received")
                break
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Listen loop error: {e}")
                await self.send_error(str(e))
                break
    
    async def process_audio_chunk(self, audio_data: str):
        """Process incoming audio chunk"""
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_data)
            self.audio_queue.put(audio_bytes)
            
            # Send acknowledgment
            await self.send_message("audio_received", "Processing...")
            
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            await self.send_error("Failed to process audio")
    
    async def process_complete_speech(self):
        """Process complete speech and generate response"""
        try:
            # Combine all audio chunks
            audio_data = b""
            while not self.audio_queue.empty():
                audio_data += self.audio_queue.get()
            
            if len(audio_data) < 1000:  # Too short
                await self.send_message("speech_too_short", "Please speak longer")
                return
            
            # Save to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                # Convert raw audio to WAV
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(CHANNELS)
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(RATE)
                    wav_file.writeframes(audio_data)
                
                temp_file.flush()
                
                # Transcribe speech
                user_text = await self.transcribe_audio(temp_file.name)
                
                # Clean up
                os.unlink(temp_file.name)
            
            if user_text:
                # Add to conversation history
                self.conversation_history.append({
                    "role": "user",
                    "content": user_text,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Send transcription to client
                await self.send_message("transcription", user_text)
                
                # Generate AI response
                await self.generate_and_send_response(user_text)
            else:
                await self.send_message("no_speech", "Could not understand speech")
                
        except Exception as e:
            logger.error(f"Speech processing error: {e}")
            await self.send_error("Failed to process speech")
    
    async def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio file to text"""
        try:
            with sr.AudioFile(audio_file_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
                
                # Recognize speech
                lang_code = 'hi-IN' if self.language == 'hi' else 'en-US'
                text = self.recognizer.recognize_google(
                    audio, 
                    language=lang_code,
                    show_all=False
                )
                
                return text.strip()
                
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return ""
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
    
    async def generate_and_send_response(self, user_text: str):
        """Generate AI response and convert to speech"""
        try:
            # Get AI response
            from app.main import krishi_agent
            ai_response = get_response(
                krishi_agent, 
                user_text, 
                language_code=self.language
            )
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Send text response first
            await self.send_ai_response(ai_response)
            
            # Convert to speech and send audio
            await self.text_to_speech_and_send(ai_response)
            
        except Exception as e:
            logger.error(f"Response generation error: {e}")
            await self.send_error("Failed to generate response")
    
    async def text_to_speech_and_send(self, text: str):
        """Convert text to speech and send audio"""
        try:
            # Generate TTS
            tts = gTTS(text=text, lang=self.language, slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Convert to base64 for WebSocket transmission
            audio_base64 = base64.b64encode(audio_buffer.read()).decode()
            
            await self.send_message("ai_audio", audio_base64)
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            await self.send_message("tts_error", "Could not generate speech")
    
    async def send_ai_response(self, text: str):
        """Send AI response as text"""
        await self.send_message("ai_response", text)
    
    async def send_message(self, msg_type: str, content: str):
        """Send message to client"""
        try:
            message = {
                "type": msg_type,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id
            }
            await self.websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Send message error: {e}")
    
    async def send_error(self, error_msg: str):
        """Send error message"""
        await self.send_message("error", error_msg)
    
    def stop(self):
        """Stop the voice session"""
        self.is_active = False


@router.websocket("/call")
async def voice_call_websocket(websocket: WebSocket, language: str = "hi"):
    """
    WebSocket endpoint for real-time voice conversation
    """
    await websocket.accept()
    
    session_id = str(uuid.uuid4())
    logger.info(f"Starting voice call session: {session_id}")
    
    try:
        # Create voice session
        session = VoiceCallSession(session_id, websocket, language)
        active_voice_sessions[session_id] = {
            "session": session,
            "start_time": datetime.now(),
            "language": language
        }
        
        # Start conversation
        await session.start_conversation()
        
    except WebSocketDisconnect:
        logger.info(f"Voice call session disconnected: {session_id}")
    except Exception as e:
        logger.error(f"Voice call session error: {e}")
    finally:
        # Cleanup
        if session_id in active_voice_sessions:
            active_voice_sessions[session_id]["session"].stop()
            del active_voice_sessions[session_id]
        logger.info(f"Voice call session ended: {session_id}")


@router.post("/upload")
async def process_voice_upload(audio_file: UploadFile = File(...), language: str = "hi"):
    """
    Process uploaded audio file and return transcribed text
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file.flush()
            
            # Convert to text using speech recognition
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_file.name) as source:
                audio_data = recognizer.record(source)
                lang_code = 'hi-IN' if language == 'hi' else 'en-US'
                text = recognizer.recognize_google(audio_data, language=lang_code)
                
        # Clean up temp file
        os.unlink(temp_file.name)
        
        return {"transcribed_text": text}
        
    except sr.UnknownValueError:
        raise HTTPException(status_code=400, detail="Could not understand audio")
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        raise HTTPException(status_code=500, detail="Voice processing failed")


@router.get("/sessions")
async def get_active_sessions():
    """Get list of active voice call sessions"""
    sessions = []
    for session_id, session_data in active_voice_sessions.items():
        sessions.append({
            "session_id": session_id,
            "start_time": session_data["start_time"].isoformat(),
            "language": session_data["language"],
            "duration_minutes": (datetime.now() - session_data["start_time"]).total_seconds() / 60
        })
    return {"active_sessions": sessions}

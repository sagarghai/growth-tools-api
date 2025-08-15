#!/usr/bin/env python3
"""
Enhanced WhatsApp Mockup Generator with realistic chat flow and sounds
"""

import os
import uuid
import subprocess
import tempfile
import logging
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from datetime import datetime
import math

logger = logging.getLogger(__name__)

class WhatsAppMockupGenerator:
    def __init__(self, messages, bot_name="Bot"):
        self.messages = messages
        self.bot_name = bot_name
        self.session_id = str(uuid.uuid4())[:8]
        
        # WhatsApp dimensions (iPhone style)
        self.width = 376
        self.height = 812
        self.fps = 30
        
        # Colors (WhatsApp dark theme)
        self.bg_color = (17, 27, 33)  # Dark background
        self.header_color = (42, 57, 66)  # Header bar
        self.user_bubble_color = (0, 95, 115)  # User message (teal)
        self.bot_bubble_color = (42, 57, 66)  # Bot message (dark gray)
        self.text_color = (255, 255, 255)
        self.time_color = (168, 168, 168)
        
        # Timing
        self.typing_duration = 2.0  # seconds of typing indicator
        self.message_display_duration = 3.0  # seconds to show message
        self.pause_between_messages = 0.5  # pause between messages
        
        # Load fonts
        try:
            self.header_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 18)
            self.message_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 16)
            self.time_font = ImageFont.truetype('/System/Library/Fonts/Arial.ttf', 12)
        except:
            self.header_font = ImageFont.load_default()
            self.message_font = ImageFont.load_default()
            self.time_font = ImageFont.load_default()
    
    def create_sound_effects(self, temp_dir):
        """Generate WhatsApp-style sound effects"""
        
        # Generate send sound (higher pitch beep)
        send_sound_path = os.path.join(temp_dir, 'send.wav')
        self._generate_beep(send_sound_path, frequency=800, duration=0.1)
        
        # Generate receive sound (lower pitch beep)
        receive_sound_path = os.path.join(temp_dir, 'receive.wav')
        self._generate_beep(receive_sound_path, frequency=600, duration=0.15)
        
        return send_sound_path, receive_sound_path
    
    def _generate_beep(self, output_path, frequency=800, duration=0.1, sample_rate=44100):
        """Generate a simple beep sound"""
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        # Generate sine wave
        wave = np.sin(frequency * 2 * np.pi * t)
        # Add envelope to avoid clicks
        envelope = np.exp(-t * 10)  # Exponential decay
        wave = wave * envelope
        # Convert to 16-bit integers
        wave = (wave * 32767).astype(np.int16)
        
        # Write WAV file manually (simple format)
        with open(output_path, 'wb') as f:
            # WAV header
            f.write(b'RIFF')
            f.write((36 + len(wave) * 2).to_bytes(4, 'little'))
            f.write(b'WAVE')
            f.write(b'fmt ')
            f.write((16).to_bytes(4, 'little'))
            f.write((1).to_bytes(2, 'little'))  # PCM
            f.write((1).to_bytes(2, 'little'))  # Mono
            f.write(sample_rate.to_bytes(4, 'little'))
            f.write((sample_rate * 2).to_bytes(4, 'little'))
            f.write((2).to_bytes(2, 'little'))
            f.write((16).to_bytes(2, 'little'))
            f.write(b'data')
            f.write((len(wave) * 2).to_bytes(4, 'little'))
            f.write(wave.tobytes())
    
    def wrap_text(self, text, max_width, font):
        """Wrap text to fit in bubble"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def draw_header(self, draw):
        """Draw WhatsApp header"""
        # Header background
        draw.rectangle([0, 0, self.width, 100], fill=self.header_color)
        
        # Profile circle (bot)
        circle_x, circle_y = 20, 50
        circle_radius = 20
        draw.ellipse([circle_x - circle_radius, circle_y - circle_radius,
                     circle_x + circle_radius, circle_y + circle_radius],
                    fill=(100, 100, 100))
        
        # Bot name
        draw.text((55, 45), self.bot_name, font=self.header_font, fill=self.text_color)
        
        # Online status
        draw.text((55, 65), "online", font=self.time_font, fill=(76, 175, 80))
        
        # Time (top right)
        current_time = datetime.now().strftime("%H:%M")
        time_bbox = self.time_font.getbbox(current_time)
        draw.text((self.width - (time_bbox[2] - time_bbox[0]) - 10, 20), 
                 current_time, font=self.time_font, fill=self.text_color)
    
    def draw_typing_indicator(self, draw, y_pos):
        """Draw typing indicator animation"""
        # Typing bubble
        bubble_x = 20
        bubble_width = 60
        bubble_height = 40
        
        # Bubble background
        draw.rounded_rectangle([bubble_x, y_pos, bubble_x + bubble_width, y_pos + bubble_height],
                             radius=15, fill=self.bot_bubble_color)
        
        # Animated dots
        dot_x = bubble_x + 15
        dot_y = y_pos + 20
        
        for i in range(3):
            x = dot_x + (i * 10)
            # Animate dots with sine wave
            opacity = int(127 + 127 * math.sin(i * 0.5))  # Simple animation effect
            dot_color = (opacity, opacity, opacity)
            draw.ellipse([x-2, dot_y-2, x+2, dot_y+2], fill=dot_color)
    
    def draw_message_bubble(self, draw, text, is_user, y_pos, show_time=True):
        """Draw a message bubble with text"""
        max_bubble_width = 250
        padding = 15
        
        # Wrap text
        lines = self.wrap_text(text, max_bubble_width - (padding * 2), self.message_font)
        
        # Calculate bubble dimensions
        line_height = 20
        bubble_height = len(lines) * line_height + (padding * 2)
        if show_time:
            bubble_height += 15  # Extra space for timestamp
        
        # Calculate bubble width based on longest line
        max_line_width = 0
        for line in lines:
            bbox = self.message_font.getbbox(line)
            line_width = bbox[2] - bbox[0]
            max_line_width = max(max_line_width, line_width)
        
        bubble_width = min(max_bubble_width, max_line_width + (padding * 2))
        
        # Position bubble
        if is_user:
            bubble_x = self.width - bubble_width - 20
            bubble_color = self.user_bubble_color
        else:
            bubble_x = 20
            bubble_color = self.bot_bubble_color
        
        # Draw bubble
        draw.rounded_rectangle([bubble_x, y_pos, bubble_x + bubble_width, y_pos + bubble_height],
                             radius=15, fill=bubble_color)
        
        # Draw text
        text_y = y_pos + padding
        for line in lines:
            draw.text((bubble_x + padding, text_y), line, 
                     font=self.message_font, fill=self.text_color)
            text_y += line_height
        
        # Draw timestamp
        if show_time:
            timestamp = datetime.now().strftime("%H:%M")
            time_bbox = self.time_font.getbbox(timestamp)
            time_x = bubble_x + bubble_width - (time_bbox[2] - time_bbox[0]) - 5
            time_y = y_pos + bubble_height - 15
            draw.text((time_x, time_y), timestamp, font=self.time_font, fill=self.time_color)
        
        return bubble_height
    
    def generate_frames(self, temp_dir):
        """Generate all video frames"""
        frames = []
        current_y = 120  # Start below header
        messages_shown = []
        
        for msg_idx, message in enumerate(self.messages):
            text = message.get('text', '')
            is_user = message.get('role', 'user') == 'user'
            
            # Phase 1: Show typing indicator (only for bot messages)
            if not is_user:
                typing_frames = int(self.typing_duration * self.fps)
                for frame in range(typing_frames):
                    img = Image.new('RGB', (self.width, self.height), self.bg_color)
                    draw = ImageDraw.Draw(img)
                    
                    # Draw header
                    self.draw_header(draw)
                    
                    # Draw previous messages
                    draw_y = 120
                    for prev_msg in messages_shown:
                        bubble_height = self.draw_message_bubble(
                            draw, prev_msg['text'], prev_msg['is_user'], draw_y
                        )
                        draw_y += bubble_height + 10
                    
                    # Draw typing indicator
                    self.draw_typing_indicator(draw, draw_y)
                    
                    frame_path = os.path.join(temp_dir, f'frame_{len(frames):06d}.png')
                    img.save(frame_path)
                    frames.append(frame_path)
            
            # Phase 2: Show the actual message
            message_frames = int(self.message_display_duration * self.fps)
            for frame in range(message_frames):
                img = Image.new('RGB', (self.width, self.height), self.bg_color)
                draw = ImageDraw.Draw(img)
                
                # Draw header
                self.draw_header(draw)
                
                # Draw all messages up to current one
                draw_y = 120
                for prev_msg in messages_shown:
                    bubble_height = self.draw_message_bubble(
                        draw, prev_msg['text'], prev_msg['is_user'], draw_y
                    )
                    draw_y += bubble_height + 10
                
                # Draw current message
                bubble_height = self.draw_message_bubble(draw, text, is_user, draw_y)
                
                frame_path = os.path.join(temp_dir, f'frame_{len(frames):06d}.png')
                img.save(frame_path)
                frames.append(frame_path)
            
            # Add message to shown messages
            messages_shown.append({'text': text, 'is_user': is_user})
            current_y += bubble_height + 10
            
            # Phase 3: Pause between messages
            if msg_idx < len(self.messages) - 1:  # Don't pause after last message
                pause_frames = int(self.pause_between_messages * self.fps)
                for frame in range(pause_frames):
                    # Just repeat the last frame
                    frame_path = os.path.join(temp_dir, f'frame_{len(frames):06d}.png')
                    img.save(frame_path)
                    frames.append(frame_path)
        
        return frames
    
    def generate_video(self, output_path):
        """Generate the complete WhatsApp mockup video with sound"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger.info(f"Generating WhatsApp mockup with {len(self.messages)} messages")
            
            # Generate sound effects
            send_sound_path, receive_sound_path = self.create_sound_effects(temp_dir)
            
            # Generate video frames
            frames = self.generate_frames(temp_dir)
            
            # Create video from frames
            frame_pattern = os.path.join(temp_dir, 'frame_%06d.png')
            video_only_path = os.path.join(temp_dir, 'video_only.mp4')
            
            # Create video
            cmd = [
                'ffmpeg', '-y', '-framerate', str(self.fps),
                '-i', frame_pattern,
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                video_only_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Create audio track with sound effects
            audio_path = self.create_audio_track(temp_dir, send_sound_path, receive_sound_path)
            
            # Combine video and audio
            cmd = [
                'ffmpeg', '-y',
                '-i', video_only_path,
                '-i', audio_path,
                '-c:v', 'copy', '-c:a', 'aac',
                '-shortest',
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
        logger.info(f"WhatsApp mockup video created: {output_path}")
        return output_path
    
    def create_audio_track(self, temp_dir, send_sound_path, receive_sound_path):
        """Create audio track with sound effects at appropriate times"""
        # Calculate timing for each message
        audio_segments = []
        current_time = 0
        
        for message in self.messages:
            is_user = message.get('role', 'user') == 'user'
            
            # Add typing delay for bot messages
            if not is_user:
                current_time += self.typing_duration
            
            # Add sound effect at message appearance
            if is_user:
                sound_file = send_sound_path
            else:
                sound_file = receive_sound_path
            
            audio_segments.append((current_time, sound_file))
            current_time += self.message_display_duration + self.pause_between_messages
        
        # Create silent audio track and overlay sounds
        total_duration = current_time + 1  # Add 1 second buffer
        silent_audio_path = os.path.join(temp_dir, 'silent.wav')
        
        # Create silent audio
        cmd = [
            'ffmpeg', '-y', '-f', 'lavfi',
            '-i', f'anullsrc=duration={total_duration}:sample_rate=44100',
            silent_audio_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Overlay sound effects
        audio_output_path = os.path.join(temp_dir, 'final_audio.wav')
        filter_complex = f"[0:a]"
        
        # Add each sound effect
        for i, (time_offset, sound_file) in enumerate(audio_segments):
            filter_complex += f"[{i+1}:a]adelay={int(time_offset*1000)}|{int(time_offset*1000)}[delayed{i}]; "
            filter_complex += f"[delayed{i}]"
        
        filter_complex += "amix=inputs=" + str(len(audio_segments) + 1) + "[out]"
        
        cmd = ['ffmpeg', '-y', '-i', silent_audio_path]
        for _, sound_file in audio_segments:
            cmd.extend(['-i', sound_file])
        
        cmd.extend([
            '-filter_complex', filter_complex,
            '-map', '[out]',
            audio_output_path
        ])
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return audio_output_path
        except:
            # Fallback to silent audio if sound mixing fails
            return silent_audio_path
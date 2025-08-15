#!/usr/bin/env python3
"""
Growth Tools API - Simple Flask server for WhatsApp mockups and AI slideshows
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import requests
import subprocess
import tempfile
import logging
from PIL import Image, ImageDraw, ImageFont
import replicate
from whatsapp_generator import WhatsAppMockupGenerator

app = Flask(__name__)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
REPLICATE_API_TOKEN = os.getenv('REPLICATE_API_TOKEN')
OUTPUT_DIR = 'output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize Replicate
replicate_client = replicate.Client(api_token=REPLICATE_API_TOKEN) if REPLICATE_API_TOKEN else None

@app.route('/')
def home():
    """API home with documentation"""
    return jsonify({
        'name': 'Growth Tools API',
        'version': '1.0.0',
        'description': 'Simple API for WhatsApp mockups and AI slideshows',
        'endpoints': {
            'slideshow': 'POST /slideshow - Generate slideshow from text prompts',
            'whatsapp': 'POST /whatsapp - Generate WhatsApp mockup video',
            'health': 'GET /health - Health check'
        },
        'examples': {
            'slideshow': {
                'url': 'POST /slideshow',
                'body': {'slides': ['sunset over mountains', 'peaceful lake']},
                'returns': 'MP4 video file'
            },
            'whatsapp': {
                'url': 'POST /whatsapp', 
                'body': {
                    'messages': [
                        {'role': 'user', 'text': 'Hello!'},
                        {'role': 'bot', 'text': 'Hi there!'}
                    ],
                    'bot_name': 'Mystic Maya'
                },
                'returns': 'MP4 video file'
            }
        }
    })

@app.route('/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'OK',
        'replicate_configured': replicate_client is not None,
        'endpoints_active': ['slideshow', 'whatsapp']
    })

@app.route('/slideshow', methods=['POST'])
def generate_slideshow():
    """Generate slideshow video from text prompts"""
    try:
        data = request.get_json()
        slides = data.get('slides', [])
        
        if not slides or len(slides) == 0:
            return jsonify({'error': 'Please provide slides array'}), 400
            
        if len(slides) > 10:
            return jsonify({'error': 'Maximum 10 slides allowed'}), 400
            
        if not replicate_client:
            return jsonify({'error': 'Replicate API not configured'}), 500
        
        session_id = str(uuid.uuid4())[:8]
        logger.info(f'Generating slideshow: {slides}')
        
        # Generate images
        with tempfile.TemporaryDirectory() as temp_dir:
            image_paths = []
            
            for i, prompt in enumerate(slides):
                logger.info(f'Creating image {i+1}: {prompt}')
                
                # Generate image with Replicate
                output = replicate_client.run(
                    "black-forest-labs/flux-schnell",
                    input={
                        "prompt": prompt,
                        "go_fast": True,
                        "megapixels": "1", 
                        "aspect_ratio": "16:9",
                        "output_format": "jpg"
                    }
                )
                
                # Download image
                image_url = output[0] if isinstance(output, list) else output
                response = requests.get(image_url)
                response.raise_for_status()
                
                image_path = os.path.join(temp_dir, f'slide_{i}.jpg')
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                image_paths.append(image_path)
            
            # Create video with FFmpeg
            output_file = os.path.join(OUTPUT_DIR, f'slideshow_{session_id}.mp4')
            
            # Create input list for FFmpeg
            input_list = os.path.join(temp_dir, 'input.txt')
            with open(input_list, 'w') as f:
                for img_path in image_paths:
                    f.write(f"file '{img_path}'\n")
                    f.write("duration 3\n")
                if image_paths:
                    f.write(f"file '{image_paths[-1]}'\n")  # Last frame
            
            # Run FFmpeg
            cmd = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0', 
                '-i', input_list,
                '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2',
                '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                output_file
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
        logger.info(f'Slideshow created: {output_file}')
        return send_file(output_file, as_attachment=True)
        
    except Exception as e:
        logger.error(f'Slideshow error: {e}')
        return jsonify({'error': str(e)}), 500

@app.route('/whatsapp', methods=['POST'])  
def generate_whatsapp():
    """Generate WhatsApp mockup video"""
    try:
        data = request.get_json()
        messages = data.get('messages', [])
        bot_name = data.get('bot_name', 'Bot')
        
        if not messages:
            return jsonify({'error': 'Please provide messages array'}), 400
            
        session_id = str(uuid.uuid4())[:8] 
        logger.info(f'Creating WhatsApp mockup: {len(messages)} messages')
        
        # Use enhanced WhatsApp generator
        generator = WhatsAppMockupGenerator(messages, bot_name)
        output_file = os.path.join(OUTPUT_DIR, f'whatsapp_{session_id}.mp4')
        
        # Generate the video
        generator.generate_video(output_file)
            
        logger.info(f'WhatsApp mockup created: {output_file}')
        return send_file(output_file, as_attachment=True)
        
    except Exception as e:
        logger.error(f'WhatsApp error: {e}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Growth Tools API starting...")
    print("📖 Documentation: http://localhost:8001/")
    print("❤️  Health check: http://localhost:8001/health")
    app.run(debug=True, host='0.0.0.0', port=8001)
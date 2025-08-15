# Growth Tools API

Super simple Flask API for growth-related tasks.

## Features

- **Slideshow Generator**: Create videos from text prompts using AI
- **WhatsApp Mockup**: Generate realistic WhatsApp chat videos
- **No Database**: Everything runs in memory, files auto-cleanup
- **Simple**: Just 4 files total

## Prerequisites

Install FFmpeg for video generation:
```bash
# macOS (if you have Homebrew)
brew install ffmpeg

# Or download from: https://ffmpeg.org/download.html
```

## Quick Start

```bash
./run.sh
```

API runs at: http://localhost:8001

## Endpoints

### `GET /` - Documentation
### `GET /health` - Health check

### `POST /slideshow` - Generate slideshow
```json
{
  "slides": ["sunset over mountains", "peaceful lake", "forest"]
}
```
Returns: MP4 video file

### `POST /whatsapp` - Generate WhatsApp mockup  
```json
{
  "messages": [
    {"role": "user", "text": "Hello!"},
    {"role": "astrologer", "text": "Hi there!"}
  ],
  "astrologer_name": "Mystic Maya"
}
```
Returns: MP4 video file

## Test Commands

```bash
# Test slideshow
curl -X POST http://localhost:8001/slideshow \
  -H "Content-Type: application/json" \
  -d '{"slides":["sunset","lake"]}' \
  --output slideshow.mp4

# Test WhatsApp
curl -X POST http://localhost:8001/whatsapp \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","text":"Hello"},{"role":"astrologer","text":"Hi!"}]}' \
  --output whatsapp.mp4
```

That's it! 🚀
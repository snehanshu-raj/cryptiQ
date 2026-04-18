# HomeGuard Security Dashboard

## Overview
The HomeGuard dashboard is a complete single-page web application that provides remote access to smart home security features via a web interface.

## Architecture

### Backend (FastAPI - `/home/srj/cryptiq/app.py`)
- **Port**: 8000
- **Authentication**: RSA-encrypted password (toy system with n=15)
- **CORS**: Enabled for ngrok and cross-origin access
- **Image Storage**: 
  - Residents: `image_authenticate/known_faces/`
  - Intruders: `image_authenticate/intruder_frames/`

### Frontend (HTML/CSS/JS - `/home/srj/cryptiq/image_authenticate/home-security-dashboard.html`)
- Single-page app (1 HTML file)
- Responsive design (mobile 375px+, desktop)
- Dark/light mode with localStorage persistence
- Web Crypto API for client-side RSA encryption
- No external frameworks (vanilla JavaScript)

## API Endpoints

### Authentication
- **GET** `/public-key` - Returns RSA public key
  ```json
  {"public_key": {"e": 3, "n": 15}}
  ```

- **POST** `/authenticate` - Authenticate with encrypted password
  ```json
  {"encrypted_password": "<base64 encrypted hash>"}
  ```

### Dashboard
- **GET** `/` - Serve main dashboard HTML

### Resident Images
- **GET** `/api/resident-images` - List all resident images
  ```json
  {"images": ["snehanshu/WIN_20260418_02_53_44_Pro.jpg", ...]}
  ```

- **GET** `/api/resident-image/{filename}` - Serve individual resident image
  - Path traversal protected
  - Supports subdirectories (e.g., `person_name/image.jpg`)
  - Valid extensions: `.jpg`, `.jpeg`, `.png`

### Intruder Detection
- **GET** `/api/intruder-images` - List intruder frames (newest first)
  ```json
  {"images": ["intruder_2026-04-18_08-56-29_frame15.jpg", ...]}
  ```

- **GET** `/api/intruder-image/{filename}` - Serve intruder frame
  - Path traversal protected
  - JPG files only
  - Sorted by timestamp (newest first)

## Security Features

1. **Path Traversal Protection**
   - Rejects filenames containing `..` or starting with `/`
   - Validates file is within intended directory
   - Python's `Path.relative_to()` ensures containment

2. **RSA Encryption**
   - Password hashed with SHA256
   - First 2 bytes encrypted with toy RSA (n=15)
   - Server decrypts and verifies

3. **CORS**
   - Allows all origins for ngrok remote access
   - Can be restricted to specific domains in production

## Running the Server

```bash
cd /home/srj/cryptiq
source venv/bin/activate
python app.py
```

Server will start on `http://0.0.0.0:8000`

## Dashboard Usage

1. **Login View**
   - Enter password: `supersecret`
   - Click "Authenticate"
   - Browser encrypts password using Web Crypto API RSA-OAEP
   - Server decrypts and verifies

2. **Dashboard View** (after auth)
   - **Residents Tab**: Grid of enrolled faces (subdirectories supported)
   - **Intruders Tab**: Grid of captured intruder frames with timestamps
   - **Theme Toggle**: Dark/light mode with localStorage persistence
   - **Responsive**: Works on mobile and desktop

## Remote Access via ngrok

```bash
ngrok http 8000
```

Then access the provided ngrok URL (e.g., `https://xxxx-xx-xxx-xxx-xx.ngrok.io`)

## Directory Structure

```
/home/srj/cryptiq/
├── app.py                              # FastAPI backend
├── image_authenticate/
│   ├── home-security-dashboard.html   # Frontend dashboard
│   ├── known_faces/                   # Resident photos (subdirs ok)
│   │   └── snehanshu/
│   │       └── WIN_20260418_02_53_44_Pro.jpg
│   └── intruder_frames/               # Detected intruder frames
│       ├── intruder_2026-04-18_08-56-29_frame15.jpg
│       └── ...
├── password_authenticate/
│   ├── keygen.py                      # Toy RSA key generation
│   ├── public_key.json
│   └── private_key.json
└── requirements.txt
```

## Testing Endpoints

```bash
# Get public key
curl http://localhost:8000/public-key

# List resident images
curl http://localhost:8000/api/resident-images

# List intruder frames
curl http://localhost:8000/api/intruder-images

# Serve HTML dashboard
curl http://localhost:8000/
```

## Features Implemented

✅ Single-page web dashboard (1 HTML file)
✅ Client-side RSA encryption (Web Crypto API)
✅ FastAPI backend with CORS
✅ Image serving with path traversal protection
✅ Resident faces organized by subdirectory
✅ Intruder frames with timestamp sorting
✅ Dark/light mode with persistence
✅ Mobile responsive design
✅ No external dependencies (vanilla JS)

## Notes

- The RSA system is educational (n=15, e=3). In production, use proper cryptography libraries with 2048+ bit keys.
- Image directories are auto-created on first run
- Intruder frames are sorted newest-first for quick review
- Dashboard caches authentication token in sessionStorage for same-session access

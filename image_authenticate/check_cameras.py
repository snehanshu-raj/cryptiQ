"""
check_cameras.py — Detect and list all available cameras.

Scans camera indices 0-10 and tests which ones are accessible.
Shows camera resolution and FPS for each available camera.
"""

import cv2

def list_available_cameras(max_index=10):
    """Find all available camera devices."""
    available_cameras = []
    
    print("Scanning for available cameras...")
    print("-" * 50)
    
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # Get camera properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            backend = cap.getBackendName()
            
            available_cameras.append({
                'index': i,
                'width': width,
                'height': height,
                'fps': fps,
                'backend': backend
            })
            
            print(f"Camera {i}:")
            print(f"  Resolution: {width}x{height}")
            print(f"  FPS: {fps}")
            print(f"  Backend: {backend}")
            print()
            
            cap.release()
    
    print("-" * 50)
    if available_cameras:
        print(f"Found {len(available_cameras)} camera(s)")
        return available_cameras
    else:
        print("No cameras found!")
        return []

if __name__ == "__main__":
    cameras = list_available_cameras()
    
    if cameras:
        print("\n📸 Usage:")
        print("Set CAMERA_INDEX in recognize.py to one of:")
        for cam in cameras:
            print(f"  CAMERA_INDEX = {cam['index']}  ({cam['width']}x{cam['height']})")

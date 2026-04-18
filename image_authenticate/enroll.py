"""
enroll.py — Enrollment script for face authentication.

Scans the known_faces/ directory for subdirectories (one per person).
Each subdirectory should contain face photos of that person.
The script detects faces, extracts ArcFace embeddings, averages them
per person, and stores the result in the SQLite database.

Usage:
    python enroll.py                    # Enroll all people from known_faces/
    python enroll.py --clear            # Clear DB before enrolling
    python enroll.py --list             # Just list currently enrolled residents
"""

import os
import sys
import argparse
import numpy as np
import cv2
from insightface.app import FaceAnalysis

from db import init_db, insert_resident, clear_db, delete_resident, list_residents

# Paths relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWN_FACES_DIR = os.path.join(SCRIPT_DIR, "known_faces")
MODEL_DIR = os.path.join(SCRIPT_DIR, "models")

# Supported image extensions
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def load_model():
    """Initialize InsightFace with ArcFace model, cached in models/ directory."""
    print("[enroll] Loading InsightFace model (this may download ~200MB on first run)...")
    app = FaceAnalysis(
        name="buffalo_l",
        root=MODEL_DIR,
        providers=["CPUExecutionProvider"]
    )
    app.prepare(ctx_id=-1, det_size=(640, 640))
    print("[enroll] Model loaded.\n")
    return app


def get_embedding(app, image_path):
    """
    Detect a face in the image and return its embedding.

    Returns:
        numpy array (512-dim) if exactly one face found, else None.
        Also returns a status message for logging.
    """
    img = cv2.imread(image_path)
    if img is None:
        return None, f"  SKIP: Could not read image: {image_path}"

    faces = app.get(img)

    if len(faces) == 0:
        return None, f"  SKIP: No face detected in {os.path.basename(image_path)}"
    if len(faces) > 1:
        return None, f"  SKIP: Multiple faces ({len(faces)}) in {os.path.basename(image_path)}"

    return faces[0].embedding, f"  OK: Extracted embedding from {os.path.basename(image_path)}"


def enroll_all(app):
    """Scan known_faces/ and enroll each person."""
    if not os.path.isdir(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
        print(f"[enroll] Created {KNOWN_FACES_DIR}/")
        print("[enroll] Add subdirectories with photos, e.g.:")
        print("         known_faces/john/photo1.jpg")
        print("         known_faces/alice/front.jpg")
        return

    # Get person directories
    person_dirs = sorted([
        d for d in os.listdir(KNOWN_FACES_DIR)
        if os.path.isdir(os.path.join(KNOWN_FACES_DIR, d)) and not d.startswith(".")
    ])

    if not person_dirs:
        print("[enroll] No person directories found in known_faces/")
        print("         Add subdirectories with photos, e.g.: known_faces/john/photo1.jpg")
        return

    # Summary counters
    total_enrolled = 0
    total_photos_used = 0
    total_photos_skipped = 0

    for person_name in person_dirs:
        person_path = os.path.join(KNOWN_FACES_DIR, person_name)
        print(f"\n--- Enrolling: {person_name} ---")

        # Gather image files
        image_files = sorted([
            f for f in os.listdir(person_path)
            if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
            and not f.startswith(".")
        ])

        if not image_files:
            print(f"  No image files found for {person_name}, skipping.")
            continue

        # Extract embeddings from each photo
        embeddings = []
        skipped = 0

        for filename in image_files:
            filepath = os.path.join(person_path, filename)
            embedding, message = get_embedding(app, filepath)
            print(message)
            if embedding is not None:
                embeddings.append(embedding)
            else:
                skipped += 1

        if not embeddings:
            print(f"  WARNING: No valid face embeddings for {person_name}, not enrolled.")
            total_photos_skipped += skipped
            continue

        # Average all embeddings into one vector
        avg_embedding = np.mean(embeddings, axis=0)

        # L2-normalize the averaged embedding
        norm = np.linalg.norm(avg_embedding)
        if norm > 0:
            avg_embedding = avg_embedding / norm

        # Remove old entry if re-enrolling, then insert
        delete_resident(person_name)
        insert_resident(person_name, avg_embedding)

        total_enrolled += 1
        total_photos_used += len(embeddings)
        total_photos_skipped += skipped

    # Print summary
    print("\n" + "=" * 50)
    print("ENROLLMENT SUMMARY")
    print("=" * 50)
    print(f"  People enrolled : {total_enrolled}")
    print(f"  Photos used     : {total_photos_used}")
    print(f"  Photos skipped  : {total_photos_skipped}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Enroll faces into the authentication database.")
    parser.add_argument("--clear", action="store_true", help="Clear all residents before enrolling")
    parser.add_argument("--list", action="store_true", help="List enrolled residents and exit")
    args = parser.parse_args()

    init_db()

    if args.list:
        list_residents()
        return

    if args.clear:
        print("[enroll] Clearing all existing residents...")
        clear_db()

    app = load_model()
    enroll_all(app)

    print("\nCurrently enrolled:")
    list_residents()


if __name__ == "__main__":
    main()

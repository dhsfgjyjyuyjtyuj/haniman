import os
import json
import random
import time
from instagrapi import Client
from moviepy.editor import ImageClip, VideoFileClip

# --- Random Delay (25-40 min effect) ---
random_wait = random.randint(0, 600)
print(f"Waiting {random_wait} seconds...")
time.sleep(random_wait)

# CONFIG
SESSION_ID = os.environ.get("INSTA_SESSION_ID")
STATE_FILE = "state.json"
PHOTO_FOLDER = "./photos"
MUSIC_FOLDER = "./music"

def load_state():
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

# Login
cl = Client()
cl.login_by_sessionid(SESSION_ID)

# List Files
photos = sorted([f for f in os.listdir(PHOTO_FOLDER) if f.endswith(('.jpg', '.jpeg', '.png'))])
songs = sorted([f for f in os.listdir(MUSIC_FOLDER) if f.endswith(('.mp4', '.mov'))])

state = load_state()
p_idx = state["photo_index"] % len(photos)
s_idx = state["song_index"] % len(songs)
start_time = state["last_timestamp"]

current_photo = os.path.join(PHOTO_FOLDER, photos[p_idx])
current_song = os.path.join(MUSIC_FOLDER, songs[s_idx])

print(f"Using Photo: {photos[p_idx]}, Song: {songs[s_idx]} from {start_time}s")

try:
    # Load Music
    song_clip = VideoFileClip(current_song)
    
    # Agar gaana khatam hone wala hai, toh agla gaana uthao
    if start_time + 6 > song_clip.duration:
        print("Song ending, moving to next song...")
        s_idx = (s_idx + 1) % len(songs)
        start_time = 8
        song_clip.close()
        current_song = os.path.join(MUSIC_FOLDER, songs[s_idx])
        song_clip = VideoFileClip(current_song)

    # Cut Audio and Create Video
    audio_clip = song_clip.audio.subclip(start_time, start_time + 6)
    photo_clip = ImageClip(current_photo).set_duration(6).set_fps(24)
    photo_clip.audio = audio_clip
    
    # Reel Save
    output = "final_reel.mp4"
    photo_clip.write_videofile(output, codec="libx264", audio_codec="aac", fps=24, logger=None)

    # Upload
    caption = "Viral Sound! 🎵 #music #reels #trending #explore"
    cl.clip_upload(output, caption=caption)
    print("✅ Upload Successful!")

    # Update State for NEXT RUN
    state["photo_index"] = p_idx + 1
    state["song_index"] = s_idx
    state["last_timestamp"] = start_time + 6
    save_state(state)

    # Clean up
    song_clip.close()
    photo_clip.close()
    os.remove(output)

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
import os
import json
import random
import time
from instagrapi import Client
from moviepy.editor import ImageClip, AudioFileClip

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
songs = sorted([f for f in os.listdir(MUSIC_FOLDER) if f.lower().endswith(('.mp3', '.wav', '.m4a'))])

state = load_state()
p_idx = state["photo_index"] % len(photos)
s_idx = state["song_index"] % len(songs)
start_time = state["last_timestamp"]

current_photo = os.path.join(PHOTO_FOLDER, photos[p_idx])
current_song = os.path.join(MUSIC_FOLDER, songs[s_idx])

print(f"Using Photo: {photos[p_idx]}, Song: {songs[s_idx]} from {start_time}s")

try:
    # --- बदलाव: VideoFileClip की जगह AudioFileClip किया गया है ---
    audio_clip = AudioFileClip(current_song)
    
    # Agar gaana khatam hone wala hai, toh agla gaana uthao
    if start_time + 6 > audio_clip.duration:
        print("Song ending, moving to next song...")
        s_idx = (s_idx + 1) % len(songs)
        start_time = 8
        audio_clip.close()
        current_song = os.path.join(MUSIC_FOLDER, songs[s_idx])
        audio_clip = AudioFileClip(current_song)

    # Cut Audio and Create Video
    extracted_audio = audio_clip.subclip(start_time, start_time + 6)
    photo_clip = ImageClip(current_photo).set_duration(6).set_fps(24)
    
    # --- बदलाव: Reel का STANDARD साइज (1080, 1920) सेट किया गया है ---
    photo_clip = photo_clip.resize((1080, 1920))
    photo_clip.audio = extracted_audio
    
    # Reel Save
    output = "final_reel.mp4"
    photo_clip.write_videofile(output, codec="libx264", audio_codec="aac", fps=24, logger=None)

    # --- बदलाव: हर बार नया और यूनिक कैप्शन बनाने का लॉजिक (त्रुटिहीन) ---
    raw_title = songs[s_idx].replace('.mp3', '').replace('.wav', '').replace('.m4a', '')
    song_title = raw_title.split(" 128")[0].split(" 320")[0].strip()
    
    mood_lines = [
        f"This song hits different... 🎧✨ | Listening to: {song_title}",
        f"Current vibe status: ON repeat! ❤️🎵 | {song_title}",
        f"Feelin' this melody today. ✨🎶 | Song: {song_title}",
        f"Let the music heal your soul. 🎧💫 | Now Playing: {song_title}",
        f"Just close your eyes and feel the music. 🌟 | {song_title}",
        f"Can't get this track out of my head! 🎶🔥 | {song_title}",
        f"Music is the shorthand of emotion. ❤️🎧 | {song_title}",
        f"A perfect song for a perfect mood. ✨🎵 | Now Playing: {song_title}",
        f"Lost in the rhythm of this sound. 🌌🎶 | {song_title}",
        f"Some songs just touch the heart directly. 🎧💖 | {song_title}"
    ]
    
    hashtag_sets = [
        "\n\n#music #reels #trending #explore #viral #foryou",
        "\n\n#trendingreels #instamusic #vibes #explorepage #fyp",
        "\n\n#reelsindia #viralvideos #lovesongs #bgm #instagramreels",
        "\n\n#songstatus #feelthemusic #reelsviral #trendingnow #musiclover",
        "\n\n#statusvideo #hindisongs #explore #foryoupage #soundon"
    ]
    
    caption = random.choice(mood_lines) + random.choice(hashtag_sets)

    # Upload (अब नए कैप्शन के साथ अपलोड होगा)
    cl.clip_upload(output, caption=caption)
    print("✅ Upload Successful!")

    # Update State for NEXT RUN
    state["photo_index"] = p_idx + 1
    state["song_index"] = s_idx
    state["last_timestamp"] = start_time + 6
    save_state(state)

    # Clean up
    audio_clip.close()
    photo_clip.close()
    os.remove(output)

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

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
SESSION_ID = os.environ.get("INSTA_SESSION_ID", "").strip()
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
    
    # --- बदलाव (फिक्स): पहले इमेज का असली साइज लोड करना ताकि इवन नंबर का ग्लिच न आए ---
    temp_clip = ImageClip(current_photo)
    w, h = temp_clip.w, temp_clip.h
    
    # यदि साइज ऑड (Odd) है तो उसे इवन (Even) में बदलें ताकि FFmpeg क्रैश न हो
    if w % 2 != 0: w -= 1
    if h % 2 != 0: h -= 1
    
    # इमेज को उसके असली लेकिन सुधरे हुए इवन साइज में सेट करें
    photo_clip = temp_clip.resize((w, h)).set_duration(6).set_fps(24)
    
    # अब मामूली ज़ूम-इन इफ़ेक्ट बिना किसी ग्लिच या लाइन्स के काम करेगा
    photo_clip = photo_clip.resize(lambda t: 1 + 0.016 * t)
    photo_clip.audio = extracted_audio
    
    # Reel Save
    output = "final_reel.mp4"
    photo_clip.write_videofile(output, codec="libx264", audio_codec="aac", fps=24, logger=None)

    # हर बार नया और यूनिक कैप्शन बनाने का लॉजिक
    raw_title = songs[s_idx].replace('.mp3', '').replace('.wav', '').replace('.m4a', '')
    song_title = raw_title.split(" 128")[0].split(" 320")[0].strip()
    
    mood_lines = [
        f"कुछ रिश्ते दर्द नहीं देते, सबक दे जाते हैं... 💔🥀 | 🎧: {song_title}",
        f"सबके बीच रहकर भी जो खालीपन लगे, वही असली अकेलापन है। 🌌🩹 | 🎧: {song_title}",
        f"दर्द कम नहीं हुआ है मेरा, बस सहने की आदत हो गयी है। 🥲💔 | 🎧: {song_title}",
        f"हम अधूरे लोग हैं... हमारी न नींद पूरी होती है, न ख्वाब। 💭🥀 | 🎧: {song_title}",
        f"खामोशी में भी कैसे रोया जाता है, ये सिर्फ टूटा हुआ दिल जानता है। 🤫💧 | 🎧: {song_title}",
        f"जो टूटकर भी मुस्कुरा दे, ऐसा इंसान हूँ मैं... 🩹🙂 | 🎧: {song_title}",
        f"Tune mujhe adhoora chhod diya, aur khud aage badh gaya. 💔🍂 | 🎧: {song_title}",
        f"Dard chhupa lena hi ab aadat ban gayi hai... 🥀🖤 | 🎧: {song_title}",
        f"Aansoo bhi ab mere nahi rahe, woh भी तेरा नाम लेकर गिरते हैं। 🥹💧 | 🎧: {song_title}",
        f"It hurts, but it's okay. I'm used to it. 💔🌌 | 🎧: {song_title}"
    ]
    
    hashtag_sets = [
        "\n\n#sadreels #brokenheart #sadstatus #feelings #aesthetic #explorepage",
        "\n\n#alone #sadshayari #lovesongs #bgm #trendingreels #foryou",
        "\n\n#mood #sadstatus #hindishayari #relatablequotes #viralreels #fyp",
        "\n\n#heartbroken #lonelyvibes #truelines #instagramreels #soundon",
        "\n\n#sadposts #shayarilover #feelthemusic #deepfeelings #explore #viral"
    ]
    
    caption = random.choice(mood_lines) + random.choice(hashtag_sets)

    # Upload
    cl.clip_upload(output, caption=caption)
    print("✅ Upload Successful with Sad Caption!")

    # Update State for NEXT RUN
    state["photo_index"] = p_idx + 1
    state["song_index"] = s_idx
    state["last_timestamp"] = start_time + 6
    save_state(state)

    # Clean up
    audio_clip.close()
    photo_clip.close()
    temp_clip.close()
    os.remove(output)

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

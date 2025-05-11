import subprocess
import time
import selenium.webdriver as webdriver
import speech_recognition as sr
import os
from pydub.silence import split_on_silence
from pydub import AudioSegment
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

MEET_AUDIO = "meeting_audio.wav"

def record_audio(meet_audio_file):
    print("Audio recording started...")
    return subprocess.Popen([
        "ffmpeg",
        "-y",
        "-f", "dshow",
        "-i", "audio=Stereo Mix", 
        meet_audio_file
    ],
    stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

def join_meeting_and_record(link):
    opt = Options()
    opt.add_argument('--disable-blink-features=AutomationControlled')
    opt.add_argument('--start-maximized')
    opt.add_experimental_option("prefs", {
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.geolocation": 0,
        "profile.default_content_setting_values.notifications": 1
    })
    driver = webdriver.Chrome(options=opt)
    driver.get(link)

    ffmpeg_proc = record_audio(MEET_AUDIO)

    try:
        while True:
            if len(driver.window_handles) == 0:
                break
            time.sleep(5)
    except:
        pass
    finally:
        driver.quit()
        print("Meeting ended.")

    # Stop audio recording
    ffmpeg_proc.terminate()
    print("Recording stopped.")

    return audio_to_text(MEET_AUDIO)

def audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    sound = AudioSegment.from_wav(audio_file)
    chunks = split_on_silence(sound, min_silence_len=500, silence_thresh=sound.dBFS-14, keep_silence=500)
    folder_name = 'audio_chunks'
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)

    fullSummary = ''
    for i, chunk in enumerate(chunks):
        chunk_filename = os.path.join(folder_name, f'chunk{i}.wav')
        chunk.export(chunk_filename, format='wav')
        with sr.AudioFile(chunk_filename) as source:
            audio_listened = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_listened)
            except sr.UnknownValueError:
                text = ''
            fullSummary += f'{text} '
    # print("full text is ", fullSummary)
    return fullSummary



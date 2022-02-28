from flask import Flask, render_template, request, redirect
import speech_recognition as sr
import os 
from pydub import AudioSegment
from pydub.silence import split_on_silence
import pyttsx3 


app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    transcript = ""
    if request.method == "POST":
        print("FORM DATA RECEIVED")

        if "file" not in request.files:
            return redirect(request.url)

        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)

        if file:
            recognizer = sr.Recognizer()
            # path = sr.AudioFile(file)
            # with audioFile as source:
            #     data = recognizer.record(source)
            # transcript = recognizer.recognize_google(data, key=None)
            # path = sys.file.append('/path/to/ffmpeg')
            sound = AudioSegment.from_wav(file)  
            
            # split audio sound where silence is 700 miliseconds or more and get chunks
            chunks = split_on_silence(sound,
                # experiment with this value for your target audio file
                min_silence_len = 500,
                # adjust this per requirement
                silence_thresh = sound.dBFS-14,
                # keep the silence for 1 second, adjustable as well
                keep_silence=500,
            )
            folder_name = "audio-chunks"
            # create a directory to store the audio chunks
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
            transcript = ""
            # process each chunk 
            for i, audio_chunk in enumerate(chunks, start=1):
                # export audio chunk and save it in
                # the `folder_name` directory.
                chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
                audio_chunk.export(chunk_filename, format="wav")
                # recognize the chunk
                with sr.AudioFile(chunk_filename) as source:
                    audio_listened = recognizer.record(source)
                    # try converting it to text
                    try:
                        text = recognizer.recognize_google(audio_listened, language="all")
                    except sr.UnknownValueError as e:
                        print("Error:", str(e))
                    except sr.FileNotFoundError:
                        print("Cannot convert audio")
                    else:
                        text = f"{text.capitalize()}. "
                        # print(chunk_filename, ":", text)
                        transcript += text

    return render_template('index.html', transcript=transcript)


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
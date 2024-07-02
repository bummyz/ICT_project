import os
import io
import openai
import pyaudio
import wave
from google.cloud import speech
from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.playback import play

# API 키 설정
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/your/service-account-file.json"
openai.api_key = "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"

# 음성 녹음 함수
def record_audio(duration=5, filename="recorded.wav"):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = duration

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    frames = []

    print("Recording...")

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return filename

# 음성 인식 함수
def transcribe_audio(file_path):
    client = speech.SpeechClient()

    with io.open(file_path, "rb") as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ko-KR",
    )

    response = client.recognize(config=config, audio=audio)
    for result in response.results:
        return result.alternatives[0].transcript

# AI 답변 생성 함수
def get_ai_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# 텍스트를 음성으로 변환 함수
def synthesize_text(text, output_file="output.mp3"):
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="ko-KR",
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file "{output_file}"')

    return output_file

# 음성 재생 함수
def play_audio(file_path):
    audio = AudioSegment.from_mp3(file_path)
    play(audio)

# 전체 프로세스 실행 함수
def main():
    # 음성 녹음
    audio_file = record_audio()
    # 음성 인식
    transcribed_text = transcribe_audio(audio_file)
    print("Transcribed Text: ", transcribed_text)

    # AI 답변 생성
    response_text = get_ai_response(transcribed_text)
    print("AI Response: ", response_text)

    # 텍스트를 음성으로 변환
    audio_output_file = synthesize_text(response_text)
    # 음성 재생
    play_audio(audio_output_file)

if __name__ == "__main__":
    main()

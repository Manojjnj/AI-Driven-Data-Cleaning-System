from faster_whisper import WhisperModel
import os

# Load the Whisper model once (can be tiny, base, small, medium, large)
model = WhisperModel("base")  # change to "small" or "medium" for higher accuracy

def transcribe_file(file_path):
    """
    Transcribes audio to text using local Faster-Whisper.
    
    Args:
        file_path (str): Path to the audio file.
        
    Returns:
        str: Transcribed text.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
    
    segments, info = model.transcribe(file_path)
    text = ""
    for segment in segments:
        text += segment.text + " "
    
    return text.strip()


# Example usage
if __name__ == "__main__":
    audio_file = "sample_audio.mp3"  # replace with your file
    try:
        result = transcribe_file(audio_file)
        print("Transcription:", result)
    except Exception as e:
        print("Error:", e)

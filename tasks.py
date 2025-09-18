# Core processing functions for the audio translation pipeline.
import yaml
from pathlib import Path
import ffmpeg
from pydub import AudioSegment
import collections
import torch
from pyannote.audio import Pipeline
import whisper
from google.cloud import translate_v2 as translate
from elevenlabs import generate, save
from elevenlabs.client import ElevenLabs

SUPPORTED_EXTENSIONS = [".wav", ".mp3", ".flac", ".ogg", ".m4a"]

def load_config(config_path="config.yaml"):
    """Loads the configuration from a YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def validate_inputs(filepath: str):
    """
    Checks if the input file exists and has a supported extension.
    Returns the Path object if valid, otherwise raises an error.
    """
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found at: {filepath}")
    if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {p.suffix}. Supported are: {SUPPORTED_EXTENSIONS}")
    print(f"Input file validation successful for: {filepath}")
    return p

def probe_media(filepath: str):
    """
    Uses ffmpeg-python to get media details.
    Returns a dictionary with media properties.
    """
    try:
        print(f"Probing media file: {filepath}")
        probe = ffmpeg.probe(filepath)
        audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
        if audio_stream is None:
            raise ValueError("No audio stream found in the file.")
        print("Probe successful.")
        return audio_stream
    except ffmpeg.Error as e:
        print(f"Error probing media file: {e.stderr}")
        raise

def preprocess_audio(filepath: str, target_sr: int = 16000, target_channels: int = 1, target_bitrate: str = "16k"):
    """
    Resamples, converts to mono, and ensures consistent audio format.
    Returns the path to the preprocessed audio file.
    """
    print(f"Preprocessing audio file: {filepath}")
    audio = AudioSegment.from_file(filepath)

    audio = audio.set_frame_rate(target_sr)
    audio = audio.set_channels(target_channels)

    # Export to a temporary path to have a consistent format (wav) for other tools.
    temp_dir = Path("/tmp/audio_pipeline")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_path = temp_dir / f"preprocessed_{Path(filepath).stem}.wav"
    audio.export(str(temp_path), format="wav", bitrate=target_bitrate)

    print(f"Audio preprocessed and saved to: {temp_path}")
    return str(temp_path)

def diarize_speakers(audio_path: str, config: dict):
    """
    Performs speaker diarization using pyannote.audio.
    Returns a list of segment dictionaries, including paths to audio chunks.

    Note: This requires a Hugging Face token with access to the pyannote models.
    Ensure you have logged in via `huggingface-cli login`.
    """
    print(f"Starting speaker diarization for: {audio_path}")
    model_name = config.get("models", {}).get("diarization", "pyannote/speaker-diarization-3.1")

    try:
        pipeline = Pipeline.from_pretrained(model_name)
        print("Diarization pipeline loaded.")
    except Exception as e:
        if "401" in str(e):
            print("\n---")
            print("!!! Pyannote Model Access Error !!!")
            print(f"Failed to load model '{model_name}'. This usually means you need to accept the user agreement on Hugging Face and provide an access token.")
            print("1. Visit hf.co/pyannote/speaker-diarization-3.1 and accept the license.")
            print("2. Visit hf.co/settings/tokens to create a token.")
            print("3. Run `huggingface-cli login` in your terminal and paste the token.")
            print("---\n")
        raise

    diarization = pipeline(str(audio_path))

    segments = []
    audio = AudioSegment.from_file(audio_path)
    output_dir = Path(config.get("paths", {}).get("output_dir", "output")) / "chunks"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Processing {len(diarization.itertracks(yield_label=True))} speaker segments...")
    for i, (turn, _, speaker) in enumerate(diarization.itertracks(yield_label=True)):
        start_ms = int(turn.start * 1000)
        end_ms = int(turn.end * 1000)

        # Extract audio chunk
        chunk = audio[start_ms:end_ms]
        chunk_path = output_dir / f"chunk_{i:04d}_{speaker}.wav"
        chunk.export(str(chunk_path), format="wav")

        segment_info = {
            "start_time": turn.start,
            "end_time": turn.end,
            "speaker_label": speaker,
            "audio_chunk_path": str(chunk_path)
        }
        segments.append(segment_info)

    print(f"Diarization complete. Created {len(segments)} audio chunks.")
    return segments

def transcribe_segments(segments: list, config: dict):
    """
    Transcribes each audio chunk using openai-whisper.
    Adds the 'text_en' key to each segment dictionary.
    """
    print(f"Starting transcription for {len(segments)} segments...")
    model_name = config.get("models", {}).get("whisper", "base")

    try:
        model = whisper.load_model(model_name)
        print(f"Whisper model '{model_name}' loaded.")
    except Exception as e:
        print(f"Error loading whisper model: {e}")
        raise

    for i, segment in enumerate(segments):
        audio_path = segment["audio_chunk_path"]
        print(f"Transcribing chunk {i+1}/{len(segments)}: {audio_path}")

        try:
            result = model.transcribe(audio_path, fp16=torch.cuda.is_available())
            text = result["text"].strip()
            segment["text_en"] = text
            print(f" > Text: {text}")
        except Exception as e:
            print(f"Error during transcription of {audio_path}: {e}")
            segment["text_en"] = "Transcription failed."

    print("Transcription complete.")
    return segments

def translate_segments(segments: list, target_language: str = "es"):
    """
    Translates the 'text_en' in each segment to the target language.
    Adds the 'text_es' key to each segment dictionary.

    Note: Requires Google Cloud credentials to be configured in the environment.
    """
    print(f"Starting translation to '{target_language}' for {len(segments)} segments...")

    try:
        translate_client = translate.Client()
        print("Google Translate client initialized.")
    except Exception as e:
        print("\n---")
        print("!!! Google Cloud Authentication Error !!!")
        print(f"Failed to initialize Google Translate client: {e}")
        print("Please ensure you have authenticated with Google Cloud. For example, run:")
        print("gcloud auth application-default login")
        print("---\n")
        raise

    for i, segment in enumerate(segments):
        text_to_translate = segment.get("text_en")
        if not text_to_translate or text_to_translate == "Transcription failed.":
            print(f"Skipping translation for segment {i+1} (no text).")
            segment["text_es"] = ""
            continue

        print(f"Translating segment {i+1}/{len(segments)}...")
        try:
            result = translate_client.translate(text_to_translate, target_language=target_language)
            translated_text = result["translatedText"]
            segment[f"text_{target_language}"] = translated_text
            print(f" > Original: {text_to_translate}")
            print(f" > Translated: {translated_text}")
        except Exception as e:
            print(f"Error during translation of segment {i+1}: {e}")
            segment[f"text_{target_language}"] = "Translation failed."

    print("Translation complete.")
    return segments

def synthesize_speech(segments: list, config: dict, target_language: str = "es"):
    """
    Synthesizes speech from the translated text for each segment.
    Adds the 'tts_audio_path_es' key to each segment dictionary.
    """
    print(f"Starting speech synthesis for {len(segments)} segments...")
    api_key = config.get("api_keys", {}).get("elevenlabs")
    if not api_key or "YOUR_ELEVENLABS_API_KEY" in api_key:
        print("\n---")
        print("!!! ElevenLabs API Key Missing !!!")
        print("Skipping speech synthesis. Please add your ElevenLabs API key to config.yaml.")
        print("---\n")
        # Add empty paths so the pipeline doesn't break
        for segment in segments:
            segment[f"tts_audio_path_{target_language}"] = None
        return segments

    try:
        client = ElevenLabs(api_key=api_key)
        print("ElevenLabs client initialized.")
    except Exception as e:
        print(f"Error initializing ElevenLabs client: {e}")
        raise

    output_dir = Path(config.get("paths", {}).get("output_dir", "output")) / f"tts_{target_language}"
    output_dir.mkdir(parents=True, exist_ok=True)

    for i, segment in enumerate(segments):
        text_to_synthesize = segment.get(f"text_{target_language}")
        tts_path_key = f"tts_audio_path_{target_language}"

        if not text_to_synthesize or "Translation failed" in text_to_synthesize:
            print(f"Skipping TTS for segment {i+1} (no translated text).")
            segment[tts_path_key] = None
            continue

        print(f"Synthesizing speech for segment {i+1}/{len(segments)}...")
        try:
            # Using a generic voice and a multilingual model suitable for Spanish
            audio = client.generate(
                text=text_to_synthesize,
                voice="Rachel", # A versatile voice
                model="eleven_multilingual_v2"
            )

            output_path = output_dir / f"tts_chunk_{i:04d}.wav"
            save(audio, str(output_path))

            segment[tts_path_key] = str(output_path)
            print(f" > Saved TTS audio to: {output_path}")

        except Exception as e:
            print(f"Error during speech synthesis for segment {i+1}: {e}")
            segment[tts_path_key] = None

    print("Speech synthesis complete.")
    return segments

def _seconds_to_srt_timestamp(seconds: float) -> str:
    """Converts seconds to SRT timestamp format (HH:MM:SS,ms)."""
    hours = int(seconds / 3600)
    seconds %= 3600
    minutes = int(seconds / 60)
    seconds %= 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

def reassemble_audio(segments: list, config: dict, target_language: str = "es"):
    """
    Reassembles the translated audio chunks into a single audio file.
    """
    print("Reassembling final translated audio...")
    if not segments:
        print("No segments to reassemble. Skipping.")
        return None

    # Find the total duration of the final audio
    total_duration_s = max(s['end_time'] for s in segments if 'end_time' in s)
    total_duration_ms = int(total_duration_s * 1000)

    # Create a silent base track
    final_audio = AudioSegment.silent(duration=total_duration_ms)

    for i, segment in enumerate(segments):
        tts_path = segment.get(f"tts_audio_path_{target_language}")
        if not tts_path or not Path(tts_path).exists():
            print(f"Skipping reassembly for segment {i+1} (no TTS audio).")
            continue

        try:
            tts_chunk = AudioSegment.from_file(tts_path)
            start_time_ms = int(segment['start_time'] * 1000)
            final_audio = final_audio.overlay(tts_chunk, position=start_time_ms)
        except Exception as e:
            print(f"Could not process chunk {tts_path}: {e}")

    output_dir = Path(config.get("paths", {}).get("output_dir", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    final_audio_path = output_dir / f"final_translation_{target_language}.wav"

    final_audio.export(str(final_audio_path), format="wav")
    print(f"Final reassembled audio saved to: {final_audio_path}")
    return str(final_audio_path)

def generate_transcript_file(segments: list, config: dict, target_language: str = "es"):
    """
    Generates a text transcript file from the segments.
    """
    print("Generating transcript file...")
    output_dir = Path(config.get("paths", {}).get("output_dir", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = output_dir / f"transcript_{target_language}.txt"

    with open(transcript_path, 'w', encoding='utf-8') as f:
        for segment in segments:
            start = segment['start_time']
            end = segment['end_time']
            speaker = segment['speaker_label']
            text_en = segment.get('text_en', '[No transcription]')
            text_translated = segment.get(f'text_{target_language}', '[No translation]')

            f.write(f"[{_seconds_to_srt_timestamp(start)} --> {_seconds_to_srt_timestamp(end)}] Speaker: {speaker}\n")
            f.write(f"EN: {text_en}\n")
            f.write(f"{target_language.upper()}: {text_translated}\n\n")

    print(f"Transcript file saved to: {transcript_path}")
    return str(transcript_path)

def generate_subtitle_file(segments: list, config: dict, target_language: str = "es"):
    """
    Generates an SRT subtitle file from the translated text.
    """
    print("Generating SRT subtitle file...")
    output_dir = Path(config.get("paths", {}).get("output_dir", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    subtitle_path = output_dir / f"subtitles_{target_language}.srt"

    with open(subtitle_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments):
            text_translated = segment.get(f'text_{target_language}')
            if not text_translated:
                continue

            start_time = _seconds_to_srt_timestamp(segment['start_time'])
            end_time = _seconds_to_srt_timestamp(segment['end_time'])

            f.write(f"{i + 1}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text_translated}\n\n")

    print(f"Subtitle file saved to: {subtitle_path}")
    return str(subtitle_path)

def generate_report(segments: list, config: dict):
    """
    Generates a summary report of the translation process.
    """
    print("Generating summary report...")
    if not segments:
        print("Cannot generate report: no segments provided.")
        return None

    # --- Calculations ---
    total_segments = len(segments)
    total_duration = max(s['end_time'] for s in segments)

    speaker_labels = [s['speaker_label'] for s in segments]
    num_speakers = len(set(speaker_labels))
    segments_per_speaker = collections.Counter(speaker_labels)

    duration_per_speaker = collections.defaultdict(float)
    for s in segments:
        duration_per_speaker[s['speaker_label']] += (s['end_time'] - s['start_time'])

    # --- Formatting ---
    report_lines = []
    report_lines.append("--- Audio Translation Pipeline Report ---")
    report_lines.append(f"\nTotal Duration: {_seconds_to_srt_timestamp(total_duration)}")
    report_lines.append(f"Total Segments Processed: {total_segments}")
    report_lines.append(f"Number of Unique Speakers: {num_speakers}")

    report_lines.append("\nSpeaker-specific Details:")
    for speaker, count in segments_per_speaker.items():
        duration_str = _seconds_to_srt_timestamp(duration_per_speaker[speaker])
        report_lines.append(f"  - {speaker}:")
        report_lines.append(f"    - Number of Segments: {count}")
        report_lines.append(f"    - Total Speech Duration: {duration_str}")

    report_str = "\n".join(report_lines)
    print(report_str)

    # --- Save Report to File ---
    output_dir = Path(config.get("paths", {}).get("output_dir", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "report.txt"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_str)

    print(f"\nReport saved to: {report_path}")

    # --- Return as Dictionary ---
    report_dict = {
        "total_duration_seconds": total_duration,
        "total_segments": total_segments,
        "num_speakers": num_speakers,
        "segments_per_speaker": dict(segments_per_speaker),
        "duration_per_speaker_seconds": dict(duration_per_speaker)
    }
    return report_dict

print("Tasks module initialized with all functions.")

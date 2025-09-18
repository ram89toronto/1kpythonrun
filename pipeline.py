# Main orchestrator for the audio translation pipeline.
import tasks
import argparse
from pathlib import Path
import time

def main(audio_path: str, config_path: str = "config.yaml", target_language: str = "es"):
    """
    Runs the full audio translation pipeline from start to finish.
    """
    start_time = time.time()
    print("--- Starting Audio Translation Pipeline ---")

    # 1. Load configuration
    config = tasks.load_config(config_path)
    print(f"Configuration loaded from {config_path}")

    # Create output directory if it doesn't exist
    output_dir = Path(config.get("paths", {}).get("output_dir", "output"))
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output will be saved to: {output_dir.resolve()}")

    # 2. Validate inputs
    try:
        input_file = tasks.validate_inputs(audio_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return

    # 3. Preprocess Audio
    # We use the original audio for diarization, but preprocessing is good for VAD/other tools
    preprocessed_audio_path = tasks.preprocess_audio(str(input_file))

    # 4. Diarize Speakers
    # NOTE: This step requires a Hugging Face token.
    # It will also chunk the audio and store paths in the segments.
    try:
        segments = tasks.diarize_speakers(str(input_file), config)
    except Exception as e:
        print(f"Critical Error during diarization: {e}")
        print("Pipeline stopped.")
        return

    # 5. Transcribe Segments
    segments = tasks.transcribe_segments(segments, config)

    # 6. Translate Segments
    # NOTE: This step requires Google Cloud credentials.
    segments = tasks.translate_segments(segments, target_language=target_language)

    # 7. Synthesize Speech (TTS)
    # NOTE: This step requires an ElevenLabs API key.
    segments = tasks.synthesize_speech(segments, config, target_language=target_language)

    # 8. Reassemble Audio
    tasks.reassemble_audio(segments, config, target_language=target_language)

    # 9. Generate Transcript and Subtitle Files
    tasks.generate_transcript_file(segments, config, target_language=target_language)
    tasks.generate_subtitle_file(segments, config, target_language=target_language)

    # 10. Generate Final Report
    tasks.generate_report(segments, config)

    end_time = time.time()
    print("\n--- Pipeline Finished ---")
    print(f"Total execution time: {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audio Translation Pipeline")
    parser.add_argument("audio_path", type=str, help="Path to the input audio file.")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to the configuration file.")
    parser.add_argument("--lang", type=str, default="es", help="Target language for translation (e.g., 'es', 'fr', 'de').")

    args = parser.parse_args()

    main(args.audio_path, args.config, args.lang)

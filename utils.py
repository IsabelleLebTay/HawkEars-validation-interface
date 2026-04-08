"""
Shared utilities for HawkEars validation and detection box drawing notebooks.

Functions for audio file lookup, stereo audio loading, and playback.
"""

import pandas as pd
import numpy as np
import librosa
import sounddevice as sd
from pathlib import Path


def parse_audio_filename(filename, sanitize_chars=None, strip_prefixes=None):
    """
    Parse location and datetime from an audio filename.

    Expected format: LocationID_YYYYMMDD_HHMMSS.wav
    Examples:
        UP-2-18-CC_20150609_123117.wav -> ('UP-2-18-CC', '2015-06-09T12:31:17Z')
        SiteName_20240101_060000.wav   -> ('SiteName',   '2024-01-01T06:00:00Z')

    Edit this function if your filenames use a different convention.

    Parameters:
        filename:         Audio filename (e.g. 'Site1_20240101_060000.wav')
        sanitize_chars:   List of characters to replace with '_' before parsing
        strip_prefixes:   List of prefixes to strip from filenames before parsing

    Returns:
        tuple: (location, datetime_str, filename_base) or None if parsing fails
    """
    if sanitize_chars is None:
        sanitize_chars = []
    if strip_prefixes is None:
        strip_prefixes = []

    try:
        name = filename
        for char in sanitize_chars:
            name = name.replace(char, '_')
        for prefix in strip_prefixes:
            name = name.replace(prefix, '')

        base = name.replace('.wav', '')
        parts = base.split('_')

        if len(parts) < 3:
            return None

        # Last two parts are always date and time
        date_str = parts[-2]
        time_str = parts[-1]

        # Everything before date/time is the location ID
        location = '_'.join(parts[:-2])

        if len(date_str) != 8 or len(time_str) != 6:
            return None

        datetime_str = (
            f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}T"
            f"{time_str[:2]}:{time_str[2:4]}:{time_str[4:6]}Z"
        )

        return location, datetime_str, base

    except Exception:
        return None


def build_audio_file_lookup(audio_dirs, file_lookup_file, force_rebuild=False,
                            sanitize_chars=None, strip_prefixes=None):
    """
    Search audio directories and build a lookup table mapping
    (location, recording_datetime) to file paths on disk.

    Results are cached to file_lookup_file after the first run.
    Set force_rebuild=True to rescan directories.

    Parameters:
        audio_dirs:       List of directory paths containing .wav files
        file_lookup_file: Path to save/load the cached lookup CSV
        force_rebuild:    If True, rescan directories even if cache exists
        sanitize_chars:   Passed to parse_audio_filename()
        strip_prefixes:   Passed to parse_audio_filename()

    Returns:
        DataFrame with columns: location, recording_datetime, filename_base,
                                file_path, file_exists
    """
    if Path(file_lookup_file).exists() and not force_rebuild:
        print(f"Loading existing file lookup from {file_lookup_file}")
        return pd.read_csv(file_lookup_file)

    print("Building audio file lookup table (this may take several minutes)...")

    file_records = []

    for base_dir in audio_dirs:
        base_path = Path(base_dir)
        if not base_path.exists():
            print(f"  Warning: Directory not found: {base_dir}")
            continue

        print(f"  Scanning: {base_dir}")

        for wav_file in base_path.rglob('*.wav'):
            parsed = parse_audio_filename(
                wav_file.name,
                sanitize_chars=sanitize_chars,
                strip_prefixes=strip_prefixes
            )
            if parsed is None:
                continue

            location, datetime_str, filename_base = parsed
            file_records.append({
                'location': location,
                'recording_datetime': datetime_str,
                'filename_base': filename_base,
                'file_path': str(wav_file),
                'file_exists': True
            })

    if len(file_records) == 0:
        raise ValueError(
            "No audio files found in the specified directories.\n"
            "Check that audio_dirs points to directories containing .wav files "
            "and that parse_audio_filename() matches your filename convention."
        )

    lookup_df = pd.DataFrame(file_records)
    lookup_df.to_csv(file_lookup_file, index=False)
    print(f"  Found {len(lookup_df)} audio files. Saved to {file_lookup_file}")

    return lookup_df


def load_audio_stereo(file_path, start_time, end_time):
    """
    Load a segment of a stereo audio file and split into left/right channels.

    Parameters:
        file_path:   Path to the .wav file
        start_time:  Start time in seconds
        end_time:    End time in seconds

    Returns:
        tuple: (audio_left, audio_right, sample_rate) or (None, None, None) on error
    """
    try:
        audio, sr = librosa.load(
            file_path, sr=None, mono=False,
            offset=start_time,
            duration=end_time - start_time
        )
        if audio.ndim == 1:
            return audio, audio, sr
        return audio[0], audio[1], sr
    except Exception as e:
        print(f"Error loading audio: {e}")
        return None, None, None


def play_audio(channel, audio_left, audio_right, sr):
    """
    Play audio through sounddevice.

    Parameters:
        channel:      'left', 'right', or 'both'
        audio_left:   Left channel audio array
        audio_right:  Right channel audio array
        sr:           Sample rate
    """
    if sr is None:
        return
    if channel == 'left' and audio_left is not None:
        sd.play(audio_left, sr)
    elif channel == 'right' and audio_right is not None:
        sd.play(audio_right, sr)
    elif channel == 'both' and audio_left is not None and audio_right is not None:
        stereo = np.vstack([audio_left, audio_right]).T
        sd.play(stereo, sr)

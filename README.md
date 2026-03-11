# HawkEars Validation Tool

An interactive Jupyter notebook for rapidly validating [HawkEars](https://github.com/jhuus/HawkEars) acoustic detections.

The tool draws a stratified validation sample across confidence score bins, then presents each detection with dual-channel spectrograms, audio playback, and keyboard shortcuts so you can label detections quickly. Progress is auto-saved and sessions can be resumed.

## Features

- **Stratified sampling** across confidence score bins (0.1 width) for coverage across the full score range
- **Dual spectrogram display** (left/right channel) with adjustable dynamic range and colormap
- **Audio playback** for left, right, or both channels
- **Keyboard shortcuts** (T/F/U/W/B/S) for fast labelling — True Positive, False Positive, Uncertain, Bad Weather, Back, Skip
- **Auto-save** every 20 validations with session resumption
- **Precision summary** by species on completion

## Installation

```
pip install pandas numpy librosa matplotlib sounddevice ipywidgets
```

Runs in JupyterLab or VS Code notebooks.

## Usage

1. Open `hawkears_validation_interface.ipynb`
2. Edit the configuration cell at the top:
   - `HAWKEARS_CSV` — path to your merged HawkEars output CSV
   - `AUDIO_DIRS` — directories containing your .wav files
   - `FOCAL_SPECIES` — species to validate (or `None` to auto-detect all)
   - `SCORE_THRESHOLD` — minimum confidence score to include
   - `VALIDATION_SAMPLES` — number of detections to sample per species
3. Run all cells. The audio file lookup is built once and cached for subsequent runs.
4. Label detections in the interactive interface.
5. Results are saved to `validation_output/validation_results.csv`.

## Input format

The notebook expects a HawkEars output CSV with columns: `filename`, `species`, `confidence`, `start_time`, `end_time`, `location`, `recording_datetime`. Audio filenames should follow the pattern `LocationID_YYYYMMDD_HHMMSS.wav` — edit `parse_audio_filename()` if your naming convention differs.

# HawkEars Validation & Amplitude Extraction Tools

Interactive Jupyter notebooks for validating [HawkEars](https://github.com/jhuus/HawkEars) acoustic detections and drawing bounding boxes around bird songs on spectrograms. Compatible with HawkEars v1.0.

**Upcoming developments:** Update to integrate with HawkEars 2.0.

## Tools included

### 1. Validation Interface (`hawkears_validation_interface.ipynb`)

Interactive validation of HawkEars detections with stratified sampling across confidence score bins.

- **Stratified sampling** across confidence score bins (0.1 width) for coverage across the full score range
- **Dual spectrogram display** (left/right channel) with adjustable dynamic range and colormap
- **Audio playback** for left, right, or both channels
- **Keyboard shortcuts** (T/F/U/W/B/S) for fast labelling — True Positive, False Positive, Uncertain, Bad Weather, Back, Skip
- **Auto-save** every 20 validations with session resumption
- **Precision summary** by species on completion

### 2. Detection Box Drawing (`draw_detection_boxes.ipynb`)

Draw bounding boxes around bird songs on dual-channel spectrograms to record time and frequency coordinates for each detection.

- **Interactive rectangle selector** — click and drag on either spectrogram to draw a box, mirrored on both channels
- **Box coordinate export** — time start/end and frequency min/max saved to CSV
- **Mic exclusion checkboxes** — flag problematic channels per detection
- **Adjustable spectrogram** — dB range and gamma sliders with live refresh
- **Audio playback** for left, right, or both channels
- **Auto-save** every 20 detections with session resumption

Used for amplitude-based distance truncation (Lebeuf-Taylor et al. 2025).

## Requirements

```
pip install -r requirements.txt
```

Runs in JupyterLab or VS Code notebooks. The detection box drawing tool requires `ipympl` for interactive matplotlib (`%matplotlib widget`).

## Usage

### Validation Interface

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

### Detection Box Drawing

1. Open `draw_detection_boxes.ipynb`
2. Edit the configuration cell at the top:
   - `DETECTIONS_CSV` — path to your filtered detections CSV
   - `AUDIO_DIRS` — directories containing your .wav files
   - `FOCAL_SPECIES` — species to process (or `None` for all)
3. Run all cells. Draw bounding boxes around bird songs on the spectrograms.
4. Results are saved to `detection_boxes_output/detection_boxes_results.csv`.

## Input format

Both notebooks expect a HawkEars output CSV with columns: `filename`, `species`, `confidence`, `start_time`, `end_time`, `location`, `recording_datetime`. Audio filenames should follow the pattern `LocationID_YYYYMMDD_HHMMSS.wav` — edit `parse_audio_filename()` in `utils.py` if your naming convention differs.

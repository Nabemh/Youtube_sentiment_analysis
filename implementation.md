# Implementation Notes

This project is largely self-contained, but a few pieces of information must come from you:

## 1. Environment variables (`.env`)
- `YOUTUBE_API_KEY` – Your YouTube Data API v3 key (already created).
- (optional, future) `OPENAI_API_KEY` – if we later add LLM-based utilities.

## 2. Video list for testing / batch runs
Provide a simple text file or CSV with one YouTube `video_id` per line/row, e.g.

```
video_id
Ks-_Mh1QhMc
9bZkp7q19f0
```
Name suggestion: `data/video_ids.csv`.

## 3. Optional configuration overrides (`config.yaml`)
You may tweak defaults such as:
- sentiment chunk length (seconds)
- logistic-regression class thresholds
- paths for raw / processed data

## 4. Python environment
- Ensure `pip install -r requirements.txt` has been executed (done for Phase 1).
- Python ≥ 3.9 recommended.

That’s it – everything else will be created programmatically by the pipeline.

# Nooshpere

Based on [LightRAG](https://github.com/HKUDS/LightRAG)

## Install
* Setup
```sh
poetry update
cp .env.example .env
```
* Change `.env` as you need
* Download [train-00000-of-00001.parquet](https://huggingface.co/datasets/parasail-ai/frames-benchmark-wikipedia/blob/main/data/train-00000-of-00001.parquet) to `import/`
* Download [test.tsv](https://huggingface.co/datasets/google/frames-benchmark/blob/main/test.tsv) to `import/`

## Import
Run `import/import.py`

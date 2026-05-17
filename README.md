## LLM Security Gateway:

A modular security gateway for LLM applications built with Flask and Microsoft Presidio.
It detects prompt injection attacks and anonymizes PII before inputs reach an LLM.

## Features:
- Prompt injection and jailbreak detection
- PII detection and masking using Microsoft Presidio
- 9 custom recognizers for Pakistani and LLM-specific entities
- Policy engine with Allow, Mask, and Block decisions
- Web UI for testing
- Latency measurement

## Installation:
pip install -r requirements.txt
python -m spacy download en_core_web_lg

## How to run it:
python app.py

## Test cases:
Run app.py first, then in a separate terminal:
python test.py

## Web Interface:
Open browser at http://127.0.0.1:5000/ui

#!/bin/bash
terminator -e "bash -c 'source /home/remi/.virtualenvs/whisper/bin/activate && cd /home/remi/voice2chatgpt && python voice_transcriber.py; exec bash'"

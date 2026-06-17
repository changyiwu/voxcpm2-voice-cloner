#!/usr/bin/env python3
"""
webui_record.py - 網頁錄音介面，用瀏覽器麥克風錄製參考音。

自動抓取使用者麥克風，提供錄音/停止按鈕，顯示要朗讀的逐字稿。
錄完自動存到 voices/<名稱>/ref_voice.wav + prompt.txt。

用法：
  python webui_record.py              # 開啟網頁介面（預設 http://127.0.0.1:7860）
  python webui_record.py --port 8080  # 指定 port
"""

import os
import sys
import wave
import argparse
import numpy as np
import gradio as gr

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_RATE = 16000


def load_sample_text():
    """載入預設朗讀文字。"""
    path = os.path.join(REPO_DIR, 'texts', 'sample_text.txt')
    with open(path, 'r', encoding='utf-8') as f:
        return f.read().strip()


def save_recording(audio_path, voice_name, custom_text):
    """
    處理 Gradio 錄音結果：
    1. 讀取瀏覽器錄的音檔
    2. 重取樣為 16kHz 單聲道
    3. 存到 voices/<voice_name>/ref_voice.wav
    4. 逐字稿存到 voices/<voice_name>/prompt.txt
    """
    if audio_path is None:
        return "❌ 尚未錄音，請先按錄音按鈕錄製聲音。", None

    if not voice_name.strip():
        return "❌ 請輸入聲音名稱。", None

    import soundfile as sf

    # 讀取瀏覽器錄音（通常是 44100 或 48000Hz）
    audio, sr = sf.read(audio_path)

    # 轉單聲道
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    # 重取樣到 16kHz（如果需要）
    if sr != SAMPLE_RATE:
        import resampy
        audio = resampy.resample(audio, sr, SAMPLE_RATE)
        sr = SAMPLE_RATE

    # 正規化音量
    peak = np.abs(audio).max()
    if peak > 0:
        audio = audio / peak * 0.95

    # 存檔
    voice_dir = os.path.join(REPO_DIR, 'voices', voice_name.strip())
    os.makedirs(voice_dir, exist_ok=True)

    wav_path = os.path.join(voice_dir, 'ref_voice.wav')
    sf.write(wav_path, audio.astype(np.float32), SAMPLE_RATE)

    # 存逐字稿
    text = custom_text.strip() if custom_text.strip() else load_sample_text()
    prompt_path = os.path.join(voice_dir, 'prompt.txt')
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(text)

    duration = len(audio) / SAMPLE_RATE
    result = (
        f"✅ 錄音完成！\n\n"
        f"  聲音名稱: {voice_name.strip()}\n"
        f"  音檔: {wav_path}\n"
        f"  時長: {duration:.1f}s ({SAMPLE_RATE}Hz)\n"
        f"  逐字稿: {prompt_path}\n\n"
        f"下一步：\n"
        f"  python clone.py \"你想說的文字\" --voice {voice_name.strip()}"
    )
    return result, wav_path


def main():
    parser = argparse.ArgumentParser(description='VoxCPM2 網頁錄音介面')
    parser.add_argument('--port', '-p', type=int, default=7860,
                        help='網頁伺服器 port（預設: 7860）')
    parser.add_argument('--share', action='store_true',
                        help='產生公開連結（Gradio share）')
    args = parser.parse_args()

    sample_text = load_sample_text()

    with gr.Blocks(title='VoxCPM2 Voice Cloner - 錄音') as app:
        gr.Markdown('# 🎙️ VoxCPM2 Voice Cloner - 參考音錄製')
        gr.Markdown('用瀏覽器麥克風錄音，錄完自動存檔，逐字稿自動產生。')

        with gr.Row():
            voice_name_input = gr.Textbox(
                label='聲音名稱',
                placeholder='例：三師爸、三帥媽、我的聲音',
                value='',
                scale=2,
            )
            custom_text_input = gr.Textbox(
                label='朗讀文字（留空用預設文字）',
                placeholder=f'留空則使用預設文字',
                value=sample_text,
                lines=5,
                scale=3,
            )

        gr.Markdown('### 操作步驟')
        gr.Markdown('1. 輸入聲音名稱\n2. 確認要朗讀的文字\n3. 按下方錄音按鈕，對著麥克風朗讀\n4. 錄完按停止\n5. 按「存檔」')

        audio_input = gr.Audio(
            label='麥克風錄音',
            type='filepath',
            sources=['microphone'],
            waveform_options=gr.WaveformOptions(show_recording_waveform=True),
        )

        save_btn = gr.Button('💾 存檔', variant='primary', size='lg')
        result_text = gr.Textbox(label='結果', lines=8, interactive=False)
        playback = gr.Audio(label='預覽錄音', interactive=False)

        save_btn.click(
            fn=save_recording,
            inputs=[audio_input, voice_name_input, custom_text_input],
            outputs=[result_text, playback],
        )

    app.launch(server_port=args.port, share=args.share)


if __name__ == '__main__':
    main()

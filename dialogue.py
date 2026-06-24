#!/usr/bin/env python3
"""
對話生成 — 三師爸與三帥媽的閒聊
模型只載入一次，逐句切換聲音生成，最後拼接成完整對話。
"""
from voxcpm import VoxCPM
import soundfile as sf
import numpy as np
import time
import os
import re

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def get_next_output_path(base_path):
    """
    依據 output 資料夾中其他檔案檔名後三個數字的最大值，
    在基礎檔名上加上最大值+1的序號（格式如 _005）。
    """
    dir_path = os.path.dirname(base_path) or '.'
    os.makedirs(dir_path, exist_ok=True)
    
    max_num = 0
    pattern = re.compile(r'_(\d{3})\.[a-zA-Z0-9]+$')
    
    try:
        for filename in os.listdir(dir_path):
            match = pattern.search(filename)
            if match:
                num = int(match.group(1))
                if num > max_num:
                    max_num = num
    except Exception:
        pass
        
    next_num = max_num + 1
    suffix = f"_{next_num:03d}"
    
    root, ext = os.path.splitext(base_path)
    root = re.sub(r'_\d{3}$', '', root)
    
    return f"{root}{suffix}{ext}"

def detect_device():
    """從 install.ps1 產生的 .gpu_type 讀取，或自動偵測。"""
    gpu_type_file = os.path.join(REPO_DIR, '.gpu_type')
    if os.path.exists(gpu_type_file):
        with open(gpu_type_file, 'r', encoding='utf-8') as f:
            gpu_type = f.read().strip()
    else:
        import torch
        if torch.cuda.is_available():
            gpu_type = 'cuda'
        elif hasattr(torch, 'xpu') and torch.xpu.is_available():
            gpu_type = 'xpu'
        else:
            gpu_type = 'cpu'

    device_map = {'cuda': 'cuda', 'xpu': 'xpu', 'cpu': 'cpu'}
    return device_map.get(gpu_type, 'cpu')

# 對話腳本：(說話者, 文字)
dialogue = [
    ("小吳", "哎呀，老柯啊，聽說最近人工智慧特別火熱。"),
    ("老柯", "那是，大勢所趨嘛。"),
    ("小吳", "可是啊，我發現 AI 再聰明，也有搞不定的事情。"),
    ("老柯", "哦？這我倒想聽聽，有什麼是 AI 搞不定的？"),
    ("小吳", "比如啊，AI 就沒辦法幫你付房租！"),
    ("老柯", "廢話！那得花真金白銀！"),
    ("小吳", "還有啊，AI 也沒辦法替你去上班打卡。"),
    ("老柯", "那當然了，替我打卡我不就失業了嘛。"),
    ("小吳", "所以說啊，這人工智慧，其實就是個聽話的代碼。"),
    ("老柯", "說得對，到頭來，還是我們寫代碼的人最厲害！"),
]

def load_voice(voice_name):
    """讀取指定聲音的參考音與逐字稿。"""
    voice_dir = os.path.join(REPO_DIR, "voices", voice_name)
    ref_wav = os.path.join(voice_dir, "ref_voice.wav")
    prompt_file = os.path.join(voice_dir, "prompt.txt")
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_text = f.read().strip()
    return ref_wav, prompt_text

def main():
    device = detect_device()
    print(f"裝置: {device}")
    print("載入 VoxCPM2 模型...")
    t0 = time.time()
    model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False, device=device, optimize=False)
    print(f"模型載入完成，耗時 {time.time()-t0:.1f}s\n")

    # 預載兩個聲音的參考資料
    voices = {}
    for name in ["小吳", "老柯"]:
        voices[name] = load_voice(name)
        print(f"  已載入聲音: {name}")

    print(f"\n開始生成對話（{len(dialogue)} 句）...\n")

    clips = []
    for i, (speaker, text) in enumerate(dialogue, 1):
        ref_wav, prompt_text = voices[speaker]
        print(f"[{i}/{len(dialogue)}] {speaker}: {text}")

        t1 = time.time()
        wav = model.generate(
            text=text,
            prompt_wav_path=ref_wav,
            prompt_text=prompt_text,
            reference_wav_path=ref_wav,
            cfg_value=1.5,
            inference_timesteps=10,
        )
        elapsed = time.time() - t1
        duration = len(wav) / model.tts_model.sample_rate
        print(f"        -> {duration:.1f}s ({elapsed:.1f}s)")

        # 句子之間加 0.4 秒停頓
        pause = np.zeros(int(0.4 * model.tts_model.sample_rate), dtype=wav.dtype)
        clips.append(wav)
        clips.append(pause)

    # 拼接所有片段
    full_audio = np.concatenate(clips)
    total_duration = len(full_audio) / model.tts_model.sample_rate
    base_output = os.path.join(REPO_DIR, "output", "dialogue_小吳_老柯.wav")
    output_path = get_next_output_path(base_output)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    sf.write(output_path, full_audio, model.tts_model.sample_rate)

    print(f"\n對話生成完成！")
    print(f"  總長度: {total_duration:.1f}s")
    print(f"  檔案: {output_path}")

if __name__ == "__main__":
    main()

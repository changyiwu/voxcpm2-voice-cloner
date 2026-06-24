# Antigravity - VoxCPM2 Voice Cloner 專案規則

## 專案概要
*   **名稱**：VoxCPM2 Voice Cloner
*   **用途**：使用 VoxCPM2 進行語音克隆與對話生成
*   **架構**：本機執行，使用 Python 3.12 虛擬環境與 Gradio WebUI

## 開發規則與命令說明
1.  **環境執行**：
    *   虛擬環境路徑：`.\.venv\Scripts\python.exe`
2.  **腳本工具**：
    *   克隆語音：`python clone.py "文字" --voice <名稱>`
    *   生成對話：編輯對話清單後，執行 `python dialogue.py`
    *   啟動錄音 UI：`python app.py`
3.  **檔名自動遞增規則**：
    *   `clone.py` 與 `dialogue.py` 輸出檔名會自動搜尋 `output/` 目錄中最大序號並自增（如 `_005.wav`）。
4.  **GPU 支援**：
    *   程式自動偵測硬體，支援 NVIDIA CUDA、Intel XPU (Arc) 與 CPU。

## 提交規範
*   個人錄音 `voices/` 與生成的語音 `output/` 被 `.gitignore` 排除，絕不上傳至 Git/GitHub。

# VoxCPM2 Voice Cloner — Agent 使用指南

本專案提供 VoxCPM2 語音生成工具，專為 AI Agent 設計。

## 工具清單

| 工具 | 用途 | 呼叫方式 |
|------|------|---------|
| `clone.py` | 用已錄聲音生成語音 | `python clone.py "文字" --voice <名稱>` |
| `dialogue.py` | 多聲音對話 | 編輯腳本後 `python dialogue.py` |
| `app.py` | 錄音 UI（給人類用） | `python app.py` → http://127.0.0.1:7860 |

## Agent 應知道的事

1. **查聲音**：`ls G:\我的雲端硬碟\2026Agents\voxcpm2-voice-cloner\voices\`
2. **生成**：`& "C:\Users\mathr\voxcpm\Scripts\python.exe" "G:\我的雲端硬碟\2026Agents\voxcpm2-voice-cloner\clone.py" "要說的文字" --voice <名稱>`
3. **輸出**：`output/cloned_voice.wav`（在專案目錄下）
4. **模型**：`openbmb/VoxCPM2`（Apache-2.0，可商用）
5. **裝置**：Intel Arc 140T（XPU），RTF ~3-4x
6. **錄新聲音**：引導使用者打開 `http://127.0.0.1:7860`

## 使用者自然語言對照

| 使用者指令 | Agent 動作 |
|-----------|-----------|
| 「用OOO的聲音說XXX」 | `clone.py "XXX" --voice OOO` |
| 「讓A和B對話」 | 編輯 `dialogue.py` + 執行 |
| 「有哪些聲音」 | `ls voices/` |
| 「我要錄聲音」 | 引導 `http://127.0.0.1:7860` |

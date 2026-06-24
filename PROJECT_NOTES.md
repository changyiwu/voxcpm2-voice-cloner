# 專案筆記 (Project Notes)

## 目前進度
- [x] 自動環境安裝（已完成，支援 NVIDIA CUDA GPU 偵測與加速）。
- [x] 修復 README.md 排版與編號錯位問題。
- [x] 修正 app.py 錄音 UI 的配色，確保亮色與暗色模式下的朗讀字體清晰可見。
- [x] 實作「後三個數字最大 + 1」的新檔名自動遞增規則，並套用於 `clone.py` 與 `dialogue.py`。
- [x] 修正 `dialogue.py` 原本寫死的 `device="xpu"` Bug，改為動態偵測。
- [x] 成功以「小吳」和「老柯」聲音生成笑話與雙口相聲音檔。

## 下一步 (Next Steps)
- 初始化 Git 本地專案，並發布至公開的 GitHub 儲存庫。
- 專案整理與交付。

## 踩坑記錄 (Lessons Learned)
- **PowerShell 執行編碼問題**：在中文路徑下直接執行無 BOM 的 UTF-8 腳本可能會被解碼為 Big5 導致語法解析出錯。使用 `Get-Content -Encoding UTF8` 可以解決此問題。
- **Gradio 6.0 樣式相容**：Gradio 的暗色模式會為 `body` 加上 `.dark` 類別，如果直接寫死 inline style 背景而不給定字體顏色，會導致暗色模式下白字與亮底色對疊無法看清。使用 CSS Class 配合 `var()` 與 `.dark` 特化可以完美相容雙色模式。
- **Gradio launch warnings**：在 Gradio 6.0 中，`css` 參數應由 `gr.Blocks(css=...)` 移至 `.launch(css=...)`。

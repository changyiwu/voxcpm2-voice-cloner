@agents.md

<!--
  本檔是「橋接檔」：Claude Code 只讀 CLAUDE.md，不讀 agents.md，
  所以用第一行的 @agents.md 把跨 Agent 專案藍圖 import 進來。
  專案內容一律寫進 agents.md，這裡只放 Claude Code 專屬規範，避免兩份分叉。
-->

## Claude Code 專屬

- 執行 `record_ui.py` 或任何伺服器時用背景執行，用完記得停掉並確認 port 已釋放。
- 生成語音後用 SendUserFile 把音檔交給使用者試聽，不要只回報路徑。

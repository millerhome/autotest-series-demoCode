# 自動化測試系列課程｜課綱（12 堂 × 約 50 分鐘）

依《自動化測試教育訓練｜課程需求說明書 v2.0》的 M0–M8 模組拆成 12 堂影片。
風格延續 `test-engineer-course.mp4`；旁白 edge-tts `zh-TW-HsiaoChenNeural`（女聲、台灣口音，專有名詞唸英文）。

| 課 | 主題 | 模組 | 實戰範例 | 狀態 |
|---|---|---|---|---|
| 1 | 觀念與策略 | M0 | 第一支 Pytest、API 測試、UI 測試、marker 分組、流程評分與回本試算 | ✅ 已完成 |
| 2 | 給 .NET 工程師的 Python | M1 | C# 對照語法、venv、requirements.txt、專案結構、資料驅動的保費規則 | ✅ 已完成 |
| 3 | Pytest 核心 | M1 | assert、pytest.raises、fixture、parametrize、marker、conftest、讀失敗訊息、常用指令 | ✅ 已完成 |
| 4 | 服務層測試（一）HTTP / JSON API | M2 | requests、Session 與登入 fixture、JSON Schema 驗證、錯誤情境、流程測試 | ✅ 已完成 |
| 5 | 服務層測試（二）SOAP / WSDL | M2 | SOAP 信封與 WSDL、zeep、SOAP Header 登入、Fault 測試、流程測試、WSDL 快照比對 | ✅ 已完成 |
| 6 | 測試資料與資料庫驗證 | M3 | SQL 驗證落地資料、工廠 fixture、Faker 假資料、清掃與交易回滾、CSV 案例、去識別化（以 SQLite 示範） | ✅ 已完成 |
| 7 | Playwright 基礎 | M4 | locator、表單與對話框操作、auto-wait 與 expect、登入狀態重複使用、API 準備資料、截圖與 trace | ✅ 已完成 |
| 8 | Page Object 與 WebForms／Blazor | M4 | Page Object 與元件、id 結尾定位、postback 與 UpdatePanel 的等待、Blazor 互動時機（以模擬網站示範） | ✅ 已完成 |
| 9 | Allure 測試報告 | M5 | 標題與分組、step、attachment 與失敗截圖、分類、歷史、品質卡點、單一檔案報告（以 Allure 3 示範） | ✅ 已完成 |
| 10 | 執行機與過版測試流程 | M6 | 環境登記檔與白名單、唯讀環境兩道防線、機密管理、pytest-xdist、過版前回歸／過版後冒煙的執行腳本（工作排程器未實測） | ✅ 已完成 |
| 11 | 與 GitHub Copilot 協作 | M7 | 提示寫法、指示檔、審查 AI 產生的測試、故意放缺陷驗證、content exclusion（AI 測試為講師整理的示範） | ✅ 已完成 |
| 12 | 維運治理與推廣 | M8 | 不穩定測試的偵測、隔離與修正、失敗分流、Definition of Done、指標、推廣路線圖、系列總結 | ✅ 已完成 |

## 每堂課的固定結構

開場（目標、地圖、資料來源）→ 觀念 → 逐步實作（畫面上的輸出皆為實際執行結果）→ 小測驗 → 動手練習 → 重點回顧 → 下一課預告 → 參考資料。

## 資料來源原則

官方文件、期刊與研討會論文、電子書，以及超過 1000 星的 GitHub 專案；每堂課片尾列出完整清單。

## 專案結構

- `src/lessons/lNN.ts`：每堂課的腳本（場景與旁白）
- `demo/lessonNN/`：該堂課可直接執行的範例程式
- `out/`：轉譯完成的影片
- `../autotest-series-tools/gen-audio.mjs`：產生旁白語音

## 本機無法實跑、需以替代環境示範的部分

Hyper-V 執行機、ASP.NET WebForms／Blazor 站台、Oracle／SQL Server、GitHub Copilot 組織版。
相關課次（6、8、10、11）會以本機可執行的替代範例示範，並在影片中標明哪些步驟需在公司環境驗證。

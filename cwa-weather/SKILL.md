---
name: cwa-weather
description: 用中央氣象署（CWA）開放資料 API 查各縣市與鄉鎮的天氣預報（天氣現象、降雨機率、氣溫、舒適度）。天氣、天氣預報、氣溫、降雨機率、明天天氣、週末天氣、台北天氣、高雄天氣的問題適用。需要在 opendata.cwa.gov.tw 免費申請的 API 金鑰。颱風警報、豪雨特報、地震速報不適用（請看中央氣象署官網）;沒有金鑰時改用 taiwan-weather（Open-Meteo 免金鑰）。
license: MIT
metadata:
  category: weather
  locale: zh-TW
---

# cwa-weather

用中央氣象署（CWA）開放資料平臺（opendata.cwa.gov.tw）查正式天氣預報。**這是官方資料**，正式預報優先用這裡;免金鑰備援是 `taiwan-weather`（Open-Meteo）。

**需要 API 金鑰（免費、即時發給）:** 到 https://opendata.cwa.gov.tw 註冊會員，登入後在「會員專區」即可看到授權碼。沒有金鑰時呼叫會回 `401 Forbidden: Authorization key is not correct.`（2026-09-09 實測）。使用者沒有金鑰時，請改用 `taiwan-weather` 或引導使用者申請，不要編造預報內容。

颱風動態、豪雨特報、各種警報、地震速報**不在本技能範圍**，一律以中央氣象署 https://www.cwa.gov.tw 為準。

## 基本流程

1. 請使用者提供 CWA 授權碼（或確認環境中已有）
2. 依需求選資料集:縣市 36 小時預報，或鄉鎮逐區預報
3. 帶 `Authorization` 參數呼叫，解析 JSON

### 1. 縣市 36 小時預報（F-C0032-001）

```bash
curl -sm 30 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=<授權碼>&locationName=臺北市' -o /tmp/cwa.json
```

- 一次最多查多個縣市:`locationName=臺北市,新北市`;不帶則回全部縣市。
- 回傳 JSON（預設;`&format=XML` 可換 XML）。結構:`records.location[]`，每縣市含 `locationName` 與 `weatherElement[]`:`Wx`（天氣現象）、`PoP`（降雨機率 %）、`MinT`（最低溫）、`CI`（舒適度）、`MaxT`（最高溫），各元素 `time[]` 內有 `startTime`/`endTime`/`parameter.parameterName`。

### 2. 鄉鎮預報（F-D0047 系列）

每個縣市有各自的 dataset id（`F-D0047-xxx`，一週逐 12 小時或 3 小時鄉鎮預報）。到 https://opendata.cwa.gov.tw 資料目錄搜尋「鄉鎮天氣預報」確認目標縣市的 id，呼叫方式相同:

```bash
curl -sm 30 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/<F-D0047-xxx>?Authorization=<授權碼>&locationName=<鄉鎮市區名>'
```

### 實測記錄

2026-09-09 實測:未帶金鑰與帶無效金鑰呼叫 `F-C0032-001` 皆回 `401 Forbidden: Authorization key is not correct.`。**本技能未持有效金鑰做端到端實測**;端點、參數與回傳結構依 CWA 開放資料平臺官方文件（https://opendata.cwa.gov.tw 的 API 文件與資料集說明頁）。首次實際使用時，若回傳結構與上述不符，以實際回傳為準並回報差異。

## 錯誤與失敗時的處理

- **401 / Authorization key is not correct**:沒有金鑰或金鑰錯誤。請使用者到 opendata.cwa.gov.tw 會員專區確認授權碼;使用者不想申請就改用 `taiwan-weather`。
- **連線逾時 / 5xx**:`curl` 一律加 `-m 30`，重試 1~2 次;仍失敗就告知 CWA 開放資料平臺可能暫時異常，正式預報請看 https://www.cwa.gov.tw。不要編造天氣。
- **回傳不是 JSON 或 `success` 為 false**:視為失敗，如實回報回傳訊息，不要用舊資料冒充。
- **颱風、警報、地震相關問題**:本技能不提供。直接請使用者看中央氣象署官網或 App。
- **金鑰是秘密**:不要把授權碼寫進回覆、文件或提交紀錄;範例一律用 `<授權碼>` 占位。


## 警特報、颱風與地震

本技能只涵蓋一般天氣預報。颱風動態、豪雨特報、各種警報與地震速報:

- **免金鑰**:用 taiwan-weather 技能裡的 NCDR CAP 公開 feed（國家災害防救科技中心彙整的官方警報,含颱風、地震、海嘯、淹水等類型,2026-09-09 實測可用）。
- CWA 官網的警報頁有 Bot 防護（2026-09-09 實測從一般網路連線回 403）,不適合程式查詢。
- CWA 開放資料平台另有警特報相關資料集（同樣用本技能的授權碼呼叫）,但截至 2026-09-09 未逐一實測;要使用時請先到 https://opendata.cwa.gov.tw 資料目錄確認資料集 id 再實測,不要直接引用未驗證的 id。

正式警報內容一律以中央氣象署公告為準。

## Open-Meteo（taiwan-weather）vs 本技能怎麼選

有授權碼時正式預報優先用本技能（官方資料、鄉鎮級）;手邊沒金鑰或只要快速概況時用 taiwan-weather（Open-Meteo,國際模式,可能與官方預報有落差）。兩者的警報查詢都走 taiwan-weather 的 NCDR CAP 段。

## English summary

Queries official weather forecasts (36-hour per-county via F-C0032-001， township forecasts via the F-D0047 series) from Taiwan's Central Weather Administration open-data platform. Requires a free, instantly issued API key from opendata.cwa.gov.tw - keyless and bad-key calls return 401 (verified 2026-09-09; no end-to-end test with a real key yet, so the response layout follows the official docs). For typhoons, heavy-rain advisories, warnings, and earthquake reports, use the keyless NCDR CAP feeds documented in taiwan-weather (the CWA website is bot-protected; verified 403 on 2026-09-09) - official announcements remain at https://www.cwa.gov.tw. Without a key, fall back to the keyless taiwan-weather (Open-Meteo) skill. Never echo the user's key into replies or commits.

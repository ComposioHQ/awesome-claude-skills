---
name: youbike-realtime
description: 查全台 14 個服務區(台北、新北、桃園、台中、台南、高雄等)YouBike 2.0 站點的即時可借車輛與可還空位,含電輔車篩選與最近站點查詢。YouBike、微笑單車、公共自行車、借車、還車、站點、哪裡有車的問題適用。免 API 金鑰、免登入。預約租車、費用計算不適用。
license: MIT
metadata:
  category: transport
  locale: zh-TW
---

# youbike-realtime

查 YouBike 2.0 站點即時狀態:可借幾台、可還幾個空位。免 API 金鑰,`curl` + `jq` 即可。

**兩層資料源**,優先用第 1 層:

1. **官方統一 feed(全台 14 個服務區)**:youbike.com.tw 地圖實際使用的即時 JSON,一次取回全台約 9,500 站(2026-09-10 實測 9,521 站),含高雄、台南等市政府開放平台沒有的縣市,且每站都有電輔車明細。注意:這是**非公開文件化的 API**,欄位可能無預警調整,所以第 2 層保留作為備援。
2. **各市政府開放資料 feed(台北、新北、台中、桃園)**:文件化的官方開放資料,統一 feed 失敗或欄位變更時改用。**高雄市政府的來源(openapi.kcg.gov.tw)2026-09-09 從台灣境外連線逾時、無法驗證,不要依賴**;高雄請用統一 feed。

回報時一律附上資料更新時間,讓使用者知道資訊有多新。

## 第 1 層:官方統一 feed(apis.youbike.com.tw)

```bash
curl -sm 60 https://apis.youbike.com.tw/json/station-yb2.json -o /tmp/youbike_all.json
```

2026-09-10 實測:HTTP 200、約 6.2MB、9,521 站、14 個服務區,回應內 `updated_at` 與查詢時刻差約 1 分鐘(近即時)。檔案大,短時間內重複查詢請用同一份快取(1~2 分鐘),不要連續請求。

### 欄位

| 欄位 | 意義 |
| --- | --- |
| `area_code` | 服務區代碼(字串,見下表;`"0A"` 等含英字,比對時當字串) |
| `status` | `1` = 營運中,`2` = 暫停營運 |
| `station_no` | 站點編號 |
| `name_tw` / `name_en` | 站名(中 / 英;**沒有**市府 feed 的 `YouBike2.0_` 前綴) |
| `district_tw` / `district_en` | 行政區 |
| `address_tw` / `address_en` | 地址 |
| `parking_spaces` | 總車位數(數字) |
| `available_spaces` | 可借車輛數(數字) |
| `available_spaces_detail` | 可借明細 `{yb1, yb2, eyb}`:YouBike 1.0 / 2.0 / 電輔車 |
| `empty_spaces` | 可還空位數(數字) |
| `lat` / `lng` | 站點座標(**字串**,算距離前要 `tonumber`) |
| `updated_at` | 資料更新時間 `YYYY-MM-DD HH:MM:SS`(台灣時間 UTC+8) |

### 服務區代碼(area_code,2026-09-10 實測)

| 代碼 | 服務區 | 約略站數 | 代碼 | 服務區 | 約略站數 |
| --- | --- | --- | --- | --- | --- |
| `00` | 台北市 | 1,800 | `0B` | 新竹縣 | 210 |
| `05` | 新北市 | 1,600 | `10` | 新竹科學園區 | 40 |
| `07` | 桃園市 | 700 | `11` | 嘉義縣 | 190 |
| `01` | 台中市 | 1,820 | `12` | 高雄市 | 1,500 |
| `13` | 台南市 | 760 | `14` | 屏東縣 | 190 |
| `08` | 嘉義市 | 220 | `15` | 台東縣 | 120 |
| `09` | 新竹市 | 150 | `0A` | 苗栗縣 | 220 |

### 查詢範例

```bash
# 高雄新興區有車可借的站(統一 feed 才有高雄)
jq -r '.[] | select(.area_code=="12" and .district_tw=="新興區" and .status==1 and .available_spaces>0)
  | "\(.name_tw) 可借\(.available_spaces) 可還\(.empty_spaces)"' /tmp/youbike_all.json

# 台北找電輔車(市府 feed 沒有電輔車欄位,統一 feed 的 eyb 全台通用)
jq -r '.[] | select(.area_code=="00" and .status==1 and .available_spaces_detail.eyb>0)
  | "\(.name_tw) 電輔車\(.available_spaces_detail.eyb) 可還\(.empty_spaces)"' /tmp/youbike_all.json

# 雙北邊界一次查(area_code 00+05),不用分兩支 feed 再合併
jq -r '.[] | select((.area_code=="00" or .area_code=="05") and .status==1 and .available_spaces>0
        and (.name_tw | gsub("臺";"台") | contains("台大")))
  | "\(.name_tw) 可借\(.available_spaces)"' /tmp/youbike_all.json

# 找離指定座標最近且有車的 5 站(以緯度 25.033、經度 121.565 為例;lat/lng 是字串)
jq -r --argjson la 25.033 --argjson lo 121.565 '
  [.[] | select(.status==1 and .available_spaces>0)
   | . + {d: (((.lat|tonumber)-$la)*((.lat|tonumber)-$la) + ((.lng|tonumber)-$lo)*((.lng|tonumber)-$lo))}]
  | sort_by(.d) | .[0:5][]
  | "\(.name_tw) 可借\(.available_spaces) 可還\(.empty_spaces) \(.address_tw)"' /tmp/youbike_all.json
```

## 站名「台 / 臺」正規化(重要)

站名混用「台」與「臺」:台北市府 feed 有 147 站用「臺」(2026-09-10 實測),新北兩者混用(「臺」27 站、「台」18 站),統一 feed 全台共 385 站名含「臺」。使用者打「台大」時,名叫「臺大」的站會全部漏掉。**搜尋站名前先把站名與關鍵字都正規化**:

```bash
# haystack 與 needle 都 gsub("臺";"台") 再比對
jq -r --arg q '台大' '.[] | select(.name_tw | gsub("臺";"台") | contains($q | gsub("臺";"台"))) | .name_tw' /tmp/youbike_all.json
```

## 第 2 層:各市政府開放資料 feed(備援)

統一 feed 連不上或欄位變更時改用。**四個城市的 feed 欄位命名分兩派**,不要混用 jq 篩選式:

- 台北派:`available_rent_bikes` / `available_return_bikes` / `Quantity`(數字型)
- 其他三市派:`sbi` / `bemp` / `tot`(字串型;新北另叫 `sbi_quantity` / `bemp` / `tot_quantity`)

### 台北市

```bash
curl -sm 30 https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json -o /tmp/youbike.json
```

2026-09-10 實測:HTTP 200、約 940KB、約 1,800 站,約 1 分鐘更新一次。**台北 feed 沒有電輔車欄位**,要篩電輔車請用統一 feed 的 `available_spaces_detail.eyb`。

| 欄位 | 意義 |
| --- | --- |
| `sno` | 站點編號 |
| `sna` / `snaen` | 站名(中文 / 英文,帶 `YouBike2.0_` 前綴) |
| `sarea` / `sareaen` | 行政區(中文 / 英文) |
| `ar` / `aren` | 地址(中文 / 英文) |
| `Quantity` | 總車位數 |
| `available_rent_bikes` | 可借車輛數 |
| `available_return_bikes` | 可還空位數 |
| `act` | `1` = 營運中,其他 = 暫停營運 |
| `latitude` / `longitude` | 站點座標 |
| `srcUpdateTime` / `mday` | 資料更新時間 |

```bash
# 大安區還有車可借的站
jq -r '.[] | select(.sarea=="大安區" and .act=="1" and .available_rent_bikes>0)
  | "\(.sna) 可借\(.available_rent_bikes) 可還\(.available_return_bikes)"' /tmp/youbike.json
```

### 新北市(data.ntpc.gov.tw)

```bash
curl -sm 30 'https://data.ntpc.gov.tw/api/datasets/010E5B15-3823-4B20-B401-B1CF000550C5/json?page=0&size=5000' -o /tmp/youbike_ntpc.json
```

2026-09-10 實測:HTTP 200、`size=5000` 一次取回全部約 1,600 站(約 700KB)。分頁參數 `page`(0 起)與 `size`。

欄位對照(新北 → 台北):

| 新北欄位 | 台北欄位 | 意義 |
| --- | --- | --- |
| `sbi_quantity` | `available_rent_bikes` | 可借車輛數 |
| `bemp` | `available_return_bikes` | 可還空位數 |
| `tot_quantity` | `Quantity` | 總車位數 |
| `lat` / `lng` | `latitude` / `longitude` | 站點座標 |
| `act` | `act` | `1` = 營運中 |
| `mday` | `mday` | 資料更新時間 |
| `yb2_quantity` / `eyb_quantity` | (無) | 可借中一般車 / 電輔車數 |

```bash
# 板橋區還有電輔車可借的站
jq -r '.[] | select(.sarea=="板橋區" and .act=="1" and (.eyb_quantity|tonumber)>0)
  | "\(.sna) 電輔車\(.eyb_quantity) 一般\(.yb2_quantity) 可還\(.bemp)"' /tmp/youbike_ntpc.json
```

注意:新北 feed 的數量欄位是字串(`"9"` 不是 `9`),比較前用 `tonumber`。

### 台中市(newdatacenter.taichung.gov.tw)

```bash
curl -sm 30 'https://newdatacenter.taichung.gov.tw/api/v1/no-auth/resource.download?rid=9468c0d0-e1ed-4ecc-a86f-ab5a9fd590ff' -o /tmp/youbike_tc.json
```

2026-09-10 實測:HTTP 200、約 750KB、約 1,820 站、一次全量下載不分頁。

### 桃園市(opendata.tycg.gov.tw)

```bash
curl -sm 30 'https://opendata.tycg.gov.tw/api/v1/dataset.api_access?rid=08274d61-edbe-419d-8fcc-7a643831283d&format=json&limit=2000' -o /tmp/youbike_ty.json
```

2026-09-10 實測:HTTP 200;**不帶 `limit` 只回 20 站**,帶 `limit=2000` 取回全部約 700 站。**注意:若回傳筆數正好等於 `limit`,代表可能被截斷,把 `limit` 加大再查一次**。

### 台中 / 桃園的共同欄位

兩市 feed 欄位命名相同(與新北不同):

| 欄位 | 意義 |
| --- | --- |
| `scity` / `scityen` | 城市(中文 / 英文) |
| `sna` / `snaen` | 站名(中文 / 英文) |
| `sarea` / `sareaen` | 行政區 |
| `ar` / `aren` | 地址 |
| `sno` | 站點編號 |
| `tot` | 總車位數(字串) |
| `sbi` | 可借車輛數(字串) |
| `bemp` | 可還空位數(字串) |
| `lat` / `lng` | 站點座標(字串) |
| `act` | `1` = 營運中 |
| `mday` | 資料更新時間 `YYYYMMDDHHMMSS` |
| `sbi_detail` | 可借明細:**台中是 `"14,1"`(一般,電輔),桃園是 JSON 字串 `{"yb2":"14","eyb":"1"}`**,兩市格式不同 |

```bash
# 台中西區有可借車的站
jq -r '.[] | select(.sarea=="西區" and .act=="1" and (.sbi|tonumber)>0)
  | "\(.sna) 可借\(.sbi) 可還\(.bemp)"' /tmp/youbike_tc.json

# 桃園找有電輔車的站(sbi_detail 是 JSON 字串,要 fromjson)
jq -r '.[] | select(.act=="1" and ((.sbi_detail|fromjson|.eyb|tonumber) // 0) > 0)
  | "\(.sna) 電輔車\(.sbi_detail|fromjson|.eyb) 可還\(.bemp)"' /tmp/youbike_ty.json
```

### 雙北合併查詢(市府 feed 版)

統一 feed 用 `area_code` 一次解決;若只能做市府 feed,分別下載後用 `jq -s add` 合併,但因兩市欄位不同,先各自正規化成共同欄位再合併:

```bash
jq -sr '
  (.[0] | map({sna, rent: .available_rent_bikes, ret: .available_return_bikes, act, lat: .latitude, lng: .longitude})) +
  (.[1] | map({sna, rent: (.sbi_quantity|tonumber), ret: (.bemp|tonumber), act, lat: (.lat|tonumber), lng: (.lng|tonumber)}))
  | .[] | select(.act=="1" and .rent>0) | "\(.sna) 可借\(.rent) 可還\(.ret)"' /tmp/youbike.json /tmp/youbike_ntpc.json
```

## 更新時間欄位格式(各市不同,全部為台灣本地時間 UTC+8)

| 來源 | 欄位 | 格式範例 |
| --- | --- | --- |
| 統一 feed | `updated_at` | `2026-09-10 03:26:31` |
| 台北 | `mday` / `infoTime` / `srcUpdateTime` / `updateTime` | `2026-09-10 03:25:04`(`infoDate` 另給日期) |
| 新北 | `mday` | `20260910T032403` |
| 台中 / 桃園 | `mday` | `20260910032603` |

## 錯誤與失敗時的處理

- **連線逾時 / 5xx**:`curl` 一律加 `-m 30`(統一 feed 用 `-m 60`),隔幾秒重試 1~2 次。
- **統一 feed 失敗**:改用第 2 層市府 feed(雙北台中桃園);其他縣市則告知統一 feed 暫時異常,建議 YouBike 官方 App 或 https://www.youbike.com.tw 確認。
- **市府 feed 失敗**:統一 feed 還正常時直接用統一 feed 頂替;兩層都失敗就告知公開資料源可能暫時異常。
- **回傳空陣列或不是 JSON**:視為失敗,不要用舊資料冒充即時資料。
- **`status` / `act` 不是營運中**:該站暫停營運,明確告知,不要只回報 0 台可借。
- **數量為 0**:如實回報「目前無車可借 / 無位可還」,數量變動很快,建議出發前再查一次。
- **桃園只查到 20 站**:忘了帶 `limit` 參數。預設只回 20 筆,全量約 700 站要 `limit=2000`(2026-09-10 實測);回傳筆數等於 `limit` 時要加大再查。
- **`sbi_detail` 格式**:台中是逗號字串 `一般,電輔`,桃園是 JSON 字串。桃園要 `fromjson` 再取值;台中用 `split(",")`。
- **站名搜不到**:先想「台 / 臺」問題,兩邊都 `gsub("臺";"台")` 再比對(見上文)。
- **欄位混用**:四市欄位名分兩派(見開頭說明),統一 feed 又是第三套命名,把台北的 `available_rent_bikes` 套到台中資料會得到空結果,先確認資料源再選篩選式。
- **高雄市**:用統一 feed(`area_code=="12"`)。高雄市政府 openapi.kcg.gov.tw 的 YouBike 端點 2026-09-09 從台灣境外連線逾時、無法驗證,不要依賴。

## English summary

Looks up real-time YouBike 2.0 availability nationwide in Taiwan (no API key; `curl` + `jq`). Two tiers: (1) the official unified feed at apis.youbike.com.tw/json/station-yb2.json - one call returns ~9,500 stations across 14 service areas including Kaohsiung and Tainan, with per-type bike detail (`available_spaces_detail` = {yb1, yb2, eyb}) and near-real-time `updated_at`; it is the feed the official map uses but is undocumented, so schema may change without notice. (2) Per-city open-data feeds (Taipei, New Taipei, Taichung, Taoyuan) as documented fallback - Taipei has no e-bike field, so use the unified feed for e-bike filtering. Field names split into families: Taipei numeric `available_rent_bikes`/`available_return_bikes`, other cities string-typed `sbi`/`bemp`/`tot` (New Taipei: `sbi_quantity`/`tot_quantity`), unified feed `available_spaces`/`empty_spaces`. Station names mix 台/臺 (147 Taipei stations use 臺) - normalize both sides with `gsub("臺";"台")` before matching. Taoyuan paginates at 20 rows unless you pass `limit=2000` (~700 stations); if the count equals the limit, raise it and requery. Update-time formats differ per city (`YYYY-MM-DD HH:MM:SS` Taipei/unified, `YYYYMMDDTHHMMSS` New Taipei, `YYYYMMDDHHMMSS` Taichung/Taoyuan), all Taiwan local time (UTC+8). Always quote the feed's update time, cache responses for 1-2 minutes instead of polling, and treat non-JSON or empty responses as failures - never pass stale data off as live.

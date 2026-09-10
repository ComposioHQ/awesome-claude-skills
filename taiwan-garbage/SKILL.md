---
name: taiwan-garbage
description: 查台北市與新北市的垃圾車清運點、路線與停靠時間。垃圾車、倒垃圾、垃圾時間、清運點、資源回收車、幾點來、今天有沒有收垃圾的問題適用。免登入,台北用臺北市資料大平臺 CSV,新北用新北市資料開放平臺 JSON。其他縣市尚未支援;是計畫停靠時間,不是即時 GPS。
license: MIT
metadata:
  category: city
  locale: zh-TW
---

# taiwan-garbage

查垃圾車清運點與停靠時間。台北市用 data.taipei 的 CSV,新北市用 data.ntpc.gov.tw 的 JSON API,都免登入、免 API 金鑰。兩市資料格式完全不同,見各自章節。

## 基本流程

1. 依城市下載對應資料
2. 依行政區、里別、地址或經緯度篩選
3. 用現在時間(Asia/Taipei)找出「下一班車」;新北資料可再依星期幾判斷「今天有沒有收」

## 台北市(data.taipei CSV)

### 1. 下載

```bash
curl -sLm 30 'https://data.taipei/api/dataset/6bb3304b-4f46-4bb0-8cd1-60c66dcd1cae/resource/a6e90031-7ec4-4089-afb5-361a4efe7202/download' -o /tmp/tpe_garbage.csv
```

2026-09-09 實測:HTTP 200、`text/csv`、約 550KB、UTF-8(有 BOM)。這是計畫停靠時間的靜態路線資料,不是即時 GPS;每次使用重新下載即可。

**下載連結的 resource id 可能更換。** 若 404,打開資料集頁 https://data.taipei/dataset/detail?id=6bb3304b-4f46-4bb0-8cd1-60c66dcd1cae ,在頁面原始碼找 `/api/dataset/<資料集id>/resource/<新的resource id>/download` 形式的連結替換。

### 2. 欄位

```
行政區,里別,分隊,局編,車號,路線,車次,抵達時間,離開時間,地點,經度,緯度
```

- `抵達時間` / `離開時間` 是 `HHMM` 字串(例如 `1630` = 16:30)。
- 一個里可能有多個清運點、多個車次。
- `經度` / `緯度` 可拿來算離指定座標最近的清運點。

### 3. 查詢範例

```bash
# 去掉 BOM 後,查某個里的所有清運點
sed '1s/^\xef\xbb\xbf//' /tmp/tpe_garbage.csv > /tmp/g.csv
awk -F',' '$2=="天壽里" {print $10, "抵達", $8, "離開", $9, "(" $6 " " $7 ")"}' /tmp/g.csv

# 找出大安區今天 18:00 之後還會到的點(時間是 HHMM 字串,可直接比字串)
awk -F',' '$1=="大安區" && $8>="1800" {print $2, $10, "抵達", $8}' /tmp/g.csv | sort -t' ' -k3

# 找離指定座標最近的 5 個清運點(以緯度 25.033、經度 121.565 為例)
awk -F',' -v la=25.033 -v lo=121.565 'NR>1 {
  d=($12-la)*($12-la)+($11-lo)*($11-lo); printf "%.8f %s %s %s 抵達%s\n", d, $1, $2, $10, $8
}' /tmp/g.csv | sort -n | head -5
```

「下一班車」的做法:把現在時間(Asia/Taipei)轉成 `HHMM`,篩出同里且 `抵達時間` 大於現在的列,取最早的一班,回報地點、抵達時間、路線與車次。

## 新北市(data.ntpc.gov.tw JSON)

### 1. 下載(分頁)

```bash
curl -sm 30 'https://data.ntpc.gov.tw/api/datasets/EDC3AD26-8AE7-4916-A00B-BC6048D19BF8/json?page=0&size=10000' -o /tmp/ntpc_g0.json
curl -sm 30 'https://data.ntpc.gov.tw/api/datasets/EDC3AD26-8AE7-4916-A00B-BC6048D19BF8/json?page=1&size=10000' -o /tmp/ntpc_g1.json
curl -sm 30 'https://data.ntpc.gov.tw/api/datasets/EDC3AD26-8AE7-4916-A00B-BC6048D19BF8/json?page=2&size=10000' -o /tmp/ntpc_g2.json
jq -s 'add' /tmp/ntpc_g0.json /tmp/ntpc_g1.json /tmp/ntpc_g2.json > /tmp/ntpc_g.json
```

2026-09-09 實測:HTTP 200;全量 26,655 列(page 0/1 各 10,000 列、page 2 有 6,655 列),每頁約 5-7MB。**size 上限 10,000,不給 page 參數只會拿到第一頁**,務必分頁抓到空頁為止。資料量大,短時間內重複查詢請用同一份快取。

### 2. 欄位

| 欄位 | 意義 |
| --- | --- |
| `city` | 行政區(板橋區、新店區…) |
| `village` | 里別 |
| `lineid` / `linename` | 路線編號 / 路線名 |
| `rank` | 停靠順序 |
| `name` | 清運點地點描述 |
| `longitude` / `latitude` | 座標(字串) |
| `time` | 停靠時間 `HH:MM`(字串) |
| `garbagemonday`…`garbagesunday` | 該日是否收一般垃圾(`Y` = 有,空字串 = 無) |
| `recyclingmonday`…`recyclingsunday` | 該日是否收資源回收(`Y` = 有) |
| `memo` | 備註 |

### 3. 查詢範例

```bash
# 板橋區今天晚上 18:00 後還會到的點
jq -r '.[] | select(.city=="板橋區" and .time>="18:00") | "\(.village) \(.name) \(.time) \(.linename)"' /tmp/ntpc_g.json | sort -t' ' -k3 | head

# 星期三有收垃圾的點(garbagewednesday == "Y")
jq -r '.[] | select(.city=="新店區" and .garbagewednesday=="Y") | "\(.village) \(.name) \(.time)"' /tmp/ntpc_g.json | head

# 離指定座標最近且今天(以星期五為例)有收的 5 個點
jq -r --argjson la 25.012 --argjson lo 121.465 '
  [.[] | select(.garbagefriday=="Y")
   | . + {d: ((.latitude|tonumber)-$la)*((.latitude|tonumber)-$la) + ((.longitude|tonumber)-$lo)*((.longitude|tonumber)-$lo)}]
  | sort_by(.d) | .[0:5][] | "\(.city)\(.village) \(.name) \(.time)"' /tmp/ntpc_g.json
```

「今天有沒有收」的做法:把今天星期幾對到 `garbage<english weekday>` 欄位(`monday`~`sunday` 全小寫),`Y` 就是有收;資源回收看 `recycling<weekday>`。注意例假日、國定假日與颱風天的停收異動以新北市政府環境保護局公告為準。

## 錯誤與失敗時的處理

- **HTTP 404(台北)**:resource id 已更換。依上面的步驟回資料集頁重新解析下載連結;解析不到就如實告知資料集頁結構改變,請使用者到 data.taipei 手動下載。
- **下載到 HTML 而不是 CSV/JSON**(例如錯誤頁):視為失敗,重試 1~2 次,仍失敗就告知來源異常。
- **BOM / 編碼(台北)**:檔案開頭有 UTF-8 BOM,解析前先去掉(上面的 `sed` 範例),否則第一欄欄名比對會失敗。
- **新北只抓到 10,000 列**:忘了分頁。`size` 上限 10,000,全量約 2.7 萬列(2026-09-09 實測),要 `page=0,1,2…` 抓到空頁為止。
- **查不到某個里**:確認里名寫法(「里」結尾、繁體),再用行政區擴大範圍列出可選的里,讓使用者挑;不要猜最近似的一筆直接回報。
- **其他縣市**:此技能只涵蓋台北市與新北市。桃園、台中、台南、高雄等縣市請回報尚未支援,或查閱該縣市開放資料平台。
- **計畫時間 vs 實際**:兩市都是計畫停靠時間,實際抵達受路況影響;停收日、國定假日與颱風天異動以各市環保局公告為準。

## English summary

Looks up garbage-truck collection stops and scheduled times for Taipei City and New Taipei City (no login, no API key). Taipei uses the data.taipei CSV (~550KB, `HHMM` times, strip the UTF-8 BOM; the download resource id can rotate - re-resolve from the dataset page on 404). New Taipei uses the data.ntpc.gov.tw JSON API, which paginates at 10,000 rows per page - fetch pages 0-2 for the full ~26.7k rows (verified 2026-09-09), with per-weekday `garbage<weekday>`/`recycling<weekday>` flags so "is there collection today" is answerable. Both sources carry lat/lon for nearest-stop queries. Times are planned stops, not live GPS; holiday and typhoon-day changes follow each city's DEP announcements.

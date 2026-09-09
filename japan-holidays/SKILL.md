---
name: japan-holidays
description: 内閣府の公式CSVから祝日・振替休日・国民の休日を調べ、連休を計算する。祝日、連休、ゴールデンウィーク、シルバーウィーク、営業日判定の質問に対応。APIキー・ログイン不要。個人の予定管理やカレンダー操作は対象外。
license: MIT
metadata:
  category: calendar
  locale: ja-JP
---

# japan-holidays

内閣府が公開する「国民の祝日・休日」の公式CSVを使って、祝日の照会と連休の計算をするスキル。APIキー不要。

## データの取得

```bash
curl -s https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv | iconv -f SHIFT_JIS -t UTF-8
```

- 文字コードは **Shift_JIS**。必ず `iconv` などでUTF-8に変換する。
- 1行目はヘッダー (`国民の祝日・休日月日,国民の祝日・休日名称`)。以降 `1955/1/1,元日` の形式。
- 振替休日・国民の休日もあらかじめ行として含まれている(名称は `休日`)。
- 収録範囲は1955年から翌年分程度まで。先の年は未収録のことがある。

## できること

### 特定の日が祝日か調べる

日付でCSVを引き、一致すれば名称を返す。なければ祝日ではない。

### ある期間の祝日一覧を出す

期間でフィルタして日付順に返す。

### 連休を計算する

1. 対象期間の全日付を走査し、各日を「休み」か判定する。休み = 土曜・日曜・CSVにある日。
2. 連続する休みの区間に切り分ける。
3. 3日以上の区間を連休として返す。区間の最初と最後の日付、日数、含まれる祝日名を添える。

ゴールデンウィーク(4月末〜5月初め)やシルバーウィーク(9月)は、この計算で自然に出てくる。

## ルールの背景(CSVに頼れない将来年を計算する場合)

- **振替休日**: 祝日が日曜と重なったら、そのあと最初の「祝日でない平日」が休みになる。
- **国民の休日**: 前後が祝日の平日は休みになる(例: 敬老の日と秋分の日に挟まれた日)。

公式CSVがその年を収録していれば、この計算を自前でやる必要はない。CSVを正とする。

## 注意

- 元データは内閣府の公開ページ (https://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html)。CSVが更新されたら最新を取り直す。
- 祝日法の改正で変わることがある。古いローカルコピーを使い回さない。

## エラー・失敗時の対応

- **タイムアウトを付ける**: `curl -sm 30` のように必ず制限時間を付ける。
- **`iconv` がない環境**: 代わりに Python を使う(ほぼどの環境にもある):

  ```bash
  curl -sm 30 -s https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv \
    | python3 -c "import sys; sys.stdout.write(sys.stdin.buffer.read().decode('cp932'))"
  ```

  変換を忘れると祝日名が文字化けする。化けたままユーザーに見せない。
- **CSVが取れない(HTTP 5xx、タイムアウト、空)**: 1〜2回再試行し、駄目なら「内閣府のサイトから祝日CSVを取得できなかった。https://www8.cao.go.jp/chosei/shukujitsu/gaiyou.html で確認してください」と伝える。手元の古いコピーを最新として扱わない。
- **該当年がCSVに未収録**: 先の年はCSVに入っていないことがある。その場合は「公式CSVに未収録」と明示したうえで、上のルール(振替休日・国民の休日)による推計であることを区別して伝える。

## English summary

Looks up Japanese national holidays and computes long weekends from the Cabinet Office's official CSV. No API key or login required. The CSV is Shift_JIS encoded, so convert to UTF-8 first (`iconv`, or Python as a fallback). It covers 1955 through roughly next year; for later years, estimate with the holiday-law rules (substitute holidays, citizen's holidays) and label the result as an estimate. Always re-fetch instead of trusting an old local copy.

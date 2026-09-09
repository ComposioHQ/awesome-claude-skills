---
name: jma-weather
description: 気象庁の公開JSONから天気予報(天気・降水確率・気温・週間予報)を取得する。天気、気温、降水確率、明日・週末の予報の質問に対応。APIキー・ログイン不要。警報・注意報や地震・津波情報は対象外(bosai-alertを使う)。
license: MIT
metadata:
  category: weather
  locale: ja-JP
---

# jma-weather

気象庁が公式サイトで公開しているJSONデータから天気予報を取得するスキル。APIキー不要、`curl` だけで使える。

## 基本の流れ

1. エリアコードを決める
2. 予報JSONを取得する
3. 必要な時刻・地点の値を読む

### 1. エリアコードを決める

全国のエリア定義は1つのJSONにまとまっている。

```bash
curl -s https://www.jma.go.jp/bosai/common/const/area.json
```

構造: `centers` (管区気象台など) → `offices` (地方の予報単位。予報APIはこのコードを使う) → `class10s` / `class15s` / `class20s` (より細かい地域)。

よく使う `offices` コード:

| コード | 地域 | コード | 地域 |
| --- | --- | --- | --- |
| 014100 | 札幌 | 130000 | 東京 |
| 040000 | 仙台 | 270000 | 大阪 |
| 230000 | 名古屋 | 340000 | 広島 |
| 460040 | 鹿児島 | 471000 | 那覇 |

### 2. 予報JSONを取得する

```bash
# 天気・降水確率・気温(数日分)
curl -s https://www.jma.go.jp/bosai/forecast/data/forecast/130000.json

# 短期予報のテキスト概況
curl -s https://www.jma.go.jp/bosai/forecast/data/overview_forecast/130000.json
```

`130000` の部分を調べたい地域の `offices` コードに変える。

### 3. JSONの読み方

`forecast` レスポンスは配列で、要素ごとに `publishingOffice` (発表気象台) と `reportDatetime` (発表時刻) を持つ。`timeSeries` に時系列データが入る。通常は2要素あり、1つ目が短期(天気・降水確率・気温)、2つ目が週間(7日先までの降水確率と最高/最低気温)を持つ。週間分だけ別エンドポイントはない。

- `timeSeries[].timeDefines`: 各時刻の枠。他の配列とインデックスが対応する。
- `areas[].weathers`: 「晴れ 時々 くもり」などの天気文字列。
- `areas[].weatherCodes`: 天気コード(文字列)。対応表は下記。
- `areas[].pops`: 降水確率(%)。時間帯ごと。
- `areas[].temps`: 気温(℃)。発表時刻によって最低/最高が入る枠が変わるので、`timeDefines` と突き合わせて「何の値か」を確認する。

主な天気コード(先頭3桁):

- 100番台: 晴れ (100: 晴)
- 200番台: くもり (200: 曇)
- 300番台: 雨 (300: 雨)
- 400番台: 雪 (400: 雪)

末尾2桁で「時々」「のち」「一時」などの変化を表す。細かい値は `weathers` の文字列をそのまま使うのが確実。

## 注意

- すべて気象庁の発表データそのまま。加工せず、発表時刻(`reportDatetime`)を一緒に伝える。
- 予報は1日数回更新される。古いデータを引用しない。
- 短時間に連続リクエストしない。同じ予報を繰り返し見るならローカルにキャッシュする。

## エラー・失敗時の対応

- **タイムアウトを付ける**: `curl` には必ず `-m 30` 程度を付ける(例: `curl -sm 30 <URL>`)。応答がないまま待ち続けない。
- **HTTP 404**: エリアコードの間違いがほぼ原因。`https://www.jma.go.jp/bosai/common/const/area.json` を取り直し、`offices` 層のコードを使っているか確認する(`class10s` などの細かいコードでは 404 になる)。
- **HTTP 5xx / タイムアウト**: 気象庁サイト側の障害か負荷。数秒おいて1〜2回だけ再試行し、直らなければ「気象庁のサイトで障害が起きている可能性がある。公式サイト https://www.jma.go.jp/jma/index.html を直接確認してください」とユーザーに伝える。推測で予報をでっち上げない。
- **空・壊れたJSON**: JSONとして解釈できないレスポンス(HTMLのエラーページなど)が返ったら、それも失敗として扱う。古いキャッシュを「最新」として渡さない。

## English summary

Fetches weather forecasts (weather, precipitation probability, temperature) for anywhere in Japan from the Japan Meteorological Agency's public JSON feeds. No API key or login required; `curl` is enough. Find the area code in `area.json`, then read the forecast JSON for that office. Always quote the JMA issue time (`reportDatetime`) with the data, and check the official JMA site for any real decision.

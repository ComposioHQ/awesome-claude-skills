---
name: calil-books
description: カーリル図書館APIで図書館の蔵書と貸出状況を検索する。蔵書検索、図書館、貸出状況、本を借りたいときに対応。無料APIキーが必要。書籍の購入・電子書籍・国会図書館の検索は対象外。
license: MIT
metadata:
  category: books
  locale: ja-JP
---

# calil-books

カーリル図書館APIを使って、図書館の検索と本の貸出状況の照会をするスキル。公式APIで、利用は無料。

## APIキーの準備(最初の1回だけ)

1. https://calil.jp/api/dashboard/ でカーリルのアカウントを作り、APIキーを発行する(無料)。
2. キーはチャットやコード、コミットに書かない。環境変数(例: `CALIL_APPKEY`)に入れて使う。

## 図書館を検索する

```bash
curl -s "https://api.calil.jp/library?appkey=${CALIL_APPKEY}&pref=東京都&format=json"
```

- `pref`: 都道府県名。`city` で市区町村に絞れる。`geocode=経度,緯度` でも検索できる。
- レスポンスの `systemid` が蔵書照会で使う図書館システムのID。`libkey` は館の略名、`formal` は正式名称。

## 蔵書・貸出状況を調べる

```bash
curl -s "https://api.calil.jp/check?appkey=${CALIL_APPKEY}&isbn=9784478025819&systemid=Tokyo_Setagaya&format=json"
```

- `isbn`: 10桁または13桁。カンマ区切りで複数指定できる。
- `systemid`: 図書館検索で得たID。カンマ区切りで複数指定できる。

### ポーリング(重要)

蔵書照会は非同期。初回レスポンスが `continue: 1` の場合、返ってきた `session` を付けて2秒以上あけて再取得する。

```bash
curl -s "https://api.calil.jp/check?appkey=${CALIL_APPKEY}&session=SESSION_ID&format=json"
```

`continue: 0` になるまで繰り返す(数回で終わることが多い)。`session` 指定の再取得では `isbn` や `systemid` は付けない。

### 結果の読み方

`books → ISBN → systemid → libkey` の順に、館ごとの状態が入る。

- `貸出可`: いま借りられる
- `蔵書なし`: その館にない
- `貸出中` / `予約中` / `準備中` / `休館中`: いまは借りられない
- `蔵書あり`: 状況不明(館に問い合わせ)

`reserveurl` に予約ページへのURLが入ることがある。

## 注意

- APIキーは無料だが利用規約がある。商用利用や大量アクセスのルールはカーリルの案内 (https://calil.jp/doc/api.html) を確認する。
- 取得したデータのキャッシュ期間にも規約上の制限がある。恒久的な保存はしない。
- キーを第三者と共有しない。

## エラー・失敗時の対応

- **タイムアウトを付ける**: `curl -sm 30` のように必ず制限時間を付ける。
- **ポーリングの上限(重要)**: `continue: 1` が続く場合、**最大10回・合計2分程度**を上限にする。それを超えたら打ち切り、「図書館APIの照会が混み合っていて結果が返りませんでした。時間をおいてもう一度試してください」とユーザーに伝える。無限にポーリングしない。
- **APIキーのエラー**: キーが無効・未設定だと正常な結果が返らない。`CALIL_APPKEY` が設定されているか、キーが正しいかを確認し、「カーリルのAPIキーが無効な可能性があります。https://calil.jp/api/dashboard/ で確認してください」と伝える。
- **HTTP 4xx**: パラメータかキーの問題。再試行で直らないので、原因を確認してから1回だけやり直す。
- **HTTP 5xx / タイムアウト**: 1〜2回だけ再試行。直らなければカーリル側の障害の可能性として、 https://calil.jp/ を直接確認するよう案内する。
- **`蔵書なし` や空の結果はエラーではない**: その館に本がない正常な結果として伝える。取得失敗と混同しない。

## English summary

Searches library holdings and loan availability across Japan via the Calil Library API. Requires a free API key from https://calil.jp/api/dashboard/ - keep it in an environment variable, never in chat or commits. Availability checks are asynchronous: poll with the returned `session` at 2+ second intervals, capped at about 10 tries / 2 minutes. The API terms limit long-term caching of results.

# React Best Practices

[English](README.md) | [한국어](README.ko.md) | [中文](README.zh.md) | **日本語**

---

エージェントとLLMに最適化されたReactベストプラクティスを作成・維持するための構造化されたリポジトリです。

## 構造

- `rules/` - 個別のルールファイル（ルールごとに1つ）
  - `_sections.md` - セクションメタデータ（タイトル、影響度、説明）
  - `_template.md` - 新しいルール作成用テンプレート
  - `area-description.md` - 個別のルールファイル
- `src/` - ビルドスクリプトとユーティリティ
- `metadata.json` - ドキュメントメタデータ（バージョン、組織、概要）
- __`AGENTS.md`__ - コンパイル済み出力（自動生成）
- __`test-cases.json`__ - LLM評価用テストケース（自動生成）

## はじめに

1. 依存関係をインストール：
   ```bash
   pnpm install
   ```

2. ルールからAGENTS.mdをビルド：
   ```bash
   pnpm build
   ```

3. ルールファイルを検証：
   ```bash
   pnpm validate
   ```

4. テストケースを抽出：
   ```bash
   pnpm extract-tests
   ```

## 新しいルールの作成

1. `rules/_template.md`を`rules/area-description.md`にコピー
2. 適切なエリア接頭辞を選択：
   - `async-` - ウォーターフォールの排除（セクション1）
   - `bundle-` - バンドルサイズ最適化（セクション2）
   - `server-` - サーバーサイドパフォーマンス（セクション3）
   - `client-` - クライアントサイドデータフェッチング（セクション4）
   - `rerender-` - 再レンダリング最適化（セクション5）
   - `rendering-` - レンダリングパフォーマンス（セクション6）
   - `js-` - JavaScriptパフォーマンス（セクション7）
   - `advanced-` - 高度なパターン（セクション8）
3. フロントマターとコンテンツを記入
4. 説明付きの明確な例を含める
5. `pnpm build`を実行してAGENTS.mdとtest-cases.jsonを再生成

## ルールファイル構造

各ルールファイルは以下の構造に従う必要があります：

```markdown
---
title: ルールタイトル
impact: MEDIUM
impactDescription: オプションの説明
tags: タグ1, タグ2, タグ3
---

## ルールタイトル

ルールとその重要性の簡単な説明。

**誤った例（何が問題かの説明）：**

```typescript
// 悪いコード例
```

**正しい例（何が正しいかの説明）：**

```typescript
// 良いコード例
```

例の後のオプションの説明テキスト。

参照：[リンク](https://example.com)

## ファイル命名規則

- `_`で始まるファイルは特別なファイル（ビルドから除外）
- ルールファイル：`area-description.md`（例：`async-parallel.md`）
- セクションはファイル名の接頭辞から自動的に推測
- ルールは各セクション内でタイトル順にアルファベット順でソート
- ID（例：1.1、1.2）はビルド時に自動生成

## 影響度レベル

- `CRITICAL` - 最優先、主要なパフォーマンス向上
- `HIGH` - 大幅なパフォーマンス改善
- `MEDIUM-HIGH` - 中〜高程度の向上
- `MEDIUM` - 中程度のパフォーマンス改善
- `LOW-MEDIUM` - 中〜低程度の向上
- `LOW` - 段階的な改善

## スクリプト

- `pnpm build` - ルールをAGENTS.mdにコンパイル
- `pnpm validate` - すべてのルールファイルを検証
- `pnpm extract-tests` - LLM評価用テストケースを抽出
- `pnpm dev` - ビルドと検証

## コントリビュート

ルールを追加または変更する際：

1. セクションに適した正しいファイル名接頭辞を使用
2. `_template.md`構造に従う
3. 説明付きの明確な悪い/良い例を含める
4. 適切なタグを追加
5. `pnpm build`を実行してAGENTS.mdとtest-cases.jsonを再生成
6. ルールはタイトルで自動的にソート - 番号の管理は不要！

## 謝辞

[Vercel](https://vercel.com)の[@shuding](https://x.com/shuding)によって作成されました。

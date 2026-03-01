# 🏟️ 松本市 体育館 空き状況チェッカー

松本市公共施設予約システムの体育館空き状況を、施設と日付を選ぶだけで自動表示するWebアプリです。

## 📸 使い方イメージ

```
① ブラウザで http://localhost:5000 を開く
        ↓
② 体育館を選択（複数選択可）・日付を入力
        ↓
③「ブラウザを起動して空き状況を確認」ボタンをクリック
        ↓
④ 別ウィンドウで予約サイトが自動操作される
        ↓
⑤ 指定日の空き状況ページが表示される
```

## ✅ 動作要件

- **OS**: Windows 10/11 または macOS
- **Python**: 3.9 以上
- インターネット接続（松本市予約サイトへのアクセス）

---

## 🚀 セットアップ手順

### 1. リポジトリをクローン

```bash
git clone https://github.com/foolproof-dev/auto-reservation.git
cd auto-reservation/matsumoto-yoyaku
```

### 2. Python ライブラリをインストール

```bash
pip install flask playwright
```

### 3. Playwright 用ブラウザをインストール

```bash
python -m playwright install chromium
```

> **Windowsの場合**、追加で以下も実行してください（依存ライブラリのインストール）:
> ```bash
> python -m playwright install-deps chromium
> ```

### 4. アプリを起動

```bash
python app.py
```

起動すると以下のように表示されます：

```
==================================================
 松本市 体育館 空き状況チェッカー
 URL: http://localhost:5000
==================================================
```

### 5. ブラウザでアクセス

お使いのブラウザで以下のURLを開いてください：

```
http://localhost:5000
```

---

## 📖 操作手順

1. **体育館を選択**（チェックボックス、複数選択可）
2. **日付を選択**（カレンダーから選択）
3. **「ブラウザを起動して空き状況を確認」** ボタンをクリック
4. 数秒後に **別ウィンドウ** で松本市予約サイトが自動操作されます
5. 指定した体育館・日付の **空き状況ページ** が表示されます

---

## 🏠 対応施設一覧

| 施設名 | 施設名 |
|---|---|
| 総合体育館 | 今井体育館 |
| 南部体育館 | 島立体育館 |
| 岡田体育館 | 寿体育館 |
| 芳川体育館 | 寿台体育館 |
| 島内体育館 | 本郷体育館 |
| 庄内体育館 | 内田体育館 |
| 芝沢体育館 | 中央体育館 |
| 神林体育館 | 臨空工業団地体育館 |
| 里山辺体育館 | 四賀体育館 |
| 鎌田体育館 | 安曇体育館 |

---

## 📁 ファイル構成

```
matsumoto-yoyaku/
├── app.py              # Flask Webサーバー
├── automation.py       # Playwright 自動操作スクリプト
├── templates/
│   └── index.html      # Webアプリ画面
└── README.md           # このファイル
```

---

## ⚙️ 仕組み

```
[ブラウザ: localhost:5000]
    │  施設ID・日付を POST
    ▼
[Flask サーバー: app.py]
    │  subprocess で起動
    ▼
[Playwright: automation.py]          [別ウィンドウ: Chromium]
  1. 予約サイトのトップへアクセス  →  画面表示
  2. 体育施設カテゴリーをクリック  →  施設一覧表示
  3. 指定施設にチェック           →  選択状態に
  4. 空き状況ページへ移行         →  カレンダー表示
  5. 指定日付を選択・次へ         →  検索結果表示 ✅
```

---

## ❓ トラブルシューティング

### ブラウザウィンドウが開かない

- `python -m playwright install chromium` を再実行してください
- Windowsの場合、`python -m playwright install-deps chromium` も実行してください

### `ModuleNotFoundError: No module named 'flask'`

```bash
pip install flask playwright
```

### ポート5000が使用中

`app.py` の最終行を変更してください：

```python
app.run(host='0.0.0.0', port=8080, debug=False)  # 5000 → 8080 に変更
```

アクセスURLも `http://localhost:8080` に変わります。

### 施設が見つからない・選択できない

松本市予約サイト側のメンテナンスや構造変更の可能性があります。  
[松本市公共施設予約システム](https://yoyaku.city.matsumoto.lg.jp/WebR/) を直接確認してください。

---

## 🔗 関連リンク

- [松本市公共施設予約システム](https://yoyaku.city.matsumoto.lg.jp/WebR/)

---

## 📝 注意事項

- このツールは松本市公共施設予約システムの操作を自動化するものです
- 予約の申込・キャンセルは自動操作せず、空き状況の**確認のみ**を行います
- サイトの仕様変更により動作しなくなる場合があります

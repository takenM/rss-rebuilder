# rss-rebuilder

ポッドキャストのRSSを定期取得・加工して、GitHub Pages から自分専用フィードとして再配信する。

```
元のRSS
   ↓ (6時間おき / GitHub Actions)
feed.py で加工
   ↓
docs/feed.xml としてコミット
   ↓
GitHub Pages が静的配信
```

音声ファイルは配信しない（`enclosure` は元の配信元URLのまま）。

## セットアップ

1. Settings → Secrets and variables → Actions → **Variables** に `SOURCE_URL` を登録（元のRSSのURL）
2. Settings → Pages で Source = `Deploy from a branch`, Branch = `main` / `/docs`
3. Actions タブから `build-feed` を手動実行
4. `https://takenm.github.io/rss-rebuilder/feed.xml` を確認
5. Podcast アプリに登録

## 加工ロジック

`feed.py` の `transform(channel)` のみを編集する。除外・絞り込み・整形などの
パターンはコメントアウトで用意済み。

ローカル検証:

```bash
SOURCE_URL="https://example.com/feed.xml" python feed.py
```

## 注意

- `ET.register_namespace()` を外すと出力が `ns0:` になり Podcast アプリが壊れる。触らない
- Public リポジトリのため Actions のログは公開される。URLやデバッグ出力を print しない
- リポジトリに人間の操作が60日間ないとスケジュール実行が自動停止する（bot コミットは対象外）

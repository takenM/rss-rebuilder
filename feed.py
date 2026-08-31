#!/usr/bin/env python3
"""
元のRSSを取得して、好きに加工して docs/feed.xml に書き出すスクリプト。

ローカル実行:
    SOURCE_URL="https://example.com/feed.xml" python feed.py
"""

import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# ---------------------------------------------------------------
# 設定
# ---------------------------------------------------------------
SOURCE_URL = os.environ.get("SOURCE_URL")
OUTPUT = Path(__file__).parent / "docs" / "feed.xml"

# ポッドキャストのRSSは名前空間だらけなので、先に登録しておく。
# これをやらないと出力が ns0: ns1: だらけになって、
# Apple Podcasts などが itunes タグを認識できなくなる。
NAMESPACES = {
    "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "atom": "http://www.w3.org/2005/Atom",
    "dc": "http://purl.org/dc/elements/1.1/",
    "media": "http://search.yahoo.com/mrss/",
    "podcast": "https://podcastindex.org/namespace/1.0",
    "googleplay": "http://www.google.com/schemas/play-podcasts/1.0",
    "sy": "http://purl.org/rss/1.0/modules/syndication/",
}
for prefix, uri in NAMESPACES.items():
    ET.register_namespace(prefix, uri)


def itunes(tag: str) -> str:
    """itunes:xxx を ElementTree の書式に変換するヘルパー"""
    return "{%s}%s" % (NAMESPACES["itunes"], tag)


# ---------------------------------------------------------------
# ここから下が「加工」の中身。ここだけ書き換えればいい
# ---------------------------------------------------------------
def transform(channel: ET.Element) -> None:
    """
    channel 要素を破壊的に書き換える。
    触らなかった要素は元のまま残るので、必要な部分だけ手を入れればよい。
    """
    items = channel.findall("item")

    # --- 例1: チャンネルのタイトルを変える ---------------------
    # title = channel.find("title")
    # if title is not None:
    #     title.text = "○○（カスタム版）"

    # --- 例2: タイトルに特定の語を含むエピソードを除外 ---------
    # NG_WORDS = ["再放送", "PR"]
    # for item in items:
    #     t = (item.findtext("title") or "")
    #     if any(w in t for w in NG_WORDS):
    #         channel.remove(item)

    # --- 例3: 逆に、特定の語を含むものだけ残す ------------------
    # KEEP = "第"
    # for item in items:
    #     if KEEP not in (item.findtext("title") or ""):
    #         channel.remove(item)

    # --- 例4: エピソードのタイトルを整形 ------------------------
    # for item in items:
    #     t = item.find("title")
    #     if t is not None and t.text:
    #         t.text = t.text.replace("【広告】", "").strip()

    # --- 例5: 最新N件だけ残す（アプリの読み込みを軽くする） -----
    # for item in items[50:]:
    #     channel.remove(item)

    # --- 例6: 説明文を書き換える -------------------------------
    # for item in items:
    #     d = item.find("description")
    #     if d is not None and d.text:
    #         d.text = d.text.split("スポンサー")[0].strip()

    # とりあえず今は素通し（何もしない）
    return


# ---------------------------------------------------------------
# 以下は基本さわらなくてよい
# ---------------------------------------------------------------
def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            # デフォルトのUAだと弾く配信元がそこそこあるので指定しておく
            "User-Agent": "Mozilla/5.0 (compatible; feed-rebuilder/1.0)",
            "Accept": "application/rss+xml, application/xml, text/xml, */*",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return res.read()


def main() -> int:
    if not SOURCE_URL:
        print("SOURCE_URL が設定されていません", file=sys.stderr)
        return 1

    # Public リポジトリだと Actions のログも公開されるため、
    # URL全体は出さずホスト名だけ出す
    host = urllib.parse.urlparse(SOURCE_URL).netloc or "(不明)"
    print(f"取得中: {host}")
    raw = fetch(SOURCE_URL)

    root = ET.fromstring(raw)
    channel = root.find("channel")
    if channel is None:
        print("channel要素が見つかりません。RSS 2.0ではないかもしれません", file=sys.stderr)
        return 1

    before = len(channel.findall("item"))
    transform(channel)
    after = len(channel.findall("item"))
    print(f"エピソード数: {before} -> {after}")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(OUTPUT, encoding="utf-8", xml_declaration=True)
    print(f"書き出し完了: {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

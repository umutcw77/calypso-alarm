import itertools
import json
import os
import urllib.request

from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT

VIDEO_ID = "BaO3jEGUHLc"
YAZAR_ANAHTAR = "calypso"
KAC_YORUMA_BAK = 80
STATE_FILE = "seen.json"
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")

URL = f"https://www.youtube.com/watch?v={VIDEO_ID}"


def bildirim_gonder(yorum):
    req = urllib.request.Request(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=yorum.get("text", "")[:300].encode("utf-8"),
        method="POST",
        headers={
            "Title": "Calypso yorum yazdi!",
            "Priority": "5",
            "Tags": "rotating_light,bell",
            "Click": f"{URL}&lc={yorum['cid']}",
        },
    )
    urllib.request.urlopen(req, timeout=15)


def main():
    if not NTFY_TOPIC:
        print("NTFY_TOPIC secret'i tanimli degil.")
        return

    ilk_calisma = not os.path.exists(STATE_FILE)
    if ilk_calisma:
        gorulen = []
    else:
        with open(STATE_FILE, encoding="utf-8") as f:
            gorulen = json.load(f)
    gorulen_set = set(gorulen)

    try:
        dl = YoutubeCommentDownloader()
        gen = dl.get_comments_from_url(URL, sort_by=SORT_BY_RECENT)
        yorumlar = list(itertools.islice(gen, KAC_YORUMA_BAK))
    except Exception as e:
        print("Yorumlar cekilemedi:", e)
        return

    if not yorumlar:
        print("Hic yorum gelmedi, atlaniyor.")
        return

    for y in yorumlar:
        if y["cid"] in gorulen_set:
            continue
        gorulen.append(y["cid"])
        gorulen_set.add(y["cid"])
        if not ilk_calisma and YAZAR_ANAHTAR.lower() in y.get("author", "").lower():
            print("ALARM:", y["author"])
            bildirim_gonder(y)

    gorulen = gorulen[-1000:]
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(gorulen, f)
    print(f"Tamam. Toplam gorulen: {len(gorulen)}")


main()

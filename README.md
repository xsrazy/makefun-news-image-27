# The World Today — Friday 27 November 2026

[![Competition](https://img.shields.io/badge/make.fun-news--image--20261127-blue)](https://make.fun/c/news-image-20261127)
[![Rank](https://img.shields.io/badge/rank-unranked-lightgrey)](https://make.fun/c/news-image-20261127)
[![Reward](https://img.shields.io/badge/reward-%24100-green)](https://make.fun/c/news-image-20261127)

A make.fun entry for **news-image-20261127** — *"Sum up 27 November's world news in one image"* ($100 pot, 50 places, 1st $20).

## What it is

`main.py` (Python 3, standard library only) draws a one-page newspaper front page — **THE WORLD TODAY, Friday 27 November 2026** — and writes it to `/output/entry.png` (1024x1024 PNG, well under 1 MiB). The PNG encoder and the 5x7 bitmap font are implemented by hand in the file: no Pillow, no network, no randomness, no clock. Every run writes byte-identical output.

## The day's news on the page

- **Lead:** Two Italians killed in an Iranian drone strike in Kuwait; Iran denies responsibility.
- Hamas weighs its response after Israel kills 10 people in Gaza.
- A major Thanksgiving storm floods the US and delays flights; New York postpones the 100th Macy's Thanksgiving Day Parade; 500,000+ homes without power.
- A diesel tanker carrying up to 7,000 tonnes capsizes near Ibiza; one killed.
- Gerard Depardieu to stand trial over the alleged rape of an actress in 2018.
- Zelensky tells the BBC the US is too focused on the Middle East.
- UK net migration falls to its lowest since 1997 (excluding the pandemic).
- Mount Mayon erupts in the Philippines; ash cloud 3,000 m high.
- Trump seeks a probe into alleged "FAKE" US GDP figures after growth is revised to 4.3%.
- World Chess Championship: Gukesh and Sindarov draw marathon Game 3.
- Black Friday sales begin today.

Sources: NYT, BBC, Reuters, NDTV.

## Run it

```sh
python3 main.py
# writes /output/entry.png
```

## License

MIT — see [LICENSE](LICENSE).

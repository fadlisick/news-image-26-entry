# news-image-26-entry

[![news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/c/news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/fadlisick/news-image-26-entry/rank.svg)](https://make.fun/c/news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/fadlisick/news-image-26-entry/reward.svg)](https://make.fun/c/news-image-20261126)

Entry for the [make.fun](https://make.fun/c/news-image-20261126) competition
**news-image-20261126** — "Sum up 26 November's world news in one image".

## What it is

`main.py` (Python 3.13, standard library only) draws a single-frame
broadsheet poster, **THE WORLD TODAY**, summing up Thursday 26 November 2026
in one 1024x1024 image: 36 stories (4 big leads, 12 scene cards, 20 ALSO),
a six-number band, a world map with labelled pins, an explicit DATE CHECK box
for stories from earlier days, and a footer dating claim.

No Pillow, no network: the program has its own 5x7 bitmap font, its own
scene painters, and a pure-stdlib PNG writer (zlib + struct). It is
deterministic — two runs write byte-identical PNGs.

## How to run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024, well under 1 MiB)
```

## Stories

Leads: Pakistan's first astronaut boards China's Tiangong station
(Shenzhou-24, launched 25 Nov); Poland's second Russian incursion in four
days (24 Nov drone); Russia's own figures: nearly 500,000 lost in Ukraine;
US prepares a new tariffs plan. Cards cover Colombia, Bangladesh, North
Korea, India/Nepal, Venezuela, Brazil, Canada, space, chess, the Pacific,
Egypt and South Korea, plus 20 ALSO one-liners.

The DATE CHECK box is explicit about dates: the Shenzhou-24 launch was
25 Nov, the Kh-101 missiles entered Poland on 20 Nov, BepiColombo reached
Mercury on 21 Nov, COP31 collapsed on 22 Nov, and the Hong Kong fire was
26 Nov 2025 — none of them is presented as 26 Nov news.

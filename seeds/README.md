# Seeds

Small hand-curated inputs, kept in version control (unlike `data/`).

| File | What | Source |
|---|---|---|
| `mugello.geojson` | Circuit outline: a closed LineString of 129 points, clockwise, starting on the main straight (5,243 m measured against the official 5,245 m) | [bacinger/f1-circuits](https://github.com/bacinger/f1-circuits) `it-1914.geojson`, MIT (see `LICENSE-f1-circuits.md`) |
| `corners.csv` | Turn number, name and the outline point index at each corner (turn 0 = start/finish line), plus where its name sits on the map (`label_dx_m`/`label_dy_m` from the corner, TV orientation, and the text anchor) | Placed by hand on the outline, then checked against the Wikimedia Commons *Mugello Racing Circuit track map.svg* (CC BY-SA 3.0). That map numbers 14 turns, treating Biondetti as one corner; we use the current 15-turn numbering (Biondetti 1 and 2) |
| `key_moments.csv` | The poster's story beats: lap, where (turn, optional), whose moment it is (`focus`: protagonist or rival) and short plain-language text | `docs/research/race_story.md` (data, broadcast, podcast) |
| `stretches.csv` | Stretches of track painted yellow on the poster: outline point range (may wrap past the line) and the moments they belong to | Layout D design; corners from `corners.csv` |
| `italy.geojson` | Italy outline (mainland, Sicily, Sardinia; 555 points) for the locator map | [Natural Earth](https://www.naturalearthdata.com/) 1:50m admin-0 countries v5.1.2, **public domain** |
| `callouts.csv` | Where each map corner's moment badges and callout text sit, as metre offsets from the corner (TV orientation) | Layout D wireframe (`design/wireframe/tools/build_poster_d.py`, converted at 1 px = 1.1498 m) |
| `key_numbers.csv` | The labels of the three key numbers beside the map; the values come from `poster.timeline` | Layout D design |

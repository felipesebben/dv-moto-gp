# Seeds

Small hand-curated inputs, kept in version control (unlike `data/`).

| File | What | Source |
|---|---|---|
| `mugello.geojson` | Circuit outline: a closed LineString of 129 points, clockwise, starting on the main straight (5,243 m measured against the official 5,245 m) | [bacinger/f1-circuits](https://github.com/bacinger/f1-circuits) `it-1914.geojson`, MIT (see `LICENSE-f1-circuits.md`) |
| `corners.csv` | Turn number, name and the outline point index at each corner (turn 0 = start/finish line) | Placed by hand on the outline, then checked against the Wikimedia Commons *Mugello Racing Circuit track map.svg* (CC BY-SA 3.0). That map numbers 14 turns, treating Biondetti as one corner; we use the current 15-turn numbering (Biondetti 1 and 2) |
| `key_moments.csv` | The poster's story beats: lap, where (turn, optional) and short plain-language text | `docs/research/race_story.md` (data, broadcast, podcast) |

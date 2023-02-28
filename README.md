# pybeatsaber
BeatSaber Beatmap IO Library written in pure python

## Installation

```sh
pip install git+https://github.com/Kitsunetic/pybeatsaber
```


## Notations

- Beatmap: a level of a beatmap, containing notes, obstacles, events, sliders.
- BeatmapInfo: more additional information about a `Beatmap`.
- BeatmapSet: a set of `BeatmapInfo`. This is categorized by `_beatmapCharacteristicName`, such as "Standard", "No Arrow", "One Saber", e.t.c.
- PyBeatmap: a container of multiple beatmaps and thier information.


## Usage

Load beatmap file (*.zip)

```py
from pybeatsaber import PyBeatmap

pybeat = PyBeatmap("000fbcb46c41cd0c363a80ae389333f7625e0921.zip")
pybeat
"""
PyBeatmap(LA DI DA,  {
    BeatmapSet(Standard: [Hard, Expert, ExpertPlus]
}
"""
```


Beatmap file data structure:
The structure is following map format of [BSMG Wiki](https://bsmg.wiki/mapping/map-format.html).

```py
bmapset = bmap.difficultyBeatmapSets[0]
"""
BeatmapSet(Standard: [Hard, Expert, ExpertPlus]
"""

bmapset.difficultyBeatmaps
"""
[BeatmapInfo(Hard, noteJumpMovementSpeed=14, noteJumpStartBeatOffset=0.4000000059604645),
 BeatmapInfo(Expert, noteJumpMovementSpeed=16, noteJumpStartBeatOffset=0),
 BeatmapInfo(ExpertPlus, noteJumpMovementSpeed=18, noteJumpStartBeatOffset=-0.4000000059604645)]
"""

bmapinfo = bmapset.difficultyBeatmaps[0]
bmap = bmapinfo.beatmap
bmap
"""
Beatmap(687 notes, 0 sliders, 166 obstacles, 9456 events)
"""
```


Read notes, obstacles, events, sliders:

```py
bmap.notes[:10]
"""
[Note(5.4: (2, 0, 1, 1),
 Note(6.4: (3, 1, 1, 5),
 Note(7.4: (1, 0, 0, 1),
 Note(8.4: (0, 1, 0, 4),
 Note(8.9: (3, 0, 1, 1),
 Note(9.9: (3, 1, 1, 0),
 Note(10.9: (2, 0, 1, 1),
 Note(11.4: (1, 0, 0, 1),
 Note(12.4: (0, 1, 0, 4),
 Note(13.4: (1, 0, 0, 1)]
"""

bmap.obstacles[:10]
"""
[Obstacle(5.4: (0, 1, 1, 0.25)),
 Obstacle(7.4: (3, 1, 1, 0.25)),
 Obstacle(9.4: (0, 1, 1, 0.25)),
 Obstacle(31.4: (3, 1, 0, 0.125)),
 Obstacle(31.4: (0, 1, 0, 0.125)),
 Obstacle(32.4: (0, 1, 0, 0.0625)),
 Obstacle(32.4: (3, 1, 0, 0.0625)),
 Obstacle(33.2: (3, 1, 0, 0.0625)),
 Obstacle(33.2: (0, 1, 0, 0.07249999791383743)),
 Obstacle(33.8: (3, 1, 0, 0.0625))]
"""

bmap.events[:10]
"""
[Event(5.4: (2, 6)),
 Event(5.4: (1, 3)),
 Event(5.4: (12, 2)),
 Event(5.4: (9, 0)),
 Event(6.4: (3, 6)),
 Event(6.4: (2, 0)),
 Event(6.4: (13, 2)),
 Event(7.4: (1, 3)),
 Event(7.4: (2, 6)),
 Event(7.4: (12, 2))]
"""

bmap.sliders[:10]
"""
[]
"""
```

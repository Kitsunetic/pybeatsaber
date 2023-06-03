# pybeatsaber
BeatSaber beatmap IO library written in pure python.

This library contains such functionalities:
- save/load `*.zip` file (which contians info.dat and music file)
- load music as `bytes` (you can also load it using `librosa` and `BytesIO`)
- load cover image (`Pillow`)

## Installation

```sh
pip install pybeatsaber
```


## Usage

Load beatmap file (*.zip).

The data has hierarchical structure.
I followed the structure introduced in documentation of [BSMG Wiki](https://bsmg.wiki/mapping/map-format.html) as much as possible.

The specific notations are following:
- `PyBeatmap`: The top class of the hierarchy. It can be opened from a `*.zip` file or you also can make this class from scratch.
- `BeatmapSet`: A sub class of `PyBeatmap`. It stores multiple `BeatmapInfo`. `PyBeatmap` can have multiple `BeatmapSet`.
- `BeatmapInfo`: A sub class of `BeatmapSet`. It stores a `Beatmap`, and additional information about the `Beatmap`.
- `Beatmap`: A class of a beatmap. It has list of `Node`s, `Obstalce`s, `Event`s, `Slider`s.
- `Note`, `Obstacle`, `Event`, `Slider`: They represents a note of game, containing informations such as timing and direction.


### Usage Example: Load a `*.zip` file:

```py
from pybeatsaber import PyBeatmap

container = PyBeatmap.from_zip("00e6c4a1bc9d5c66169331fce2ddf05243ad57f9.zip")
container
"""
PyBeatmap(Mandala, (ft. Mitaka) {
    BeatmapSet(Standard: [Easy, Normal, Hard, Expert, ExpertPlus]
}
"""

container.difficultyBeatmapSets
"""
{'Standard': BeatmapSet(Standard: [Easy, Normal, Hard, Expert, ExpertPlus]}
"""

beatmap_set = container.difficultyBeatmapSets["Standard"]
beatmap_set
"""
BeatmapSet(Standard: [Hard, Expert, ExpertPlus]
"""

beatmap_set.difficultyBeatmaps
"""
[BeatmapInfo(Easy, noteJumpMovementSpeed=12, noteJumpStartBeatOffset=0.5),
 BeatmapInfo(Normal, noteJumpMovementSpeed=14, noteJumpStartBeatOffset=1),
 BeatmapInfo(Hard, noteJumpMovementSpeed=16, noteJumpStartBeatOffset=-0.200000002980232),
 BeatmapInfo(Expert, noteJumpMovementSpeed=19, noteJumpStartBeatOffset=-0.5),
 BeatmapInfo(ExpertPlus, noteJumpMovementSpeed=19, noteJumpStartBeatOffset=-0.5)]
"""

beatmap_info = beatmap_set.difficultyBeatmaps[0]
beatmap_info
"""
BeatmapInfo(Easy, noteJumpMovementSpeed=12, noteJumpStartBeatOffset=0.5)
"""

beatmap = beatmap_info.beatmap
beatmap
"""
Beatmap(185 notes, 0 sliders, 0 obstacles, 5365 events)
"""
```


### Usage Example: Read notes, obstacles, events, sliders:

```py
beatmap.notes[:10]
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

beatmap.obstacles[:10]
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

beatmap.events[:10]
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

beatmap.sliders[:10]
"""
[]
"""
```

### Usage Example: Save the beatmap:

```py
container.to_zip("test.zip")
```

You can open and visualize the result throguh [Beatmapper](https://beatmapper.app/)!

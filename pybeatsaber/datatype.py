import json
from dataclasses import dataclass
from os import PathLike
from typing import List, Union
from zipfile import ZipFile

__all__ = ["Note", "Slider", "Obstacle", "Event", "Beatmap", "BeatmapInfo", "BeatmapSet", "PyBeatmap"]


class _BytableDataType:
    def to_dict(self):
        out_dict = {}

        for k, v in self.__annotations__.items():
            if isinstance(v, _BytableDataType):
                v = v.to_dict()

            out_dict[k] = v

        return out_dict

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_bytes(self):
        return self.to_json().encode("utf-8")


@dataclass
class Note(_BytableDataType):
    time: float
    lineIndex: int
    lineLayer: int
    type: int
    cutDirection: int
    customData: dict

    def time_seconds(self, bpm: float):
        return self.time / bpm * 60

    @property
    def v(self):
        if self.type == 3:
            return 19  # no direction
        else:
            return 1 + self.type * 9 + self.cutDirection  # left = 1 ~ 9, right = 10 ~ 18

    def is_valid(self):
        x = self.lineIndex in (0, 1, 2, 3)
        x &= self.lineLayer in (0, 1, 2)
        x &= self.time in (0, 1)
        x &= (self.type in (0, 1) and self.cutDirection in (0, 1, 2, 3, 4, 5, 6, 7, 8)) or self.type == 3
        x &= self.time >= 0.0
        return x

    def __repr__(self):
        return f"Note({self.time:.1f}: ({self.lineIndex}, {self.lineLayer}, {self.type}, {self.cutDirection})"

    @staticmethod
    def from_dict(data: dict):
        return Note(
            time=data["_time"],
            lineIndex=data["_lineIndex"],
            lineLayer=data["_lineLayer"],
            type=data["_type"],
            cutDirection=data.get("_cutDirection", -1),
            customData=data.get("_customData", {}),
        )


@dataclass
class Slider(_BytableDataType):
    colorType: int
    headTime: float
    headLineIndex: int
    headLineLayer: int
    headControlPointLengthMultiplier: float
    headCutDirection: int
    tailTime: float
    tailLineIndex: int
    tailLineLayer: int
    tailControlPointLengthMultiplier: float
    tailCutDirection: int
    sliderMidAnchorMode: int
    customData: dict

    def __repr__(self):
        msg = f"Slider({self.headTime:.1f}: ({self.headLineIndex}, {self.headLineLayer}, {self.headCutDirection}) | "
        msg += f"{self.tailTime:.1f}: ({self.tailLineIndex}, {self.tailLineLayer}, {self.tailCutDirection}))"
        return msg

    @staticmethod
    def from_dict(data: dict):
        return Slider(
            colorType=data["_colorType"],
            headTime=data["_headTime"],
            headLineIndex=data["_headLineIndex"],
            headLineLayer=data["_headLineLayer"],
            headControlPointLengthMultiplier=data["_headControlPointLengthMultiplier"],
            headCutDirection=data["_headCutDirection"],
            tailTime=data["_tailTime"],
            tailLineIndex=data["_tailLineIndex"],
            tailLineLayer=data["_tailLineLayer"],
            tailControlPointLengthMultiplier=data["_tailControlPointLengthMultiplier"],
            tailCutDirection=data["_tailCutDirection"],
            sliderMidAnchorMode=data["_sliderMidAnchorMode"],
            customData=data.get("_customData", {}),
        )


@dataclass
class Obstacle(_BytableDataType):
    time: float
    lineIndex: int
    width: int
    type: int
    duration: int
    customData: dict

    def time_seconds(self, bpm: float):
        return self.time / bpm * 60

    def is_valid(self):
        x = self.lineIndex in (0, 1, 2, 3)
        x &= self.width in (1, 2, 3, 4)
        x &= self.type in (0, 1)
        x &= 1 <= (self.lineIndex + self.width) <= 4
        x &= self.time >= 0
        x &= self.duration >= 0
        return x

    def __repr__(self):
        return f"Obstacle({self.time:.1f}: ({self.lineIndex}, {self.width}, {self.type}, {self.duration}))"

    @staticmethod
    def from_dict(data: dict):
        return Obstacle(
            time=data["_time"],
            lineIndex=data["_lineIndex"],
            width=data["_width"],
            type=data["_type"],
            duration=data["_duration"],
            customData=data.get("_customData", {}),
        )


@dataclass
class Event(_BytableDataType):
    time: int
    type: int
    value: int
    floatValue: float
    customData: dict

    def __repr__(self):
        return f"Event({self.time:.1f}: ({self.type}, {self.value}))"

    @staticmethod
    def from_dict(data: dict):
        return Event(
            time=data["_time"],
            type=data["_type"],
            value=data["_value"],
            floatValue=data.get("_floatValue", 1.0),
            customData=data.get("_customData", {}),
        )


@dataclass
class Beatmap(_BytableDataType):
    version: str
    notes: List[Note]
    sliders: List[Slider]
    obstacles: List[Obstacle]
    events: List[Event]
    customData: dict

    @staticmethod
    def from_dict(data: dict):
        notes = data.get("_notes", [])
        sliders = data.get("_sliders", [])
        obstacles = data.get("_obstacles", [])
        events = data.get("_events", [])

        notes = [Note.from_dict(x) for x in notes]
        sliders = [Slider.from_dict(x) for x in sliders]
        obstacles = [Obstacle.from_dict(x) for x in obstacles]
        events = [Event.from_dict(x) for x in events]

        return Beatmap(
            version=data.get("_version", "2.0,0"),
            notes=notes,
            sliders=sliders,
            obstacles=obstacles,
            events=events,
            customData=data.get("_customData", {}),
        )

    def __repr__(self):
        msg = f"Beatmap({len(self.notes)} notes, {len(self.sliders)} sliders, {len(self.obstacles)} obstacles, {len(self.events)} events)"
        return msg


@dataclass
class BeatmapInfo(_BytableDataType):
    difficulty: str
    beatmapFilename: str
    noteJumpMovementSpeed: int
    noteJumpStartBeatOffset: int
    customData: dict
    beatmap: Beatmap

    @staticmethod
    def from_zip(data: dict, zfile: ZipFile):
        beatmapFilename = data["_beatmapFilename"]
        beatmap_data = json.loads(str(zfile.read(beatmapFilename), encoding="utf-8"))
        beatmap = Beatmap.from_dict(beatmap_data)

        return BeatmapInfo(
            difficulty=data["_difficulty"],
            beatmapFilename=beatmapFilename,
            noteJumpMovementSpeed=data["_noteJumpMovementSpeed"],
            noteJumpStartBeatOffset=data["_noteJumpStartBeatOffset"],
            customData=data.get("_customData", {}),
            beatmap=beatmap,
        )

    def __repr__(self):
        msg = f"BeatmapInfo({self.difficulty},"
        msg += f" noteJumpMovementSpeed={self.noteJumpMovementSpeed},"
        msg += f" noteJumpStartBeatOffset={self.noteJumpStartBeatOffset})"
        return msg


@dataclass
class BeatmapSet(_BytableDataType):
    beatmapCharacteristicName: str
    difficultyBeatmaps: List[BeatmapInfo]
    customData: dict

    @staticmethod
    def from_zip(data: dict, zfile: ZipFile):
        difficultyBeatmaps = data.get("_difficultyBeatmaps", [])
        for difficultyBeatmap in difficultyBeatmaps:
            difficultyBeatmap
        difficultyBeatmaps = [BeatmapInfo.from_zip(x, zfile) for x in difficultyBeatmaps]

        return BeatmapSet(
            beatmapCharacteristicName=data["_beatmapCharacteristicName"],
            difficultyBeatmaps=difficultyBeatmaps,
            customData=data.get("_customData", {}),
        )

    def __repr__(self):
        msg = f"BeatmapSet({self.beatmapCharacteristicName}: ["
        msg += ", ".join([bmap.difficulty for bmap in self.difficultyBeatmaps])
        msg += "]"
        return msg


class PyBeatmap:
    def __init__(
        self,
        version: str,
        songName: str,
        songSubName: str,
        songAuthorName: str,
        levelAuthorName: str,
        beatsPerMinute: int,
        songTimeOffset: int,
        shuffle: int,
        shufflePeriod: float,
        perviewStartTime: float,
        previewDuration: float,
        songFilename: str,
        coverImageFilename: str,
        environmentName: str,
        difficultyBeatmapSets: List[BeatmapSet],
        customData: dict,
        song: bytes,
    ):
        self.version = version
        self.songName = songName
        self.songSubName = songSubName
        self.songAuthorName = songAuthorName
        self.levelAuthorName = levelAuthorName
        self.beatsPerMinute = beatsPerMinute
        self.songTimeOffset = songTimeOffset
        self.shuffle = shuffle
        self.shufflePeriod = shufflePeriod
        self.perviewStartTime = perviewStartTime
        self.previewDuration = previewDuration
        self.songFilename = songFilename
        self.coverImageFilename = coverImageFilename
        self.environmentName = environmentName
        self.difficultyBeatmapSets = difficultyBeatmapSets
        self.customData = customData
        self.song = song

    @property
    def bpm(self):
        return self.beatsPerMinute

    @staticmethod
    def from_zip(zip_file_path: PathLike):
        with ZipFile(zip_file_path, "r") as zfile:
            namelist = zfile.namelist()
            namelist_l = [name.lower() for name in namelist]
            idx = namelist_l.index("info.dat")
            assert idx >= 0, "no 'info.dat' file exists"
            info_file_name = namelist[idx]

            info = json.loads(str(zfile.read(info_file_name), encoding="utf-8"))
            difficultyBeatmapSets = info.get("_difficultyBeatmapSets", [])
            difficultyBeatmapSets = [BeatmapSet.from_zip(x, zfile) for x in difficultyBeatmapSets]

            songFilename = info["_songFilename"]
            song = zfile.read(songFilename)

            return PyBeatmap(
                version=info["_version"],
                songName=info["_songName"],
                songSubName=info["_songSubName"],
                songAuthorName=info["_songAuthorName"],
                levelAuthorName=info["_levelAuthorName"],
                beatsPerMinute=info["_beatsPerMinute"],
                songTimeOffset=info["_songTimeOffset"],
                shuffle=info["_shuffle"],
                shufflePeriod=info["_shufflePeriod"],
                perviewStartTime=info.get("_perviewStartTime", 0.0),
                previewDuration=info.get("_previewDuration", 0.0),
                songFilename=songFilename,
                coverImageFilename=info["_coverImageFilename"],
                environmentName=info["_environmentName"],
                difficultyBeatmapSets=difficultyBeatmapSets,
                customData=info.get("_customData", {}),
                song=song,
            )

    def __repr__(self):
        msg = f"PyBeatmap({self.songName}, {self.songSubName} {{\n"
        msg += ",\n".join(["    " + bmapset.__repr__() for bmapset in self.difficultyBeatmapSets])
        msg += "\n}"
        return msg

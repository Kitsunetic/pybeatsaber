import json
from dataclasses import dataclass
from os import PathLike
from typing import List, Union
from zipfile import ZipFile

__all__ = ["Note", "Slider", "Obstacle", "Event", "Beatmap", "BeatmapInfo", "BeatmapSet", "BeatmapLevel", "BeatmapZipFile"]


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
    type: int
    duration: int
    width: int
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

    @staticmethod
    def from_dict(data: dict):
        return Obstacle(
            time=data["_time"],
            lineIndex=data["_lineIndex"],
            type=data["_type"],
            duration=data["_duration"],
            width=data["_width"],
            customData=data.get("_customData", {}),
        )


@dataclass
class Event(_BytableDataType):
    time: int
    type: int
    value: int
    floatValue: float
    customData: dict

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


@dataclass
class BeatmapInfo(_BytableDataType):
    difficulty: str
    beatmapFilename: str
    noteJumpMovementSpeed: int
    noteJumpStartBeatOffset: int
    customData: dict

    @staticmethod
    def from_dict(data: dict):
        return BeatmapInfo(
            difficulty=data["_difficulty"],
            beatmapFilename=data["_beatmapFilename"],
            noteJumpMovementSpeed=data["_noteJumpMovementSpeed"],
            noteJumpStartBeatOffset=data["_noteJumpStartBeatOffset"],
            customData=data.get("_customData", {}),
        )

    def load_beatmap(self, zfile: Union[ZipFile, "BeatmapZipFile"]):
        if isinstance(zfile, BeatmapZipFile):
            zfile = zfile.zfile

        data = json.loads(str(zfile.read(self.beatmapFilename), encoding="utf-8"))
        return Beatmap.from_dict(data)


@dataclass
class BeatmapSet(_BytableDataType):
    beatmapCharacteristicName: str
    difficultyBeatmaps: List[BeatmapInfo]
    customData: dict

    @staticmethod
    def from_dict(data: dict):
        difficultyBeatmaps = data.get("_difficultyBeatmaps", [])
        difficultyBeatmaps = [BeatmapInfo.from_dict(x) for x in difficultyBeatmaps]

        return BeatmapSet(
            beatmapCharacteristicName=data["_beatmapCharacteristicName"],
            difficultyBeatmaps=difficultyBeatmaps,
            customData=data.get("_customData", {}),
        )


@dataclass
class BeatmapLevel(_BytableDataType):
    version: str
    songName: str
    songSubName: str
    songAuthorName: str
    levelAuthorName: str
    beatsPerMinute: int
    songTimeOffset: int
    shuffle: int
    shufflePeriod: float
    perviewStartTime: float
    previewDuration: float
    songFilename: str
    coverImageFilename: str
    environmentName: str
    difficultyBeatmapSets: List[BeatmapSet]
    customData: dict

    @property
    def bpm(self):
        return self.beatsPerMinute

    @staticmethod
    def from_dict(data: dict):
        difficultyBeatmapSets = data.get("_difficultyBeatmapSets", [])
        difficultyBeatmapSets = [BeatmapSet.from_dict(x) for x in difficultyBeatmapSets]

        return BeatmapLevel(
            version=data["_version"],
            songName=data["_songName"],
            songSubName=data["_songSubName"],
            songAuthorName=data["_songAuthorName"],
            levelAuthorName=data["_levelAuthorName"],
            beatsPerMinute=data["_beatsPerMinute"],
            songTimeOffset=data["_songTimeOffset"],
            shuffle=data["_shuffle"],
            shufflePeriod=data["_shufflePeriod"],
            perviewStartTime=data.get("_perviewStartTime", 0.0),
            previewDuration=data.get("_previewDuration", 0.0),
            songFilename=data["_songFilename"],
            coverImageFilename=data["_coverImageFilename"],
            environmentName=data["_environmentName"],
            difficultyBeatmapSets=difficultyBeatmapSets,
            customData=data.get("_customData", {}),
        )


class BeatmapContainer:
    def __init__(self, zfile_path: PathLike, mode="r"):
        self._zfile_path = str(zfile_path)
        self._mode = mode

        self.zfile = ZipFile(self._zfile_path, mode=mode)

        namelist = self.zfile.namelist()
        namelist_l = [name.lower() for name in namelist]
        idx = namelist_l.index("info.dat")
        assert idx >= 0
        info_file_name = namelist[idx]

        data = json.loads(str(self.zfile.read(info_file_name), encoding="utf-8"))
        self.info = BeatmapLevel.from_dict(data)

    def close(self):
        self.zfile.close()

    def __enter__(self):
        pass

    def __exit__(self):
        self.close()

    def __repr__(self) -> str:
        return f"BeatmapZipFile(zfile_path='{self._zfile_path}', mode='{self._mode}')"

    def song_file(self) -> bytes:
        return self.zfile.read(self.info.songFilename)

    def get_beatmap_set(self, beatmapCharacteristicName="Standard") -> BeatmapSet:
        for beatmap_set in self.info.difficultyBeatmapSets:
            if beatmap_set.beatmapCharacteristicName == beatmapCharacteristicName:
                return beatmap_set

    def get_beatmaps(self, beatmapCharacteristicName="Standard") -> List[BeatmapInfo]:
        beatmap_set = self.get_beatmap_set(beatmapCharacteristicName)
        if beatmap_set is None:
            return []

        else:
            return beatmap_set.difficultyBeatmaps

    @property
    def filelist(self):
        return self.zfile.filelist

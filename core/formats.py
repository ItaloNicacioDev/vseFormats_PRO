from dataclasses import dataclass

@dataclass(frozen=True)
class FormatPreset:
    id: str
    name: str
    category: str
    width: int
    height: int
    aspect: str
    description: str = ""

PRESETS = (
    FormatPreset("youtube_720p", "YouTube 720p", "YouTube", 1280, 720, "16:9"),
    FormatPreset("youtube_1080p", "YouTube 1080p", "YouTube", 1920, 1080, "16:9"),
    FormatPreset("youtube_1440p", "YouTube 1440p", "YouTube", 2560, 1440, "16:9"),
    FormatPreset("youtube_4k", "YouTube 4K", "YouTube", 3840, 2160, "16:9"),
    FormatPreset("youtube_8k", "YouTube 8K", "YouTube", 7680, 4320, "16:9"),
    FormatPreset("vertical_720", "Vertical 720", "Vertical", 720, 1280, "9:16"),
    FormatPreset("vertical_1080", "Vertical 1080", "Vertical", 1080, 1920, "9:16"),
    FormatPreset("vertical_4k", "Vertical 4K", "Vertical", 2160, 3840, "9:16"),
    FormatPreset("tiktok_1080", "TikTok / Reels / Shorts", "Social", 1080, 1920, "9:16"),
    FormatPreset("square_1080", "Square 1080", "Square", 1080, 1080, "1:1"),
    FormatPreset("square_1350", "Social Portrait", "Square", 1080, 1350, "4:5"),
    FormatPreset("widescreen_qhd", "Widescreen QHD", "Widescreen", 2560, 1440, "16:9"),
    FormatPreset("widescreen_3440", "Ultrawide", "Widescreen", 3440, 1440, "21:9"),
    FormatPreset("cinema_185", "Cinema 1.85", "Cinema", 1998, 1080, "1.85:1"),
    FormatPreset("cinema_239", "Cinema 2.39", "Cinema", 2048, 858, "2.39:1"),
    FormatPreset("cinema_4k_239", "Cinema 4K 2.39", "Cinema", 4096, 1716, "2.39:1"),
    FormatPreset("multicam_1080", "Multicam 1080p", "Multicam", 1920, 1080, "16:9"),
    FormatPreset("multicam_4k", "Multicam 4K", "Multicam", 3840, 2160, "16:9"),
)

CATEGORIES = ("YouTube", "Social", "Vertical", "Cinema", "Multicam", "Widescreen", "Square")


def get_preset(preset_id):
    return next((p for p in PRESETS if p.id == preset_id), None)


def presets_for_category(category):
    return tuple(p for p in PRESETS if p.category == category)


def active_preset_id(scene):
    width = round(scene.render.resolution_x * scene.render.resolution_percentage / 100)
    height = round(scene.render.resolution_y * scene.render.resolution_percentage / 100)
    for p in PRESETS:
        if p.width == width and p.height == height:
            return p.id
    return ""

FPS_PRESETS = (
    ("23.976", 24000, 1001),
    ("24", 24, 1),
    ("25", 25, 1),
    ("29.97", 30000, 1001),
    ("30", 30, 1),
    ("48", 48, 1),
    ("50", 50, 1),
    ("59.94", 60000, 1001),
    ("60", 60, 1),
    ("120", 120, 1),
)


def fps_value(numerator, denominator):
    return numerator / denominator


def set_scene_fps(scene, numerator, denominator):
    scene.render.fps = numerator
    scene.render.fps_base = denominator


def current_fps(scene):
    return scene.render.fps / scene.render.fps_base


def nearest_fps_id(scene):
    value = current_fps(scene)
    return min(FPS_PRESETS, key=lambda item: abs(fps_value(item[1], item[2]) - value))[0]

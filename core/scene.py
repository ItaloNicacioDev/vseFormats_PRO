from .fps import set_scene_fps
from .formats import get_preset


def apply_preset(scene, preset_id, fps_num=None, fps_den=None):
    preset = get_preset(preset_id)
    if preset is None:
        raise ValueError(f"Unknown preset: {preset_id}")
    render = scene.render
    render.resolution_x = preset.width
    render.resolution_y = preset.height
    render.resolution_percentage = 100
    if fps_num is not None and fps_den is not None:
        set_scene_fps(scene, fps_num, fps_den)
    scene.vse_formats.last_preset = preset.id
    return preset

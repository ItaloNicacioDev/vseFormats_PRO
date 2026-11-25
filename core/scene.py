from .fps import set_scene_fps
from .formats import get_preset
from .timeline_range import apply_timeline_range, get_max_frame_end


def apply_preset(scene, preset_id, fps_num=None, fps_den=None):
    preset = get_preset(preset_id)
    if preset is None:
        raise ValueError(f"Unknown preset: {preset_id}")
    render = scene.render
    render.resolution_x = preset.width
    render.resolution_y = preset.height
    if fps_num is not None and fps_den is not None:
        if fps_den == 0:
            fps_den = 1
        set_scene_fps(scene, fps_num, fps_den)
    vse_formats = getattr(scene, "vse_formats", None)
    if vse_formats is not None:
        if fps_num is not None:
            vse_formats.fps_numerator = int(fps_num)
        if fps_den is not None:
            vse_formats.fps_denominator = int(fps_den)
        vse_formats.last_preset = preset.id
    # Sincroniza frame_end com o conteúdo existente, se houver
    try:
        max_frame = get_max_frame_end(scene)
        if max_frame > 0:
            apply_timeline_range(scene, max_frame)
    except Exception:
        pass
    return preset

"""Auto Timeline Range — ajuste automático do final do playback do VSE.

Acompanha o maior frame final ocupado pelos strips e estende
scene.frame_end para comportar esse conteúdo, com margem visual.
Inspirado no comportamento "auto fit" do Adobe Premiere Pro.

Não altera duração, FPS, resolução nem posição dos clipes.
Só aumenta o frame_end; nunca diminui automaticamente (evita cortar o playback).
"""

import bpy

MARGIN_DEFAULT = 100


def get_max_frame_end(scene):
    """Retorna o maior frame final ocupado pelos strips na timeline.

    Considera a posição real dos strips (left/right handle), não a soma de
    durações. Suporta os nomes de propriedade do Blender 5.1+ (right_handle)
    com fallback para os nomes anteriores (frame_final_end).
    """
    seq = scene.sequence_editor
    if seq is None:
        return 0

    max_end = 0
    for strip in seq.strips_all:
        end = getattr(strip, "right_handle", None)
        if end is None:
            end = getattr(strip, "frame_final_end", 0)
        try:
            end = int(end)
        except (TypeError, ValueError):
            end = 0
        if end > max_end:
            max_end = end
    return max_end


def apply_timeline_range(context, max_frame, margin=MARGIN_DEFAULT):
    """Estende scene.frame_end para max_frame + margem, se ainda não cobrir."""
    scene = context.scene
    if scene is None:
        return False

    target = int(max_frame) + int(margin)
    if scene.frame_end < target:
        scene.frame_end = target
        return True
    return False


class AutoFitState:
    """Estado do auto fit (mantido fora de bpy.props para não poluir Scene)."""

    enabled = False
    last_max_frame = 0
    timer_registered = False


def _auto_fit_timer():
    """Callback do timer do Blender. Verifica mudanças no maior frame final."""
    scene = bpy.context.scene
    if scene is None:
        return 0.5

    seq = scene.sequence_editor
    if seq is None:
        return 0.5

    if not getattr(scene.vse_formats, "auto_fit_enabled", True):
        AutoFitState.last_max_frame = 0
        return 0.5

    max_frame = get_max_frame_end(scene)
    if max_frame > 0 and max_frame != AutoFitState.last_max_frame:
        AutoFitState.last_max_frame = max_frame
        apply_timeline_range(bpy.context, max_frame)

    return 0.5


def start_auto_fit_timer():
    if AutoFitState.timer_registered:
        return
    try:
        bpy.app.timers.register(_auto_fit_timer, persistent=True)
        AutoFitState.timer_registered = True
    except Exception:
        pass


def stop_auto_fit_timer():
    if not AutoFitState.timer_registered:
        return
    try:
        if bpy.app.timers.is_registered(_auto_fit_timer):
            bpy.app.timers.unregister(_auto_fit_timer)
    except Exception:
        pass
    AutoFitState.timer_registered = False
    AutoFitState.last_max_frame = 0

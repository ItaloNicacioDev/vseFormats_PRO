"""Auto Timeline Range — ajuste automático do enquadramento horizontal do VSE.

Calcula o maior frame final ocupado pelos strips e enquadra a timeline do
Video Sequencer para comportar esse conteúdo, com margem visual opcional.
Inspirado no comportamento "auto fit" do Adobe Premiere Pro.

Não altera duração, FPS, resolução nem posição dos clipes.
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


def _find_vse_window_area_region(context):
    """Localiza a primeira área SEQUENCE_EDITOR com região WINDOW."""
    for window in context.window_manager.windows:
        screen = window.screen
        if not screen:
            continue
        for area in screen.areas:
            if area.type != 'SEQUENCE_EDITOR':
                continue
            for region in area.regions:
                if region.type == 'WINDOW':
                    return window, area, region
    return None


def apply_timeline_range(context, max_frame, margin=MARGIN_DEFAULT):
    """Ajusta o enquadramento horizontal do VSE para max_frame + margem.

    Usa bpy.ops.sequencer.view_all() (caminho nativo e confiável) e, quando
    possível, amplia o xmax do View2D para incluir a margem visual.
    """
    found = _find_vse_window_area_region(context)
    if not found:
        return False

    window, area, region = found

    override = {
        'window': window,
        'screen': window.screen,
        'area': area,
        'region': region,
    }

    try:
        with bpy.context.temp_override(**override):
            bpy.ops.sequencer.view_all()
    except Exception:
        return False

    # Tenta aplicar margem extra no final via View2D (pode não ser gravável
    # em todas as versões do Blender; se falhar, view_all já enquadrou).
    try:
        v2d = region.view2d
        cur = v2d.cur
        target_xmax = float(max_frame) + float(margin)
        if cur.xmax < target_xmax:
            cur.xmax = target_xmax
        region.tag_redraw()
    except Exception:
        pass

    return True


class AutoFitState:
    """Estado do auto fit (mantido fora de bpy.props para não poluir Scene)."""

    enabled = False
    last_max_frame = 0
    timer_registered = False


def _auto_fit_timer():
    """Callback do timer do Blender. Verifica mudanças no maior frame final."""
    scene = bpy.context.scene
    if scene is None or scene.sequence_editor is None:
        return 0.5

    if not getattr(scene.vse_formats, "auto_fit_enabled", False):
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

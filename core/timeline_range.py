"""Auto Timeline Range — ajuste automático do final do playback do VSE.

Acompanha o maior frame final ocupado pelos strips e estende
scene.frame_end para comportar esse conteúdo, com margem visual.
Inspirado no comportamento "auto fit" do Adobe Premiere Pro.

Totalmente automático: sem botões, sem popup, sem intervenção do usuário.
Não altera duração, FPS, resolução nem posição dos clipes.
Só aumenta o frame_end; nunca diminui automaticamente (evita cortar o playback).
"""

import bpy

MARGIN_DEFAULT = 100


def get_max_frame_end(scene):
    """Retorna o maior frame final ocupado pelos strips na timeline.

    Considera a posição real dos strips (right/left handle), não a soma de
    durações. Suporta nomes do Blender 5.1+ (right_handle) com fallback para
    nomes anteriores (frame_final_end).
    """
    seq = getattr(scene, "sequence_editor", None)
    if seq is None:
        return 0

    max_end = 0
    strips = getattr(seq, "strips_all", None)
    if strips is None:
        strips = getattr(seq, "sequences", [])

    for strip in strips:
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


def get_min_frame_start(scene):
    """Retorna o menor frame inicial ocupado pelos strips na timeline."""
    seq = getattr(scene, "sequence_editor", None)
    if seq is None:
        return 0

    strips = getattr(seq, "strips_all", None)
    if strips is None:
        strips = getattr(seq, "sequences", [])

    min_start = None
    for strip in strips:
        start = getattr(strip, "frame_final_start", None)
        if start is None:
            start = getattr(strip, "left_handle", None)
        try:
            start = int(start)
        except (TypeError, ValueError):
            continue
        if min_start is None or start < min_start:
            min_start = start
    return min_start if min_start is not None else 0


class AutoFitState:
    """Estado do auto fit (mantido fora de bpy.props para não poluir Scene)."""

    enabled = True
    last_max_frame = 0
    timer_registered = False
    handler_registered = False
    _is_adjusting = False


def apply_timeline_range(scene, max_frame, margin=MARGIN_DEFAULT):
    """Estende scene.frame_end para max_frame + margem, se ainda não cobrir."""
    if scene is None:
        return False

    target = int(max_frame) + int(margin)
    if scene.frame_end < target:
        scene.frame_end = target
        return True
    return False


def _check_and_fit():
    """Executa a verificação e ajuste do frame_end (usado por timer e handler)."""
    try:
        scene = bpy.context.scene
        if scene is None:
            return

        vse_formats = getattr(scene, "vse_formats", None)
        if vse_formats is None or not getattr(vse_formats, "auto_fit_enabled", True):
            AutoFitState.last_max_frame = 0
            return

        if AutoFitState._is_adjusting:
            return

        max_frame = get_max_frame_end(scene)
        if max_frame > 0 and max_frame != AutoFitState.last_max_frame:
            AutoFitState._is_adjusting = True
            try:
                AutoFitState.last_max_frame = max_frame
                apply_timeline_range(scene, max_frame)
                # Ajusta frame_start para o menor frame ocupado pelos strips
                min_start = get_min_frame_start(scene)
                if min_start > 0 and scene.frame_start > min_start:
                    scene.frame_start = min_start
            finally:
                AutoFitState._is_adjusting = False
    except Exception as exc:
        print(f"[VSE Formats Pro] Auto Fit error: {exc}")


def _auto_fit_timer():
    """Callback do timer do Blender. Verifica mudanças no maior frame final."""
    _check_and_fit()
    return 0.05


def _depsgraph_handler(scene, depsgraph):
    """Handler do depsgraph: dispara ajuste imediatamente ao mudar a cena."""
    _check_and_fit()


def start_auto_fit_timer():
    if AutoFitState.timer_registered:
        return
    try:
        bpy.app.timers.register(_auto_fit_timer, persistent=True, first_interval=0.0)
        AutoFitState.timer_registered = True
    except Exception:
        pass


def start_auto_fit_handler():
    if AutoFitState.handler_registered:
        return
    try:
        bpy.app.handlers.depsgraph_update_post.append(_depsgraph_handler)
        AutoFitState.handler_registered = True
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


def stop_auto_fit_handler():
    if not AutoFitState.handler_registered:
        return
    try:
        bpy.app.handlers.depsgraph_update_post.remove(_depsgraph_handler)
    except (ValueError, AttributeError):
        pass
    AutoFitState.handler_registered = False


def stop_auto_fit():
    stop_auto_fit_timer()
    stop_auto_fit_handler()
    AutoFitState.last_max_frame = 0

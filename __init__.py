bl_info = {
    "name": "VSE Formats Pro",
    "author": "Italo Nicacio Dev",
    "version": (4, 2, 6),
    "blender": (5, 0, 0),
    "location": "Video Sequencer > Sidebar > VSE Formats",
    "description": "Production format presets for the Blender Video Sequencer with independent FPS control.",
    "category": "Sequencer",
}

from .operators.format_ops import CLASSES as FORMAT_CLASSES
from .operators.preset_ops import CLASSES as PRESET_CLASSES
from .ui.panels import CLASSES as PANEL_CLASSES
from .ui.header import register_header, unregister_header
from .ui.format_launcher import CLASSES as LAUNCHER_CLASSES
from .core import state
from .core import timeline_range

_CLASSES = FORMAT_CLASSES + PRESET_CLASSES + PANEL_CLASSES + LAUNCHER_CLASSES


def register():
    import bpy
    state.register()
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    register_header()
    # Inicia o timer de Auto Fit automaticamente (ativado por padrão).
    timeline_range.start_auto_fit_timer()
    # O watcher automático do launcher não é iniciado por padrão:
    # abrir um popup não solicitado ao entrar no VSE é intrusivo.
    # start_launcher_watcher() pode ser chamado manualmente quando desejado.
    print("[VSE Formats Pro 4.0] Registered for Blender 5.x+")


def unregister():
    unregister_header()
    import bpy
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
    timeline_range.stop_auto_fit_timer()
    state.unregister()
    print("[VSE Formats Pro 4.0] Unregistered")


if __name__ == "__main__":
    register()

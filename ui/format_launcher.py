import bpy
from bpy.types import Operator
from ..core.formats import CATEGORIES, presets_for_category, get_preset
from ..core.fps import FPS_PRESETS, current_fps


class VSEF_OT_ShowLauncher(Operator):
    bl_idname = "vsef.show_launcher"
    bl_label = "VSE Formats"
    bl_description = "Choose a video format for the current VSE project"

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=520)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        r = scene.render
        fps = current_fps(scene)

        active = scene.vse_formats.last_preset
        active_preset = get_preset(active) if active else None

        title = layout.row()
        title.scale_y = 1.35
        title.label(text="VSE FORMATS", icon='FILE_MOVIE')

        subtitle = layout.row()
        subtitle.label(
            text="Choose your project format",
            icon='IMAGE_DATA'
        )

        current = layout.box()
        current.label(
            text="CURRENT PROJECT",
            icon='CHECKMARK'
        )

        row = current.row(align=True)
        row.label(
            text=f"{r.resolution_x} × {r.resolution_y}"
        )
        row.label(
            text=f"{fps:.3f} FPS",
            icon='TIME'
        )

        if active_preset:
            current.label(
                text=f"{active_preset.name}  •  {active_preset.aspect}"
            )
        else:
            current.label(
                text="Custom format"
            )

        layout.separator(factor=0.7)

        layout.label(
            text="FPS",
            icon='TIME'
        )

        fps_grid = layout.grid_flow(
            columns=5,
            even_columns=True,
            align=True
        )

        for label, num, den in FPS_PRESETS:
            op = fps_grid.operator(
                'vsef.set_fps',
                text=label,
                depress=abs(fps - num / den) < 0.0005,
            )

            op.numerator = num
            op.denominator = den

        layout.separator(factor=0.8)

        for category in CATEGORIES:

            presets = presets_for_category(category)

            if not presets:
                continue

            box = layout.box()

            header = box.row()
            header.label(
                text=category.upper(),
                icon='FILE_MOVIE'
            )

            grid = box.grid_flow(
                columns=2,
                even_columns=True,
                align=True
            )

            for preset in presets:

                is_active = preset.id == active

                op = grid.operator(
                    'vsef.apply_format',
                    text=preset.name,
                    icon='CHECKMARK' if is_active else 'NONE',
                    depress=is_active,
                )

                op.preset_id = preset.id
                op.fps_numerator = r.fps
                op.fps_denominator = r.fps_base


CLASSES = (
    VSEF_OT_ShowLauncher,
)


_last_area_types = {}
_timer_running = False


def _scan_vse_areas():

    global _timer_running

    _timer_running = False

    try:
        windows = bpy.context.window_manager.windows
    except Exception:
        return None

    seen = set()

    for window in windows:

        screen = window.screen

        if not screen:
            continue

        for area in screen.areas:

            key = (
                window.as_pointer(),
                area.as_pointer()
            )

            seen.add(key)

            previous = _last_area_types.get(key)
            current = area.type

            _last_area_types[key] = current

            # Entrou em uma área do Video Sequencer
            if (
                current == 'SEQUENCE_EDITOR'
                and previous != 'SEQUENCE_EDITOR'
            ):

                region = next(
                    (
                        r
                        for r in area.regions
                        if r.type == 'WINDOW'
                    ),
                    None
                )

                if region is None:
                    continue

                try:

                    with bpy.context.temp_override(
                        window=window,
                        area=area,
                        region=region
                    ):

                        bpy.ops.vsef.show_launcher(
                            'INVOKE_DEFAULT'
                        )

                except Exception as exc:

                    print(
                        f"[VSE Formats Pro] "
                        f"Launcher could not open: {exc}"
                    )

    # Remove áreas que não existem mais
    for key in tuple(_last_area_types):

        if key not in seen:
            del _last_area_types[key]

    return 0.35


def start_launcher_watcher():

    global _timer_running

    if _timer_running:
        return

    _timer_running = True

    bpy.app.timers.register(
        _scan_vse_areas,
        first_interval=0.5,
        persistent=True
    )


def stop_launcher_watcher():

    global _timer_running

    _timer_running = False

    try:

        if bpy.app.timers.is_registered(
            _scan_vse_areas
        ):

            bpy.app.timers.unregister(
                _scan_vse_areas
            )

    except Exception:
        pass

    _last_area_types.clear()
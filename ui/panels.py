import bpy
from bpy.types import Panel
from ..core.formats import CATEGORIES, presets_for_category, active_preset_id, get_preset
from ..core.fps import FPS_PRESETS, current_fps

class VSEF_PT_Main(Panel):
    bl_label = "VSE Formats Pro"
    bl_idname = "VSEF_PT_main"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'VSE Formats'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        r = scene.render
        w = round(r.resolution_x * r.resolution_percentage / 100)
        h = round(r.resolution_y * r.resolution_percentage / 100)
        fps = current_fps(scene)
        active = active_preset_id(scene)

        box = layout.box()
        box.label(text="CURRENT PROJECT", icon='FILE_MOVIE')
        row = box.row(); row.scale_y = 1.2
        row.label(text=f"{w} × {h}", icon='IMAGE_DATA')
        row.label(text=f"{fps:.3f} FPS", icon='TIME')
        if active:
            preset = get_preset(active)
            box.label(text=f"{preset.name}  •  {preset.aspect}", icon='CHECKMARK')
        else:
            box.label(text="Custom format", icon='PREFERENCES')

        layout.separator(factor=0.5)
        layout.label(text="FPS", icon='TIME')
        grid = layout.grid_flow(columns=3, even_columns=True, align=True)
        for label, num, den in FPS_PRESETS:
            op = grid.operator('vsef.set_fps', text=label, depress=abs(fps - num / den) < 0.0005)
            op.numerator = num; op.denominator = den

        layout.separator(factor=0.6)
        for category in CATEGORIES:
            presets = presets_for_category(category)
            box = layout.box()
            box.label(text=category, icon='FILE_MOVIE')
            grid = box.grid_flow(columns=1, align=True)
            for preset in presets:
                row = grid.row(align=True)
                is_active = preset.id == active
                op = row.operator('vsef.apply_format', text=preset.name, icon='CHECKMARK' if is_active else 'NONE', depress=is_active)
                op.preset_id = preset.id
                op.fps_numerator = r.fps
                op.fps_denominator = r.fps_base
                row.label(text=f"{preset.width} × {preset.height}  •  {preset.aspect}")

        layout.separator(factor=0.5)
        row = layout.row(align=True)
        row.operator('vsef.copy_current_resolution', text='Copy Resolution', icon='COPY_ID')
        row.operator('vsef.reset_project', text='Reset State', icon='FILE_REFRESH')


CLASSES = (VSEF_PT_Main,)

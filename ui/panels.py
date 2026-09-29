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

        # Current project
        box = layout.box()
        box.label(text="CURRENT PROJECT", icon='FILE_MOVIE')
        row = box.row(align=True)
        row.label(text=f"{w} × {h}", icon='IMAGE_DATA')
        row.label(text=f"{fps:.3f} FPS", icon='TIME')
        if active:
            preset = get_preset(active)
            box.label(text=f"{preset.name}  •  {preset.aspect}", icon='CHECKMARK')
        else:
            box.label(text="Custom format", icon='PREFERENCES')

        # Compact format switching while editing.
        switch = layout.box()
        switch.label(text="QUICK FORMAT", icon='FILE_MOVIE')
        row = switch.row(align=True)

        if w > h:
            op = row.operator('vsef.switch_orientation', text='9:16', icon='FORWARD')
            op.orientation = 'PORTRAIT'
            op = row.operator('vsef.switch_orientation', text='1:1', icon='SNAP_FACE')
            op.orientation = 'SQUARE'
        elif h > w:
            op = row.operator('vsef.switch_orientation', text='16:9', icon='BACK')
            op.orientation = 'LANDSCAPE'
            op = row.operator('vsef.switch_orientation', text='1:1', icon='SNAP_FACE')
            op.orientation = 'SQUARE'
        else:
            op = row.operator('vsef.switch_orientation', text='16:9', icon='FORWARD')
            op.orientation = 'LANDSCAPE'
            op = row.operator('vsef.switch_orientation', text='9:16', icon='FORWARD')
            op.orientation = 'PORTRAIT'

        # FPS and format presets are separate collapsible child panels below.

        row = layout.row(align=True)
        row.operator('vsef.copy_current_resolution', text='Copy', icon='COPY_ID')
        row.operator('vsef.reset_project', text='Reset', icon='FILE_REFRESH')


class VSEF_PT_FPS(Panel):
    bl_label = "FPS"
    bl_idname = "VSEF_PT_fps"
    bl_parent_id = "VSEF_PT_main"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'VSE Formats'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        fps = current_fps(scene)

        grid = layout.grid_flow(columns=3, even_columns=True, align=True)
        for label, num, den in FPS_PRESETS:
            op = grid.operator(
                'vsef.set_fps',
                text=label,
                depress=abs(fps - num / den) < 0.0005,
            )
            op.numerator = int(num)
            op.denominator = int(den)


def _make_category_panel(category, index):
    safe = ''.join(c if c.isalnum() else '_' for c in category).lower()

    class CategoryPanel(Panel):
        bl_label = category
        bl_idname = f"VSEF_PT_category_{index}_{safe}"
        bl_parent_id = "VSEF_PT_main"
        bl_space_type = 'SEQUENCE_EDITOR'
        bl_region_type = 'UI'
        bl_category = 'VSE Formats'
        bl_options = {'DEFAULT_CLOSED'}

        @classmethod
        def poll(cls, context):
            return bool(presets_for_category(category))

        def draw(self, context):
            layout = self.layout
            scene = context.scene
            r = scene.render
            active = active_preset_id(scene)

            # Two columns keep preset lists compact.
            grid = layout.grid_flow(columns=2, even_columns=True, align=True)
            for preset in presets_for_category(category):
                is_active = preset.id == active
                op = grid.operator(
                    'vsef.apply_format',
                    text=preset.name,
                    icon='CHECKMARK' if is_active else 'NONE',
                    depress=is_active,
                )
                op.preset_id = preset.id
                op.fps_numerator = int(r.fps)
                op.fps_denominator = int(round(r.fps_base))

    CategoryPanel.__name__ = f"VSEF_PT_Category_{index}_{safe}"
    return CategoryPanel


_CATEGORY_PANELS = tuple(
    _make_category_panel(category, index)
    for index, category in enumerate(CATEGORIES)
)


CLASSES = (VSEF_PT_Main, VSEF_PT_FPS) + _CATEGORY_PANELS

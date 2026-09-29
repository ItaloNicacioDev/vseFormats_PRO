import bpy
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty
from ..core.scene import apply_preset
from ..core.formats import get_preset


class VSEF_OT_ApplyFormat(Operator):
    bl_idname = "vsef.apply_format"
    bl_label = "Apply Format"
    bl_options = {'REGISTER', 'UNDO'}

    preset_id: StringProperty()
    fps_numerator: IntProperty(default=30)
    fps_denominator: IntProperty(default=1)

    def execute(self, context):
        preset = get_preset(self.preset_id)
        if not preset:
            self.report({'ERROR'}, "Unknown format preset")
            return {'CANCELLED'}
        try:
            apply_preset(
                context.scene,
                self.preset_id,
                self.fps_numerator,
                self.fps_denominator,
            )
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report(
            {'INFO'},
            f"{preset.name}: {preset.width} × {preset.height} @ "
            f"{self.fps_numerator / self.fps_denominator:.3f} FPS",
        )
        return {'FINISHED'}


class VSEF_OT_SetFPS(Operator):
    bl_idname = "vsef.set_fps"
    bl_label = "Set FPS"
    bl_options = {'REGISTER', 'UNDO'}

    numerator: IntProperty(min=1)
    denominator: IntProperty(min=1)

    def execute(self, context):
        context.scene.render.fps = self.numerator
        context.scene.render.fps_base = self.denominator
        context.scene.vse_formats.fps_numerator = self.numerator
        context.scene.vse_formats.fps_denominator = self.denominator
        return {'FINISHED'}


class VSEF_OT_SwitchOrientation(Operator):
    """Switch the current project between landscape and portrait."""

    bl_idname = "vsef.switch_orientation"
    bl_label = "Switch Orientation"
    bl_options = {'REGISTER', 'UNDO'}

    orientation: bpy.props.EnumProperty(
        name="Orientation",
        items=(
            ('LANDSCAPE', "16:9 Landscape", "Switch to a landscape project"),
            ('PORTRAIT', "9:16 Vertical", "Switch to a vertical project"),
            ('SQUARE', "1:1 Square", "Switch to a square project"),
        ),
        default='PORTRAIT',
    )

    def execute(self, context):
        scene = context.scene
        render = scene.render
        width = max(1, int(render.resolution_x))
        height = max(1, int(render.resolution_y))

        if self.orientation == 'PORTRAIT':
            # Preserve the current resolution while rotating it.
            if width > height:
                render.resolution_x, render.resolution_y = height, width
            elif width == height:
                # A square has no orientation, so use a practical vertical default.
                render.resolution_x, render.resolution_y = 1080, 1920

        elif self.orientation == 'LANDSCAPE':
            if height > width:
                render.resolution_x, render.resolution_y = height, width
            elif width == height:
                render.resolution_x, render.resolution_y = 1920, 1080

        elif self.orientation == 'SQUARE':
            side = min(width, height)
            render.resolution_x = side
            render.resolution_y = side

        # Percentage is kept intact; only the project dimensions change.
        scene.vse_formats.last_preset = ""
        return {'FINISHED'}


CLASSES = (
    VSEF_OT_ApplyFormat,
    VSEF_OT_SetFPS,
    VSEF_OT_SwitchOrientation,
)

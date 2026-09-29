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
            apply_preset(context.scene, self.preset_id, self.fps_numerator, self.fps_denominator)
        except Exception as exc:
            self.report({'ERROR'}, str(exc))
            return {'CANCELLED'}
        self.report({'INFO'}, f"{preset.name}: {preset.width} × {preset.height} @ {self.fps_numerator / self.fps_denominator:.3f} FPS")
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


CLASSES = (VSEF_OT_ApplyFormat, VSEF_OT_SetFPS)

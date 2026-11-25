import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from ..core.formats import get_preset

class VSEF_OT_ResetProject(Operator):
    bl_idname = "vsef.reset_project"
    bl_label = "Reset VSE Formats State"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.vse_formats.last_preset = ""
        scene.vse_formats.fps_numerator = 30
        scene.vse_formats.fps_denominator = 1
        # Reset de resolução e frame_end para valores padrão
        render = scene.render
        render.resolution_x = 1920
        render.resolution_y = 1080
        render.resolution_percentage = 100
        try:
            scene.frame_end = 250
        except Exception:
            pass
        return {'FINISHED'}


class VSEF_OT_CopyCurrentResolution(Operator):
    bl_idname = "vsef.copy_current_resolution"
    bl_label = "Copy Current Resolution"

    def execute(self, context):
        r = context.scene.render
        w = round(r.resolution_x * r.resolution_percentage / 100)
        h = round(r.resolution_y * r.resolution_percentage / 100)
        context.window_manager.clipboard = f"{w} × {h}"
        self.report({'INFO'}, f"Copied: {w} × {h}")
        return {'FINISHED'}


CLASSES = (VSEF_OT_ResetProject, VSEF_OT_CopyCurrentResolution)

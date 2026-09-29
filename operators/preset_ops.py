import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from ..core.formats import get_preset

class VSEF_OT_ResetProject(Operator):
    bl_idname = "vsef.reset_project"
    bl_label = "Reset VSE Formats State"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.scene.vse_formats.last_preset = ""
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

import bpy
from bpy.props import StringProperty, IntProperty

class VSEFormatsProperties(bpy.types.PropertyGroup):
    last_preset: StringProperty(default="youtube_1080p")
    fps_numerator: IntProperty(default=30, min=1)
    fps_denominator: IntProperty(default=1, min=1)


def register():
    bpy.utils.register_class(VSEFormatsProperties)
    bpy.types.Scene.vse_formats = bpy.props.PointerProperty(type=VSEFormatsProperties)


def unregister():
    del bpy.types.Scene.vse_formats
    bpy.utils.unregister_class(VSEFormatsProperties)

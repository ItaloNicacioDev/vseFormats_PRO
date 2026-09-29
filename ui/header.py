import bpy


def draw_vse_formats_menu(self, context):
    if context.space_data.type != 'SEQUENCE_EDITOR':
        return
    layout = self.layout
    layout.separator()
    op = layout.operator('wm.call_panel', text='VSE Formats', icon='FILE_MOVIE')
    op.name = 'VSEF_PT_main'


def register_header():
    # Keep the feature discoverable without replacing Blender's VSE UI.
    bpy.types.SEQUENCER_HT_header.append(draw_vse_formats_menu)


def unregister_header():
    try:
        bpy.types.SEQUENCER_HT_header.remove(draw_vse_formats_menu)
    except (ValueError, AttributeError):
        pass

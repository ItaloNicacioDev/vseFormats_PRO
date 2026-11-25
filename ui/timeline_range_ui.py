"""Interface do Auto Timeline Range: popup flutuante e botão no header do VSE."""

import bpy


def draw_timeline_range_menu(self, context):
    """Adiciona o botão Auto Timeline ao menu existente do header do sequencer."""
    if context.space_data.type != 'SEQUENCE_EDITOR':
        return
    layout = self.layout
    layout.separator()
    layout.operator('vsef.show_timeline_range_popup', text='Auto Timeline', icon='TIME')


def register_header():
    bpy.types.SEQUENCER_HT_header.append(draw_timeline_range_menu)


def unregister_header():
    try:
        bpy.types.SEQUENCER_HT_header.remove(draw_timeline_range_menu)
    except (ValueError, AttributeError):
        pass

"""Operadores do Auto Timeline Range."""

import bpy
from bpy.types import Operator
from ..core.timeline_range import (
    start_auto_fit_timer,
    stop_auto_fit_timer,
    apply_timeline_range,
    get_max_frame_end,
)


class VSEF_OT_ToggleAutoFit(Operator):
    """Ativa/desativa o ajuste automático da timeline ao adicionar ou mover clipes."""

    bl_idname = "vsef.toggle_auto_fit"
    bl_label = "Auto Fit Timeline"
    bl_description = "Liga ou desliga o enquadramento automático da timeline do VSE"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        scene.vse_formats.auto_fit_enabled = not scene.vse_formats.auto_fit_enabled

        if scene.vse_formats.auto_fit_enabled:
            start_auto_fit_timer()
            self.report({'INFO'}, "Auto Fit ativado")
        else:
            stop_auto_fit_timer()
            self.report({'INFO'}, "Auto Fit desativado")
        return {'FINISHED'}


class VSEF_OT_FitContent(Operator):
    """Enquadra a timeline sob demanda para comportar todo o conteúdo existente."""

    bl_idname = "vsef.fit_content"
    bl_label = "Fit Content"
    bl_description = "Recalcula e enquadra toda a timeline ao conteúdo atual"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        max_frame = get_max_frame_end(scene)
        if max_frame <= 0:
            self.report({'WARNING'}, "Nenhum strip encontrado na timeline")
            return {'CANCELLED'}

        ok = apply_timeline_range(context, max_frame)
        if ok:
            self.report({'INFO'}, f"Timeline enquadrada até o frame {max_frame}")
        else:
            self.report({'ERROR'}, "Não foi possível enquadrar a timeline")
            return {'CANCELLED'}
        return {'FINISHED'}


class VSEF_OT_ShowTimelineRangePopup(Operator):
    """Abre a janela flutuante de controle do Auto Timeline Range."""

    bl_idname = "vsef.show_timeline_range_popup"
    bl_label = "Auto Timeline Range"
    bl_description = "Controle de ajuste automático da timeline do VSE"

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=320)

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        enabled = scene.vse_formats.auto_fit_enabled

        row = layout.row(align=True)
        row.scale_y = 1.25
        op = row.operator(
            "vsef.toggle_auto_fit",
            text="Auto Fit",
            icon='PLAY' if enabled else 'PAUSE',
        )
        op.depress = enabled

        row = layout.row(align=True)
        row.scale_y = 1.1
        row.operator("vsef.fit_content", text="Fit Content", icon='ZOOM_ALL')

        layout.separator()

        box = layout.box()
        if enabled:
            box.label(text="Auto Fit: ATIVO", icon='CHECKMARK')
        else:
            box.label(text="Auto Fit: inativo", icon='ERROR')


CLASSES = (
    VSEF_OT_ToggleAutoFit,
    VSEF_OT_FitContent,
    VSEF_OT_ShowTimelineRangePopup,
)

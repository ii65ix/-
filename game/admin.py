from django.contrib import admin

from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "mode", "order", "q_type", "prompt_preview")
    list_filter = ("mode", "q_type")
    search_fields = ("prompt",)
    ordering = ("mode", "order", "id")
    fieldsets = (
        ("أساسي", {"fields": ("mode", "order", "prompt", "q_type")}),
        ("اختيار من متعدد — أسماء الخيارات وفهارس الصحيح", {"fields": ("choices_json", "correct_indices")}),
        ("صح أو خطأ — الإجابة الصحيحة", {"fields": ("correct_tf",)}),
        ("سؤال نصي — rubric (JSON)", {"fields": ("rubric_json",)}),
    )

    @admin.display(description="نص السؤال (مختصر)")
    def prompt_preview(self, obj: Question):
        t = obj.prompt.replace("\n", " ")
        return (t[:70] + "…") if len(t) > 70 else t

    def has_delete_permission(self, request, obj=None):
        """لا حذف من لوحة الإدارة — التعديل والإضافة فقط."""
        return False


admin.site.site_header = "My Responsibilities — إدارة الأسئلة"
admin.site.site_title = "الأسئلة"

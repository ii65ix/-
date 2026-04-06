from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Question(models.Model):
    """أسئلة اللعبة — تُدار من لوحة الإدارة /admin/."""

    MODE_SITUATION = "situation"
    MODE_TRUEFALSE = "truefalse"
    MODE_JOURNEY = "journey"
    MODE_CHOICES = [
        (MODE_SITUATION, "ماذا أفعل؟ (situation)"),
        (MODE_TRUEFALSE, "صح أو خطأ (true/false)"),
        (MODE_JOURNEY, "رحلة المسؤولية (journey)"),
    ]

    TYPE_MC = "mc"
    TYPE_TEXT = "text"
    TYPE_TF = "true_false"
    TYPE_CHOICES = [
        (TYPE_MC, "اختيار من متعدد"),
        (TYPE_TEXT, "إجابة نصية + معيار تقييم (rubric)"),
        (TYPE_TF, "صح/خطأ فقط"),
    ]

    mode = models.CharField("وضع اللعب", max_length=20, choices=MODE_CHOICES, db_index=True)
    order = models.PositiveIntegerField("الترتيب", default=0, help_text="رقم أصغر = يظهر أولاً داخل نفس الوضع.")
    prompt = models.TextField("نص السؤال", help_text="يمكن استخدام أسطر متعددة (عربي/إنجليزي).")
    q_type = models.CharField("نوع السؤال", max_length=20, choices=TYPE_CHOICES, default=TYPE_MC)

    choices_json = models.JSONField("خيارات (للاختيار من متعدد)", default=list, blank=True)
    correct_indices = models.JSONField(
        "الفهارس الصحيحة",
        default=list,
        blank=True,
        help_text='قائمة أرقام الخيارات الصحيحة مثل [0] أو [0,2]. فارغة لنوع "نص".',
    )
    correct_tf = models.BooleanField(
        "الإجابة الصحيحة (صح/خطأ)",
        null=True,
        blank=True,
        help_text="للوضع صح/خطأ فقط: يحدد إن كان «صح» هو الجواب الصحيح.",
    )
    rubric_json = models.JSONField("معيار التقييم (rubric)", null=True, blank=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["mode", "order", "id"]
        verbose_name = "سؤال"
        verbose_name_plural = "الأسئلة"

    def __str__(self):
        return f"[{self.mode}] {self.prompt[:50]}…"

    def clean(self):
        if self.mode == self.MODE_TRUEFALSE:
            if self.q_type != self.TYPE_TF:
                raise ValidationError({"q_type": "وضع صح/خطأ يتطلب نوع «صح/خطأ فقط»."})
            if self.correct_tf is None:
                raise ValidationError({"correct_tf": "حدد إن كانت الإجابة الصحيحة هي «صح» أم «خطأ»."})
        elif self.mode == self.MODE_JOURNEY:
            if self.q_type != self.TYPE_MC:
                raise ValidationError({"q_type": "رحلة المسؤولية تستخدم اختياراً من متعدد فقط."})
            if not self.choices_json:
                raise ValidationError({"choices_json": "أضف الخيارات."})
            if not self.correct_indices:
                raise ValidationError({"correct_indices": "حدد فهرس أو فهارس الإجابات الصحيحة."})
        elif self.mode == self.MODE_SITUATION:
            if self.q_type == self.TYPE_TEXT:
                if self.rubric_json is None:
                    raise ValidationError({"rubric_json": "أسئلة النص تحتاج معيار تقييم (rubric) ككائن JSON."})
            elif self.q_type == self.TYPE_MC:
                if not self.choices_json:
                    raise ValidationError({"choices_json": "أضف خيارين على الأقل."})
                if not self.correct_indices:
                    raise ValidationError({"correct_indices": "حدد الفهرس الصحيح (مثل [0])."})


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="game_profile",
        verbose_name="المستخدم",
    )
    bio = models.TextField("نبذة عنك", blank=True, max_length=500)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "بروفايل"
        verbose_name_plural = "البروفايلات"

    def __str__(self):
        return f"Profile({self.user.username})"


class GameResult(models.Model):
    """نتيجة جولة لعب كاملة (وضع واحد)."""

    MODE_SITUATION = "situation"
    MODE_TRUEFALSE = "truefalse"
    MODE_JOURNEY = "journey"
    MODE_CHOICES = [
        (MODE_SITUATION, "ماذا أفعل؟"),
        (MODE_TRUEFALSE, "صح أو خطأ"),
        (MODE_JOURNEY, "رحلة المسؤولية"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="game_results",
        verbose_name="المستخدم",
    )
    mode = models.CharField("وضع اللعب", max_length=20, choices=MODE_CHOICES, db_index=True)
    score = models.PositiveIntegerField("النقاط")
    created_at = models.DateTimeField("التاريخ", auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "نتيجة لعب"
        verbose_name_plural = "نتائج اللعب"

    def __str__(self):
        return f"{self.user.username} {self.mode} {self.score}"

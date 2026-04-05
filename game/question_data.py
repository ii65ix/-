"""تحويل أسئلة قاعدة البيانات إلى الشكل الذي يتوقعه سكربت اللعبة في المتصفح."""

from __future__ import annotations

from typing import Any

from .models import Question


def _normalize_c(indices: list[int]) -> int | list[int]:
    if len(indices) == 1:
        return indices[0]
    return indices


def build_game_data() -> dict[str, list[dict[str, Any]]]:
    """يُرجع dict بنفس بنية `data` في index.html."""
    out: dict[str, list[dict[str, Any]]] = {"situation": [], "truefalse": [], "journey": []}
    for q in Question.objects.all().order_by("mode", "order", "id"):
        if q.mode == Question.MODE_TRUEFALSE:
            out["truefalse"].append(
                {
                    "q": q.prompt,
                    "answer": "True" if q.correct_tf else "False",
                }
            )
        elif q.mode == Question.MODE_JOURNEY:
            out["journey"].append(
                {
                    "q": q.prompt,
                    "a": q.choices_json,
                    "c": q.correct_indices,
                }
            )
        elif q.mode == Question.MODE_SITUATION:
            if q.q_type == Question.TYPE_TEXT:
                out["situation"].append(
                    {
                        "q": q.prompt,
                        "text": True,
                        "rubric": q.rubric_json or {},
                    }
                )
            else:
                item: dict[str, Any] = {
                    "q": q.prompt,
                    "a": q.choices_json,
                    "c": _normalize_c([int(x) for x in q.correct_indices]),
                }
                out["situation"].append(item)
    return out


def seed_from_dict(data: dict[str, list[dict[str, Any]]]) -> int:
    """يملأ الجدول من قاموس بنفس شكل اللعبة. يُرجع عدد الأسئلة المُنشأة."""
    if Question.objects.exists():
        return 0
    n = 0
    for mode_key, rows in (
        ("situation", data.get("situation") or []),
        ("truefalse", data.get("truefalse") or []),
        ("journey", data.get("journey") or []),
    ):
        for i, row in enumerate(rows, start=1):
            if mode_key == "truefalse":
                ans = row.get("answer", "False")
                Question.objects.create(
                    mode=Question.MODE_TRUEFALSE,
                    order=i,
                    prompt=row["q"],
                    q_type=Question.TYPE_TF,
                    correct_tf=ans == "True",
                )
            elif mode_key == "journey":
                c = row["c"]
                indices = c if isinstance(c, list) else [c]
                Question.objects.create(
                    mode=Question.MODE_JOURNEY,
                    order=i,
                    prompt=row["q"],
                    q_type=Question.TYPE_MC,
                    choices_json=row["a"],
                    correct_indices=[int(x) for x in indices],
                )
            else:
                if row.get("text"):
                    Question.objects.create(
                        mode=Question.MODE_SITUATION,
                        order=i,
                        prompt=row["q"],
                        q_type=Question.TYPE_TEXT,
                        rubric_json=row.get("rubric") or {},
                    )
                else:
                    c = row["c"]
                    indices = c if isinstance(c, list) else [c]
                    Question.objects.create(
                        mode=Question.MODE_SITUATION,
                        order=i,
                        prompt=row["q"],
                        q_type=Question.TYPE_MC,
                        choices_json=row["a"],
                        correct_indices=[int(x) for x in indices],
                    )
            n += 1
    return n

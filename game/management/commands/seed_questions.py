import json
from pathlib import Path

from django.core.management.base import BaseCommand

from game.question_data import seed_from_dict


class Command(BaseCommand):
    help = "Load default questions from game/data/questions_seed.json (only if the table is empty)."

    def handle(self, *args, **options):
        base = Path(__file__).resolve().parent.parent.parent
        path = base / "data" / "questions_seed.json"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        n = seed_from_dict(data)
        if n:
            self.stdout.write(self.style.SUCCESS(f"Seeded {n} questions from questions_seed.json."))
        else:
            self.stdout.write(
                "Questions already exist; nothing added (delete questions in admin to re-seed)."
            )

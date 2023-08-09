import json


class DB:
    def __init__(self, filename):
        self.db = dict()
        self.filename = filename
        try:
            self.load()
        except FileNotFoundError:
            self.dump()

    def __call__(self, *args, **kwargs):
        return self.db

    def load(self):
        with open(self.filename) as f:
            self.db = json.load(f)

    def dump(self):
        with open(self.filename, 'w') as f:
            json.dump(self.db, f, indent=2, ensure_ascii=False)

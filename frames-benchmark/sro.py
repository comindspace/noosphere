from dataclasses import dataclass

from string_utils import is_full_string

@dataclass
class SRO:
    subject: str
    relation: str
    object: str

    def is_full(self) -> bool:
        return is_full_string(self.subject) and is_full_string(self.relation) and is_full_string(self.object)

    @staticmethod
    def replace(string: str, prefix: str) -> str:
        return string.lstrip('0123456789.- ').removeprefix(f"{prefix}:").strip().replace("\'", "\\'")

    def __init__(self, string: str):
        strings = string.splitlines()
        self.subject = ''
        self.relation = ''
        self.object = ''
        if len(strings) >= 3:
            try:
                self.subject = self.replace(strings[0], 'Subject')
                self.relation = self.replace(strings[1], 'Relationship')
                self.object = self.replace(strings[2], 'Object')
            finally:
                pass

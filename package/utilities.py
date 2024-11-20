from typing import Generator, LiteralString

from langchain_core.documents.base import Document

def get_file_contents(name: str) -> str | None:
    """
    Given a name of the file, return the contents of that file.
    """
    try:
        f = open(name, 'r', encoding='utf-8')
        return f.read().strip()
    except FileNotFoundError:
        print("'%s' file not found" % name)
        return None

def removeprefixes(string: str, *words: str) -> str:
    for word in words:
        if len(s := string.removeprefix(word)) < len(string):
            return s
    return string

def process_response(documents: list[Document], *words: list[str]) -> Generator[str, None, None]:
    for line in documents[0].page_content.splitlines():
        if s := removeprefixes(line.strip(), *([f"{w}:" for w in words])).strip():
            yield s

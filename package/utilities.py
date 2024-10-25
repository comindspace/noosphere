def get_file_contents(name: str) -> str:
    "Given a name of the file, return the contents of that file."
    try:
        with open(name, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        print("'%s' file not found" % name)

import os


async def read_file(file_path):
    with open(os.path.join("Docs", file_path), "r", encoding="utf-8") as f:
        return f.read()

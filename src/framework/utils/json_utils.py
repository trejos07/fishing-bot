import json
import os

def load_json(file_path : str, object_hook = None):
    if not os.path.exists(file_path):
        print(f'can\'t find file at path: {file_path}')
        return

    with open(file_path, 'r') as f:
        if object_hook is None:
            return json.load(f)
        else:
            return object_hook(json.load(f))

def save_json(path : str, data, encoder = None):

    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        print(f'can\'t find directory: {directory}')
        return

    with open(path, 'w', encoding='utf-8') as f:
        if encoder is None:
            json.dump(data, f, ensure_ascii = False, indent = 4)
        else:
            json.dump(data, f, ensure_ascii = False, indent = 4, default = encoder)
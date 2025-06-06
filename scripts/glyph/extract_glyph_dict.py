from .glyph_generator import _load_dict
import json

if __name__ == "__main__":
    d = _load_dict()
    print(json.dumps(d, indent=2, ensure_ascii=False))

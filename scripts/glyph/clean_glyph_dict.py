from .glyph_generator import _load_dict, _save_dict

if __name__ == "__main__":
    data = _load_dict()
    reverse = {}
    duplicates = []
    for term, glyph in data.items():
        if glyph in reverse:
            duplicates.append(term)
        else:
            reverse[glyph] = term
    for term in duplicates:
        del data[term]
    if duplicates:
        print("Removed duplicates:", duplicates)
        _save_dict(data)
    else:
        print("No duplicates found")

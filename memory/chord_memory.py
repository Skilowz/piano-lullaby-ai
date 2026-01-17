from collections import Counter

def build_chord_memory(perception):
    key = perception.get("key", "C")
    mode = perception.get("mode", "major")

    if mode == "minor":
        chords = [f"{key}m", "F", "G", f"{key}m"]
    else:
        chords = [key, "F", "G", key]

    return {
        "key": key,
        "mode": mode,
        "chords": chords
    }

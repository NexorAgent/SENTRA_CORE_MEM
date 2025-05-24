# SENTRA.MEM – Gardien mémoire compressée

def compress_entry(entry):
    return f"⟁{entry['date']}::{entry['type']}>{entry['contenu'][:20]}...#"

def inject_memory(memory_log):
    return "\n".join([compress_entry(e) for e in memory_log])

from difflib import SequenceMatcher

def highlight_changes(original, rewritten):
    """Highlight specific biased words instead of full sentences."""
    try:
        original_words = original.split()
        rewritten_words = rewritten.split()

        matcher = SequenceMatcher(None, original_words, rewritten_words)
        explained_changes = []

        for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
            if opcode == "replace":  # Word was changed
                original_text = " ".join(original_words[i1:i2])
                rewritten_text = " ".join(rewritten_words[j1:j2])
                explained_changes.append(f"🔴 <del>{original_text}</del> ➝ 🟢 <ins>{rewritten_text}</ins>")
            elif opcode == "delete":  # Word was removed
                removed_text = " ".join(original_words[i1:i2])
                explained_changes.append(f"❌ Removed: <del>{removed_text}</del>")
            elif opcode == "insert":  # Word was added
                added_text = " ".join(rewritten_words[j1:j2])
                explained_changes.append(f"✅ Added: <ins>{added_text}</ins>")

        return explained_changes if explained_changes else ["No significant changes."]
    except Exception as e:
        print(f"❌ Error in Highlighting Changes: {str(e)}")
        return ["Error detecting changes."]

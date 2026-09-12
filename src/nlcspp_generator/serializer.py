from __future__ import annotations


def escape_attribute(value: str) -> str:
    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&amp;amp;quot;",
        "\t": "&#x9;",
        "\n": "&#xA;",
        "\r": "&#xD;",
    }
    return "".join(replacements.get(character, character) for character in value)


def encode_document(lines: list[str]) -> bytes:
    return "\r\n".join(lines).encode("utf-8-sig")
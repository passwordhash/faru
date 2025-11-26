from typing import Optional, Tuple


def check_brackets(s: str) -> Optional[int]:
    """
    Check wether brackets in the string are balanced.

    Returns index of the first unmatched bracket or None if all brackets are matched.
    """
    opens = "([{"
    closes = ")]}"
    match = {")": "(", "]": "[", "}": "{"}

    stack: list[Tuple[str, int]] = []

    for i, ch in enumerate(s):
        if ch in opens:
            stack.append((ch, i))
        elif ch in closes:
            if len(stack) == 0:
                return i
            top_ch, _ = stack.pop()
            if match[ch] != top_ch:
                return i

    if stack:
        _, pos = stack[0]
        return pos

    return None


def main() -> None:
    s = input().strip()

    res = check_brackets(s)
    if res is None:
        print("OK")
    else:
        print(res + 1)
        exit(1)


if __name__ == "__main__":
    main()

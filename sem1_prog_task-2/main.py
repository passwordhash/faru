from typing import List, NamedTuple, Literal, cast

UNITS = {
    "ноль": 0,
    "один": 1,
    "два": 2,
    "три": 3,
    "четыре": 4,
    "пять": 5,
    "шесть": 6,
    "семь": 7,
    "восемь": 8,
    "девять": 9,
}

TEENS = {
    "десять": 10,
    "одиннадцать": 11,
    "двенадцать": 12,
    "тринадцать": 13,
    "четырнадцать": 14,
    "пятнадцать": 15,
    "шестнадцать": 16,
    "семнадцать": 17,
    "восемнадцать": 18,
    "девятнадцать": 19,
}

TENS = {
    "двадцать": 20,
    "тридцать": 30,
    "сорок": 40,
    "пятьдесят": 50,
    "шестьдесят": 60,
    "семьдесят": 70,
    "восемьдесят": 80,
    "девяносто": 90,
}

HUNDREDS = {
    100: "сто",
    200: "двести",
    300: "триста",
    400: "четыреста",
    500: "пятьсот",
    600: "шестьсот",
    700: "семьсот",
    800: "восемьсот",
    900: "девятьсот",
}

THOUSANDS = {
    1: "одна тысяча",
    2: "две тысячи",
    3: "три тысячи",
    4: "четыре тысячи",
}

OPERATIONS = {
    "плюс": "+",
    "минус": "-",
    "умножить": "*",
}

UNITS_R = {v: k for k, v in UNITS.items()}
TEENS_R = {v: k for k, v in TEENS.items()}
TENS_R = {v: k for k, v in TENS.items()}


def words_to_int_0_99(tokens: List[str]) -> int:
    """Translates a list of words into a number 0..99"""
    if not tokens:
        raise ValueError("Expected a number in words (0..99)")

    if len(tokens) == 1:
        # one word
        t = tokens[0]
        if t in UNITS:
            return UNITS[t]
        if t in TEENS:
            return TEENS[t]
        if t in TENS:
            return TENS[t]
        raise ValueError(f"Unknown number: {t}")

    if len(tokens) == 2:
        # two words: tens + units
        t1, t2 = tokens
        if t1 in TENS and t2 in UNITS and UNITS[t2] != 0:
            return TENS[t1] + UNITS[t2]

        raise ValueError(f"Invalid number: {' '.join(tokens)}")

    raise ValueError(f"Too long number: {' '.join(tokens)}")


def int_0_99_to_words(n: int) -> str:
    """Converts an integer 0..99 to Russian words"""
    if n < 10:
        return UNITS_R[n]
    if 10 <= n <= 19:
        return TEENS_R[n]
    if n % 10 == 0:
        return TENS_R[n]

    tens = n // 10 * 10
    units = n % 10
    return f"{int_0_99_to_words(tens)} {int_0_99_to_words(units)}"


def int_0_999_to_words(n: int) -> str:
    """Converts an integer 0..999 to Russian words"""
    assert 0 <= n <= 999
    if n < 100:
        return int_0_99_to_words(n)

    parts: List[str] = []
    hundreds = n // 100 * 100
    remainder = n % 100
    parts.append(HUNDREDS[hundreds])
    if remainder:
        parts.append(int_0_99_to_words(remainder))

    return " ".join(parts)


def int_to_words_ru(n: int) -> str:
    """Converts an integer to Russian words"""
    if n == 0:
        return "ноль"
    if n < 0:
        raise NotImplementedError("Negative numbers are not supported")
        # return f"минус {int_to_words_ru(-n)}"

    if n < 100:
        return int_0_99_to_words(n)
    if n < 1000:
        return int_0_999_to_words(n)
    if n < 10000:
        thousands = n // 1000
        remainder = n % 1000

        if thousands in THOUSANDS:
            th_part = THOUSANDS[thousands]
        else:
            th_part = f"{int_0_99_to_words(thousands)} тысяч"

        if remainder:
            return f"{th_part} {int_0_999_to_words(remainder)}"
        return th_part

    raise NotImplementedError("Numbers >= 10000 are not supported")


class ParsedExpr(NamedTuple):
    left: int
    op: Literal["+", "-", "*"]
    right: int


def parse_expression(expr: str) -> ParsedExpr:
    """
    Parses expression of the form '<number> <operation> <number>'"
    Returns a tuple (a, op, b) where a and b are integers and op is the operation symbol.
    """
    tokens = expr.strip().lower().split()
    if not tokens:
        raise ValueError("Empty expression")

    op_idx = -1
    op_symbol = None
    for i, t in enumerate(tokens):
        if t in OPERATIONS:
            op_idx = i
            op_symbol = OPERATIONS[t]
            break
    if op_idx == -1 or op_symbol is None:
        raise ValueError("Operation not found in expression")

    left_tokens = tokens[:op_idx]
    right_tokens = tokens[op_idx + 1 :]
    if not left_tokens or not right_tokens:
        raise ValueError("Invalid format: expected '<number> <operation> <number>'")

    a = words_to_int_0_99(left_tokens)
    b = words_to_int_0_99(right_tokens)
    op_lit = cast(Literal["+", "-", "*"], op_symbol)
    return ParsedExpr(a, op_lit, b)


def calc(expr: str) -> str:
    parsed = parse_expression(expr)
    a = parsed.left
    op = parsed.op
    b = parsed.right
    if op == "+":
        res = a + b
    elif op == "-":
        res = a - b
    elif op == "*":
        res = a * b
    else:
        raise ValueError("Неизвестная операция")

    return int_to_words_ru(res)


def main():
    inp = input().strip().lower()
    print(calc(inp))


if __name__ == "__main__":
    main()

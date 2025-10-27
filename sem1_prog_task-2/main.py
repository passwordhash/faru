from typing import List, NamedTuple, Literal, cast
from decimal import Decimal, ROUND_HALF_UP

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
    "разделить": "/",
    "остаток": "%",
}

UNITS_R = {v: k for k, v in UNITS.items()}
TEENS_R = {v: k for k, v in TEENS.items()}
TENS_R = {v: k for k, v in TENS.items()}
HUNDREDS_R = {v: k for k, v in HUNDREDS.items()}

FEM_UNIT_ALIASES = {
    "одна": "один",
    "две": "два",
}

DENOM_FORMS: dict[int, tuple[str, str]] = {
    10: ("десятая", "десятых"),
    100: ("сотая", "сотых"),
    1000: ("тысячная", "тысячных"),
}

OP_PATTERNS: list[tuple[list[str], str]] = [
    (["остаток", "от", "деления", "на"], "%"),
    (["разделить", "на"], "/"),
    (["умножить", "на"], "*"),
    (["остаток", "от", "деления"], "%"),
    (["разделить"], "/"),
    (["умножить"], "*"),
    (["плюс"], "+"),
    (["минус"], "-"),
    (["остаток"], "%"),
]

AND_TOKEN = "и"


def words_to_int_0_99(tokens: List[str]) -> int:
    """Parse number words (1-2 tokens) into an integer 0..99."""
    if not tokens:
        raise ValueError("Expected a number in words (0..99)")

    if len(tokens) == 1:
        # one word
        t = FEM_UNIT_ALIASES.get(tokens[0], tokens[0])
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
        t2 = FEM_UNIT_ALIASES.get(t2, t2)
        if t1 in TENS and t2 in UNITS and UNITS[t2] != 0:
            return TENS[t1] + UNITS[t2]

        raise ValueError(f"Invalid number: {' '.join(tokens)}")

    raise ValueError(f"Too long number: {' '.join(tokens)}")


def words_to_int_0_999(tokens: List[str]) -> int:
    """Parse number words into an integer 0..999."""
    if not tokens:
        raise ValueError("Expected number in words (0..999)")

    total = 0
    used_teens = False
    for raw in tokens:
        t = FEM_UNIT_ALIASES.get(raw, raw)
        if t in HUNDREDS_R:
            total += HUNDREDS_R[t]
        elif t in TEENS:
            if used_teens:
                raise ValueError("Invalid number: duplicate teens segment")
            total += TEENS[t]
            used_teens = True
        elif t in TENS:
            total += TENS[t]
        elif t in UNITS:
            total += UNITS[t]
        else:
            raise ValueError(f"Unknown number token: {t}")
    if total < 0 or total > 999:
        raise ValueError("Out of supported range 0..999")
    return total


def _denominator_from_word(w: str) -> int | None:
    if w.startswith("десят"):
        return 10
    if w.startswith("сот"):
        return 100
    if w.startswith("тысяч"):
        return 1000
    return None


def parse_number(tokens: List[str]) -> Decimal:
    if not tokens:
        raise ValueError("Expected number tokens")

    if AND_TOKEN in tokens:
        i_idx = tokens.index(AND_TOKEN)
        int_part_tokens = tokens[:i_idx]
        frac_tokens = tokens[i_idx + 1 :]
        if not int_part_tokens or len(frac_tokens) < 2:
            raise ValueError("Invalid decimal format")

        integer = words_to_int_0_99(int_part_tokens)
        frac_num_tokens = frac_tokens[:-1]
        denom_word = frac_tokens[-1]
        denom = _denominator_from_word(denom_word)
        if denom is None:
            raise ValueError("Unknown denominator word")
        if denom == 1000:
            frac_num = words_to_int_0_999(frac_num_tokens)
        else:
            frac_num = words_to_int_0_99(frac_num_tokens)
        if not (0 <= frac_num < denom):
            raise ValueError("Fractional part out of bounds")
        return Decimal(integer) + (Decimal(frac_num) / Decimal(denom))
    else:
        integer = words_to_int_0_99(tokens)
        return Decimal(integer)


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
    """Convert a non-negative integer to Russian words."""
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


def _denom_word(denom: int, numerator: int) -> str:
    """Return correct denominator word for 10/100/1000 depending on numerator."""
    forms = DENOM_FORMS.get(denom)
    if not forms:
        raise ValueError("Unsupported denominator")
    sing, plural = forms
    last_two = numerator % 100
    singular = (last_two % 10 == 1) and (last_two != 11)
    return sing if singular else plural


def number_to_words_ru(x: Decimal) -> str:
    """Convert Decimal to Russian words; round half up to thousandths."""
    if x < 0:
        raise NotImplementedError("Negative numbers are not supported")
    q = x.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
    int_part = int(q)
    frac = q - Decimal(int_part)
    if frac == 0:
        return int_to_words_ru(int_part)

    num = int((frac * 1000).to_integral_value(rounding=ROUND_HALF_UP))
    denom = 1000
    while denom > 10 and num % 10 == 0:
        num //= 10
        denom //= 10
    if denom == 1000:
        num_words = int_0_999_to_words(num)
    else:
        num_words = int_0_99_to_words(num)
    # Feminine agreement for 1/2 with feminine denominators
    if num % 100 != 11 and num % 10 in (1, 2):
        parts = num_words.split()
        if parts:
            if parts[-1] == "один":
                parts[-1] = "одна"
            elif parts[-1] == "два":
                parts[-1] = "две"
            num_words = " ".join(parts)

    return f"{int_to_words_ru(int_part)} и {num_words} {_denom_word(denom, num)}"


class ParsedExpr(NamedTuple):
    left: Decimal
    op: Literal["+", "-", "*", "/", "%"]
    right: Decimal


def parse_expression(expr: str) -> ParsedExpr:
    """Parse '<number> <op> <number>', supporting multi-word ops and decimals."""
    tokens = expr.strip().lower().split()
    if not tokens:
        raise ValueError("Empty expression")

    op_symbol = None
    left_tokens = None
    right_tokens = None
    for i in range(len(tokens)):
        for pat, sym in OP_PATTERNS:
            L = len(pat)
            if i + L <= len(tokens) and tokens[i : i + L] == pat:
                op_symbol = sym
                left_tokens = tokens[:i]
                right_tokens = tokens[i + L :]
                break
        if op_symbol is not None:
            break

    if op_symbol is None or left_tokens is None or right_tokens is None:
        raise ValueError("Operation not found in expression")

    if not left_tokens or not right_tokens:
        raise ValueError("Invalid format: expected '<number> <operation> <number>'")

    a = parse_number(left_tokens)
    b = parse_number(right_tokens)
    op_lit = cast(Literal["+", "-", "*", "/", "%"], op_symbol)
    return ParsedExpr(a, op_lit, b)


def calc(expr: str) -> str:
    """Evaluate expression and return result in words; round to thousandths."""
    parsed = parse_expression(expr)
    a = parsed.left
    b = parsed.right
    op = parsed.op
    if op == "+":
        res = a + b
    elif op == "-":
        res = a - b
    elif op == "*":
        res = a * b
    elif op == "/":
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        res = a / b
    elif op == "%":
        if b == 0:
            raise ZeroDivisionError("Division by zero")
        res = a % b
    else:
        raise ValueError("Unknown operation")

    return number_to_words_ru(res)


def main():
    inp = input().strip().lower()
    print(calc(inp))


if __name__ == "__main__":
    main()

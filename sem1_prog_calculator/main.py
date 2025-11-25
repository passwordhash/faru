from typing import List, NamedTuple, Literal, cast
from fractions import Fraction

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
    10000: ("десятитысячная", "десятитысячных"),
    100000: ("стотысячная", "стотысячных"),
    1000000: ("миллионная", "миллионных"),
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

THOUSAND_FORMS = {
    "one": "тысяча",
    "few": "тысячи",
    "many": "тысяч",
}


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


def words_to_int_0_999999(tokens: List[str]) -> int:
    """Parse number words into an integer 0..999999 (supports 'тысяча/тысячи/тысяч')."""
    if not tokens:
        raise ValueError("Expected number in words (0..999999)")
    thou_idx = -1
    for i, t in enumerate(tokens):
        if t in ("тысяча", "тысячи", "тысяч"):
            thou_idx = i
            break
    if thou_idx == -1:
        return words_to_int_0_999(tokens)
    # thousands segment
    left = tokens[:thou_idx]
    right = tokens[thou_idx + 1 :]
    thousands = 1 if not left else words_to_int_0_999(left)
    remainder = 0 if not right else words_to_int_0_999(right)
    total = thousands * 1000 + remainder
    if total < 0 or total > 999_999:
        raise ValueError("Out of supported range 0..999999")
    return total


def _denominator_from_word(w: str) -> int | None:
    """Map denominator word to a power of ten up to 1_000_000."""
    if w.startswith("миллион"):
        return 1_000_000
    if w.startswith("стотысяч"):
        return 100_000
    if w.startswith("десятитысяч"):
        return 10_000
    if w.startswith("тысяч"):
        return 1_000
    if w.startswith("сот"):
        return 100
    if w.startswith("десят"):
        return 10
    return None


def parse_number(tokens: List[str]) -> Fraction:
    """Parse integer or decimal number into an exact Fraction."""
    if not tokens:
        raise ValueError("Expected number tokens")

    if "и" in tokens:
        i_idx = tokens.index("и")
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
        if denom >= 1000:
            frac_num = words_to_int_0_999999(frac_num_tokens)
        else:
            frac_num = words_to_int_0_99(frac_num_tokens)
        if not (0 <= frac_num < denom):
            raise ValueError("Fractional part out of bounds")
        return Fraction(integer) + Fraction(frac_num, denom)
    else:
        integer = words_to_int_0_99(tokens)
        return Fraction(integer)


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


def _thousands_form(count: int) -> str:
    """Pick correct 'тысяча/тысячи/тысяч' based on count."""
    last_two = count % 100
    last = count % 10
    if 11 <= last_two <= 14:
        key = "many"
    elif last == 1:
        key = "one"
    elif last in (2, 3, 4):
        key = "few"
    else:
        key = "many"
    return THOUSAND_FORMS[key]


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
    if n < 1_000_000:
        thousands = n // 1000
        remainder = n % 1000
        # thousands words in feminine for 1/2
        th_words = int_0_999_to_words(thousands)
        parts = th_words.split()
        if parts:
            if parts[-1] == "один":
                parts[-1] = "одна"
            elif parts[-1] == "два":
                parts[-1] = "две"
            th_words = " ".join(parts)
        th_part = f"{th_words} {_thousands_form(thousands)}"
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


def _digits_to_words(d: str) -> str:
    """Spell each digit separately in words (e.g., '02' -> 'ноль два')."""
    return " ".join(UNITS_R[int(ch)] for ch in d)


def _count_factor(n: int, p: int) -> int:
    c = 0
    while n % p == 0 and n > 0:
        n //= p
        c += 1
    return c


def _feminize_last_word(words: str) -> str:
    """Replace trailing 'один'/'два' with 'одна'/'две' in a number phrase."""
    parts = words.split()
    if not parts:
        return words
    if parts[-1] == "один":
        parts[-1] = "одна"
    elif parts[-1] == "два":
        parts[-1] = "две"
    return " ".join(parts)


def rational_to_words(x: Fraction) -> str:
    """Convert Fraction to words with a finite fractional part and a repeating period (up to 4 digits)."""
    if x < 0:
        raise NotImplementedError("Negative numbers are not supported")
    int_part = x.numerator // x.denominator
    rem = x.numerator % x.denominator
    if rem == 0:
        return int_to_words_ru(int_part)

    q = x.denominator
    # finite part length
    c2 = _count_factor(q, 2)
    c5 = _count_factor(q, 5)
    k = max(c2, c5)
    pow10 = 10**k if k > 0 else 1
    d = (rem * pow10) // q
    r = (rem * pow10) % q

    parts_out: List[str] = [int_to_words_ru(int_part)]
    if k > 0 and d > 0:
        denom_word = _denom_word(pow10, d)
        d_words = int_to_words_ru(d)
        # feminine agreement with denominator
        d_words = _feminize_last_word(d_words)
        parts_out.append(f"и {d_words} {denom_word}")
    # repeating part
    if r != 0:
        digits: List[str] = []
        seen: dict[int, int] = {}
        pos = 0
        while r and pos < 200:
            if r in seen:
                start = seen[r]
                period_digits = "".join(digits[start:])
                break
            seen[r] = pos
            r *= 10
            digit = r // q
            r = r % q
            digits.append(str(digit))
            pos += 1
        else:
            period_digits = "".join(digits)  # fallback
        # limit to 4 symbols displayed
        if len(period_digits) > 4:
            period_digits = period_digits[:4]
        parts_out.append(f"и {_digits_to_words(period_digits)} в периоде")

    return " ".join(parts_out)


class ParsedExpr(NamedTuple):
    left: Fraction
    op: Literal["+", "-", "*", "/", "%"]
    right: Fraction


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
    """Evaluate expression and return result in words with repeating part if any."""
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
            raise ZeroDivisionError("Modulo by zero")
        res = a % b
    else:
        raise ValueError("Unknown operation")

    return rational_to_words(res)


def main():
    inp = input().strip().lower()
    print(calc(inp))


if __name__ == "__main__":
    main()

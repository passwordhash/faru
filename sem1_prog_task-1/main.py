from random import randint


SHUFFLE_TIMES = 1000


def input_list_len() -> int:
    input_msg = "Enter a positive integer: "
    inputed = input(input_msg)
    while True:
        if not inputed.isdigit() or int(inputed) <= 0:
            inputed = input(f"Invalid input. {input_msg}")
            continue
        break

    return int(inputed)


def generate_list(n: int) -> list:
    return [i for i in range(1, n + 1)]


def shuffle(arr: list) -> None:
    """
    Knuth shuffle algorithm implementation.
    Time complexity: O(n)

    param arr: list to be shuffled (will be modified))
    """
    n = len(arr)
    for i in range(n - 1, 0, -1):
        j = randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]


def main():
    n = input_list_len()

    arr = generate_list(n)

    values_freq = {i: [0] * n for i in range(1, n + 1)}
    for _ in range(SHUFFLE_TIMES):
        shuffle(arr)
        for i, v in enumerate(arr):
            values_freq[v][i] += 1

    print("Shuffled list:", arr)

    for value in range(1, n + 1):
        print(f"Value {value} frequency: {values_freq[value]}")


if __name__ == "__main__":
    main()

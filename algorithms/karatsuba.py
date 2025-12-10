# algorithms/karatsuba.py

def parse_integers_file_content(file_content: str):
    """Parse content with exactly two integers, one per line."""
    lines = file_content.strip().splitlines()
    if len(lines) != 2:
        raise ValueError("Content must contain exactly 2 numbers, one per line")
    x = int(lines[0].strip())
    y = int(lines[1].strip())
    return x, y


def karatsuba(x: int, y: int) -> int:
    """Recursive Karatsuba multiplication."""
    if x < 10 or y < 10:
        return x * y
    n = max(len(str(x)), len(str(y)))
    m = n // 2
    high1, low1 = divmod(x, 10**m)
    high2, low2 = divmod(y, 10**m)
    z0 = karatsuba(low1, low2)
    z1 = karatsuba(low1 + high1, low2 + high2)
    z2 = karatsuba(high1, high2)
    return (z2 * 10**(2*m)) + ((z1 - z2 - z0) * 10**m) + z0


def karatsuba_steps(x: int, y: int):
    """
    Generator to yield each step of Karatsuba multiplication
    for visualization.
    """
    if x < 10 or y < 10:
        yield {"type": "base", "x": x, "y": y, "product": x * y}
        return x * y

    n = max(len(str(x)), len(str(y)))
    m = n // 2
    high1, low1 = divmod(x, 10**m)
    high2, low2 = divmod(y, 10**m)

    # Split step
    yield {"type": "split", "x": x, "y": y,
           "high_x": high1, "low_x": low1,
           "high_y": high2, "low_y": low2}

    # Recursive steps
    z0 = yield from karatsuba_steps(low1, low2)
    z2 = yield from karatsuba_steps(high1, high2)
    z1 = yield from karatsuba_steps(low1 + high1, low2 + high2)

    # Combine step
    product = (z2 * 10**(2*m)) + ((z1 - z2 - z0) * 10**m) + z0
    yield {"type": "combine", "x": x, "y": y,
           "z2": z2, "z1": z1, "z0": z0,
           "product": product}

    return product

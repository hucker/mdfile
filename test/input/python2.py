def fib(n:int):
    """
    Calculate the nth Fibonacci number using a recursive method.

    This function computes the Fibonacci number at the nth position in the
    sequence, where the sequence starts with 0 and 1. The computation is
    performed recursively by summing the two preceding numbers in the sequence.

    Args:
        n: The position in the Fibonacci sequence to compute; must be a
           non-negative integer.

    Returns:
        The nth Fibonacci number.
    """

    if n < 2:
        return n
    else:
        return fib(n-1) + fib(n-2)
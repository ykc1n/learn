# Appendix B: Standard Library · Study Guide

This original checklist accompanies the standard-library appendix. The complete book’s function descriptions are available through your imported PDF.

## I/O and strings
For every I/O call, record its header, input contract, result, and failure signal. For string operations, record whether the operation appends a terminator, how it interprets its size argument, and whether overlap is permitted. `memmove` permits overlapping regions; `memcpy` does not.

## Character classification and numbers
Character classification has a restricted argument domain. Numerical conversion functions differ in their error reporting; `strtol` lets you inspect where parsing stopped and detect range problems, while `atoi` cannot express the same diagnostics. Mathematical functions have domains and ranges that deserve deliberate tests.

## Memory and general utilities
Match every successful owned allocation with one release. `calloc` initializes allocated bytes to zero; do not generalize this into a portable claim about all pointer or floating representations. On `realloc` failure the original allocation remains valid, so keep the original pointer until success is known. A `qsort` comparison should implement a consistent ordering and avoid overflow from naive subtraction.

## Diagnostics and environment
`assert` is a debugging check that may be removed when `NDEBUG` is defined; do not rely on it for required side effects. `errno` is meaningful when the relevant operation’s contract says to inspect it. Signal handlers have constraints on what they may do. Time and locale functions depend on their documented environment.

## Practice lab
Make a reference card for five functions used in your programs. Include the header, parameter preconditions, return value, error behavior, and ownership effects. Write a conversion helper using `strtol` that rejects trailing junk and out-of-range results before narrowing to a smaller type.

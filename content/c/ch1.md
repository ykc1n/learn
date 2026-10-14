# Chapter 1: A Tutorial Introduction

## First programs and formatted output
A C program begins execution in `main`. Standard I/O declarations come from `<stdio.h>`. In a hosted implementation, returning zero from `main` reports success. A string literal contains characters plus a terminating zero byte. Escape sequences such as `\n` represent characters that are awkward to type directly.

```c
#include <stdio.h>
int main(void)
{
    printf("Learning locally.\n");
    return 0;
}
```

Compile source into an executable, then run the executable; editing source does not change an already compiled binary. Distinguish compile errors, link errors, and wrong output.

## Variables, arithmetic, and loops
A declaration gives an object a type and a name. Integer division discards a fractional part; choose floating operands when a fractional result is required. A `while` loop checks its condition before its body. A `for` loop groups initialization, condition, and update. Keep invariants visible: what is true before and after each iteration? A symbolic constant can give a repeated value meaning, but a macro does textual substitution and has no independent storage.

## Character input and output
`getchar()` returns an `int`: either a character value or the distinct sentinel `EOF`. Store the result in `int`, not `char`, so the sentinel can be represented. A stream reaches end-of-file only after an input operation detects it. `putchar()` writes a character; character constants such as `'x'` differ from string literals such as `"x"`.

## Counting and state
Counting characters, lines, and words requires different rules. A word-counting state machine can remember whether it is currently inside a word. Decide which characters count as separators and update the counter at transitions, not for every letter. Include zero-length input, repeated spaces, and a final line with no newline in your tests.

## Arrays, functions, and arguments
An array stores a fixed number of same-type elements, indexed from zero. Track both capacity and the current useful length. A function declaration tells callers the return type and parameter types. C passes arguments by value: changing a scalar parameter changes only the function’s local copy. Passing an array usually passes a pointer to its first element; a function can then mutate the caller’s elements. This does not mean that C has pass-by-reference parameters.

## Strings and storage
A C string is a sequence ending in `\0`; reserve room for that terminator. A function reading a line must bound its writes and communicate the amount read. File-scope variables can outlive individual calls but expose shared state. Prefer an explicit interface that receives needed data over an unnecessary global.

## Practice lab
Write a program that counts digits and separators in standard input. Use a ten-element array, check each character before computing an index, and print the counts after end-of-file. Explain why the input variable is `int`. Test empty input, all digits, and text without a trailing newline.

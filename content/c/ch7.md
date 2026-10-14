# Chapter 7: Input and Output

## Streams and formatted I/O
The standard library abstracts input and output as streams. `stdin`, `stdout`, and `stderr` have conventional roles. `printf` conversions must match argument types; a mismatch can cause undefined behavior. Its return value can report output failure. Formatting controls presentation rather than changing the underlying object’s type.

## Variable arguments
A variadic function cannot infer each argument’s type from the raw call data. A format string or another contract tells it what to expect. Default argument promotions apply to arguments passed through `...`: small integer types are promoted and `float` becomes `double`. In user-defined variadic functions, use `<stdarg.h>` and pair initialization with cleanup.

## Formatted input
`scanf` usually needs pointers to writable destinations. Check its conversion count. Input formats have whitespace and matching rules that differ from output formats. Bound string conversions to the destination capacity; reserve room for the zero terminator. For robust interactive input, read a bounded line and parse it deliberately rather than leaving an invalid character stuck in the stream.

## File operations and errors
`fopen` returns a stream pointer or a null pointer on failure. Open modes distinguish reading, writing/truncation, and appending. Close a stream when finished and check important error reports. End-of-file and I/O error are not the same condition; use `feof` and `ferror` after an operation fails. `perror` helps describe a library or system error using the current error indication.

## Line and character operations
`fgets` limits the number of bytes stored, adds a terminator when successful, and may retain a newline. A line longer than the buffer may arrive in several pieces. Character input returns an `int` so it can also represent `EOF`. Avoid unsafe unbounded line-input routines; do not treat a buffer as an unlimited destination.

## Useful library tools
`<string.h>` operates on byte strings and memory; overlapping copies require the appropriate operation. `<ctype.h>` functions require `EOF` or a value representable as `unsigned char`; cast a possibly negative plain `char` before classifying it. `<math.h>` offers numerical functions. `<stdlib.h>` covers conversions, allocation, sorting, and program termination. The library is part of the language environment, so know its preconditions and failure signals.

## Practice lab
Read a text file line by line, number the lines, and write them to a second file. Check both opens, each important write, and the final input error flag. Test a line longer than your buffer and distinguish a fragment from a complete line. Never use user input as a `printf` format string.

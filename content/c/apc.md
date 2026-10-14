# Appendix C: Summary of Changes · Study Guide

## From early C to ANSI C
The second edition reflects the ANSI standardization effort. Function prototypes improve checking of calls. Library declarations and headers provide consistent interfaces. Qualifiers such as `const` express access constraints. These changes affect what a compiler can diagnose and how programmers communicate a contract.

## Compatibility is a question to investigate
Old source can rely on obsolete declaration styles, implicit assumptions, or a particular implementation. Do not assume that successful compilation proves portability or correctness. Select a language standard explicitly, read warnings, and distinguish extensions from portable features.

## Beyond the second edition
C99, C11, C17, and C23 are later revisions. This course follows the second edition’s topic sequence while flagging historical interfaces and unsafe practices. Newer features can be studied separately after the core rules are understood; avoid mixing dialects accidentally in one explanation.

## Index and final review
Use the index in your PDF to locate unfamiliar terms rather than reading linearly every time. Before the final exam, revisit notes about undefined behavior, object lifetime, conversion, ownership, and error handling. These rules connect many otherwise separate chapters.

## Practice lab
Take a small C90 program and list which changes you would make when adopting a newer standard. Separate language changes from library changes and platform-specific APIs. Explain which tests remain valuable across all versions.

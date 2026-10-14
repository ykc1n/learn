# Appendix A: Reference Manual · Study Guide

This original guide helps you navigate the book’s reference appendix. Consult your PDF for the complete reference prose and grammar.

## Lexical conventions and syntax
Separate tokens, comments, identifiers, keywords, constants, and string literals. Recognize translation phases and how the preprocessor affects tokens. A grammar explains which constructs are legal; precedence tables are a convenience for understanding expression grouping.

## Meaning of objects and types
Distinguish an object from a function, an lvalue from a value, and a pointer type from its pointed-to type. Qualifications affect the operations permitted through an access path. Type compatibility and declaration rules govern whether interfaces across translation units agree.

## Conversions and expressions
Classify implicit conversions before predicting an arithmetic result. Distinguish integer promotions, usual arithmetic conversions, assignment conversion, and casts. For an expression, establish grouping, then analyze required sequencing; do not infer argument order from precedence.

## Declarations and storage
Read declarators from the name outward. Separate linkage, scope, and storage duration. Check array bounds, pointer validity, and object lifetime before using a value. A valid declaration does not imply that every expression involving that object is valid at run time.

## Statements, external definitions, and preprocessing
Connect a function’s declaration with its definition. Trace control transfers through blocks, loops, switches, and labels. A translation unit is preprocessed and translated separately; external declarations must still describe compatible entities across the program.

## A reference lookup habit
When a test behaves unexpectedly, reduce it to a small example, identify the applicable rule, and classify the behavior: defined, implementation-defined, unspecified, or undefined. Record the classification in your notes. Modern standard revisions may differ from the second edition’s ANSI C description.

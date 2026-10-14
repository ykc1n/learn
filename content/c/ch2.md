# Chapter 2: Types, Operators, and Expressions

## Names, constants, and declarations
Choose names that describe meaning. Reserved words cannot be identifiers. C provides integer and floating types whose exact sizes depend on the implementation; use `<limits.h>` and `<float.h>` to inspect limits. A character constant has type `int` in ordinary C; a string literal supplies an array of characters. An enumeration names integer constants. `const` prevents modification through a qualified lvalue; it is not a general textual replacement like `#define`.

## Arithmetic, comparisons, and logic
Arithmetic operators calculate values. Relational and equality operators yield `int` results of zero or one. Logical `&&` and `||` short-circuit: the right operand is evaluated only when required. A nonzero value is true in a condition. Remember that `=` assigns while `==` compares. `5 / 2` is integer division; `5 / 2.0` involves floating arithmetic.

## Conversions
The usual arithmetic conversions choose a common type for many binary operations. Signed and unsigned mixtures can surprise you: a negative value converted to an unsigned type becomes a large value modulo the unsigned range. A cast requests a conversion; it does not repair an invalid memory access or make an overflowing computation safe. Keep domain assumptions explicit.

## Increment, bit operations, and assignment
Prefix increment changes an object and produces the updated value. Postfix increment produces its previous value and schedules the update as part of the expression. Do not modify the same scalar multiple times without required sequencing. Bitwise operators manipulate bit patterns; logical operators test truth. Use unsigned operands for predictable shifts and masking. Parenthesize macro arguments and entire macro expansions.

```c
unsigned int flags = 10U;
unsigned int enabled = flags & 2U;
flags |= 1U;
```

`&` is bitwise AND here; `&&` would produce a truth value. A compound assignment updates its left operand while evaluating that operand only once. The conditional operator chooses one of two expressions.

## Precedence and evaluation order
Precedence determines grouping, not the order in which function arguments are evaluated. Associativity resolves equal-precedence grouping. Parentheses help communicate intent but do not introduce every kind of sequencing. Avoid code that depends on unspecified argument evaluation order, or invokes undefined behavior with unsequenced modifications.

## Practice lab
For an unsigned byte represented in an `unsigned int`, write expressions to test a bit, set it, and clear it. Trace each in binary. Then compare a short-circuit guard, `p != NULL && *p == 7`, with a bitwise expression. Explain why only the logical guard protects the dereference.

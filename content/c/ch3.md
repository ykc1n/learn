# Chapter 3: Control Flow

## Statements, blocks, and selection
A semicolon terminates many statements; braces group statements into a block. An `if` chooses a path based on a scalar condition. In a chain of alternatives, test from the most specific or highest-priority case toward the default. An `else` attaches to the nearest unmatched `if`; braces make the intended nesting visible.

## Switch
A `switch` chooses among integral constant labels. Execution continues through later cases unless a transfer such as `break` ends it. Fall-through can be deliberate, but accidental fall-through is a common bug. `default` handles unlisted cases. A `break` terminates the nearest loop or switch, not all enclosing control structures.

## Loops
Use a `while` when the number of iterations is not known ahead of time. A `for` conveniently expresses a counter-controlled loop. A `do ... while` checks its condition after the body, so the body runs at least once. Keep the update on every required path. With `continue`, a `for` proceeds to its update expression, whereas a `while` proceeds to its condition.

```c
int i;
for (i = 0; i < 6; ++i) {
    if (i % 2 == 0)
        continue;
    printf("%d\n", i);
}
```

The loop prints odd indices. Evaluate its bounds carefully: six elements have valid indices zero through five, not one through six.

## Break, continue, and goto
`break` leaves the nearest loop; `continue` advances within it. Neither expresses a function return. `goto` jumps to a label in the same function. It can centralize cleanup in systems code, but unrestricted jumps make invariants harder to reason about. If several resources are acquired, each error path should release exactly the resources that were successfully acquired.

## Reasoning about algorithms
Before a loop, state its invariant. At the end, combine the invariant with the negated loop condition to justify the result. Trace boundary inputs and verify termination. For a search algorithm, distinguish a found position from a not-found sentinel. For sorting, check that each pass makes progress and that bounds prevent overrunning the array.

## Practice lab
Implement a menu parser using `switch`, then a bounded search using `for`. Write tests for the first item, last item, missing item, and empty collection. Introduce an accidental empty statement after an `if` and explain why the program changes behavior.

# Chapter 6: Structures

## Group related data
A `struct` groups named members that may have different types. Access a member with `.` when you have a structure object, and `->` when you have a pointer to one. Each structure has its own members; declaring a type does not allocate a particular instance. Structures may contain arrays, pointers, and other structures.

```c
struct sample {
    const char *label;
    double value;
};
struct sample s = {"temperature", 21.5};
```

## Structure values and pointers
Structure assignment copies member values as a value operation, but a pointer member still points to the same target; this is not a deep clone of dynamically allocated data. Passing a structure by value gives a separate structure value. Passing a pointer can avoid a copy and allow mutation. Document who owns each allocated target and how long it remains alive.

## Arrays of structures and self-reference
An array of structures stores repeated records contiguously. A linked node can contain a pointer to its own structure type because the pointer size is known without recursively embedding an entire node. The type cannot contain a complete instance of itself as a member. A tree makes different ordering and ownership promises than a flat array.

## Search trees and lookup tables
A binary search tree compares keys and follows a left or right branch. Correctness depends on preserving the ordering invariant. An unbalanced tree can degenerate into a chain. A hash table computes a bucket from a key and handles collisions, often with chains. Hash equality does not imply key equality; compare keys within the bucket.

## Typedef
`typedef` gives a type an alias; it does not create a distinct runtime representation. Clear names can communicate intent, but aliases that hide pointer ownership can obscure important behavior. Keep public interfaces readable to a caller who has not seen the implementation.

## Unions and bit-fields
A union provides shared storage for alternative members. Track which representation is valid rather than assuming that writing every member preserves every value. A tagged union pairs a union with an explicit discriminator. Bit-fields pack small integer fields into implementation-dependent layouts; do not use their layout as a portable network or disk format.

## Practice lab
Define a linked-list node holding a short label and a count. Write insertion, lookup, and destruction functions. On allocation failure, preserve the existing list. Trace pointer updates for an empty list and for inserting before the first node. Explain why a shallow copy is insufficient for independent ownership of the entire list.

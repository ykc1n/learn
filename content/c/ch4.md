# Chapter 4: Functions and Program Structure

## Function contracts
A function interface describes its result, parameters, and responsibilities. Declare functions before calling them, and use prototypes with parameter types. An `int f(void)` declaration says no parameters; the older `int f()` declaration does not provide the same parameter information in C90. Return values should communicate success or failure when callers need to recover.

## Scope, linkage, and duration
Scope is where a name can be used. Linkage determines whether declarations identify the same entity across scopes or files. Storage duration controls how long an object exists. These concepts are related but distinct. Automatic local objects ordinarily exist only during a call; a pointer to such an object becomes invalid after it returns.

## External and static objects
Use a header for declarations shared by source files. Define an external object once and declare it with `extern` elsewhere. At file scope, `static` gives an object or function internal linkage. A `static` local object preserves its value between calls while its name remains local to the block. Excess global state increases coupling and makes tests interfere with one another.

## Header organization and register
Header guards prevent repeated inclusion from redefining declarations. Avoid placing ordinary external object definitions in a header included by several source files. `register` is historically an optimization hint; it does not guarantee a hardware register, and the language restricts taking the address of a register-qualified object.

## Recursion
Recursive functions need a base case and an argument that moves toward it. Each call has its own automatic objects. Trace the call stack rather than treating recursion as a jump. A recursive function is not automatically efficient; deep recursion can exhaust available stack storage. Prefer a loop when it communicates the algorithm more simply.

## Preprocessing
The preprocessor handles `#include`, `#define`, and conditional compilation before ordinary translation. Function-like macros substitute tokens, and an argument may be evaluated repeatedly in the resulting code. Parentheses avoid many grouping bugs but cannot prevent repeated side effects. Prefer an ordinary function where type checking and single argument evaluation matter. Conditional compilation lets a build select platform-specific code without sprinkling run-time tests everywhere.

## Practice lab
Split a running-total module into a header, implementation, and caller. Keep its total private with file-scope `static`, expose reset/add/read functions, and compile the implementation separately. Compare a macro that squares its argument with a function; explain the effect of passing an increment expression.

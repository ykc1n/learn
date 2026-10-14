# Chapter 5: Pointers and Arrays

## Addresses and indirection
A pointer value identifies an object or function, or is a null pointer value. `&x` obtains the address of an addressable object; `*p` designates the pointed-to object when the pointer is valid. A pointer type describes the type accessed through it. An uninitialized pointer is not a valid place to store data. Null, dangling, and out-of-bounds pointers are different problems.

## Function parameters
All arguments are passed by value, including pointers. A function receives a copy of an address and can use it to modify the object at that address. To change the caller’s pointer itself, pass a pointer to that pointer. A swap routine needs addresses of the two caller objects, not copies of their scalar values.

## Arrays and arithmetic
In many expressions, an array converts to a pointer to its first element. Exceptions include its use with `sizeof` and unary `&`. The array is not itself a pointer object. Pointer arithmetic advances in units of the pointed-to type. Arithmetic and comparisons must respect array boundaries; you may form a one-past pointer but not dereference it. Subtracting pointers into the same array gives an element distance.

## Strings and pointer arrays
A string needs a zero terminator and writable storage when you intend to modify it. A pointer to a string literal is not a writable character array. Arrays of pointers can represent variable-length strings efficiently; each pointer and each pointed-to string still has its own lifetime. Compare strings by content with a string function, not by comparing their addresses.

## Multidimensional arrays
A two-dimensional array contains contiguous rows. Advancing a pointer to a row moves by an entire row. An `int **` does not describe the same layout as an array of fixed-width rows. When passing a multidimensional array, the compiler needs the row width to compute indexing correctly. In C90, sizes in these declarations follow the older constant-bound rules.

## Command-line arguments and function pointers
`argc` counts command-line arguments, and `argv` points to strings. Check that an argument exists before indexing it. A function pointer can select behavior at run time; its pointed-to signature must match the function you call. Read complicated declarations by starting at the identifier and following parentheses, suffixes, and pointer operators.

## Practice lab
Write a string-length function that advances a pointer without stepping beyond the terminator. Then create an array of pointers to three immutable strings and a function pointer for choosing a comparison routine. Draw the pointer objects separately from the character arrays they address.

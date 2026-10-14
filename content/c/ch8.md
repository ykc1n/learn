# Chapter 8: The UNIX System Interface

## File descriptors
Unix system calls use small integer file descriptors rather than C `FILE *` streams. The conventional descriptors 0, 1, and 2 correspond to standard input, output, and error. A descriptor refers to an open kernel-managed resource; a pathname identifies a directory entry. Multiple descriptors can refer to related open-file state.

## Reading and writing
`read` reports how many bytes were obtained, zero at end-of-file, or a negative error result. `write` can transfer fewer bytes than requested. Correct copying code handles partial writes, advances the buffer by the number transferred, and deals with interrupted operations according to its contract. Requested length is not a guarantee of the result length.

## Open, create, close, and removal
Opening selects access flags and may create a file when specified. Creation modes are affected by the process file-mode mask. Close descriptors along every exit path. Removing a directory entry does not necessarily destroy data immediately while other links or open references remain. Unix interfaces are platform APIs, not ISO C facilities.

## Positioning and library implementation
`lseek` changes a seekable descriptor’s file position; pipes are generally not seekable. Buffering can reduce expensive system calls by collecting small reads and writes. Mixing raw descriptor operations and buffered stream operations on the same underlying resource requires care because the library may hold buffered data and its own notion of position.

## Directories and metadata
A directory organizes names, while metadata describes the referred-to object. Use the modern platform’s directory interfaces and check every reported error. Distinguish a symbolic link from its target when selecting metadata operations. Traversing a directory tree needs explicit handling of permissions, cycles or links, and paths too long for fixed buffers.

## Allocation model
An allocator obtains storage, divides it into blocks, remembers allocation metadata, and coalesces freed regions when appropriate. Alignment, arithmetic overflow, and ownership are correctness requirements. `malloc` returns a suitably aligned allocation or a null pointer; the bytes are initially uninitialized. Call `free` once for each owned allocation and never use the allocation afterward.

## Historical examples and modern practice
The second edition’s Unix examples describe the systems of its era. Treat implementation sketches as educational, not as replacements for your platform’s supported allocator or standard library. Consult current manual pages for signatures and platform differences. Compile user programs with diagnostics and use memory-checking tools when available.

## Practice lab
Design a descriptor-based file copy function with explicit error returns. Explain each case: empty input, partial write, interrupted call, failed open, and failed close. Draw an allocator’s free-list update for splitting a block and coalescing adjacent free blocks without implementing an unsafe production allocator.

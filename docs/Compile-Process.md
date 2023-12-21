This document describes compilation process of MCDIL.

# Parsing

Whole parsing process would be done by [Lark](https://github.com/lark-parser/lark),
which is very powerful Python library to define own grammar and generate a parser.
For exact grammar specifications, please have a look at [mcdil.lark](https://github.com/McDic/MCDIL/blob/master/mcdil/mcdil.lark).

I plan to optimize the current grammar even further to use LR(1) parser, but that's a low priority task.

# Identifier Mapping

After parsing is done, the compiler construct basic components and map identifier dependency graph of each components.
This includes variables, functions, namespace, type name, aliases, etc.
We check if there is any invalid use of identifiers like out of scope, undefined, etc.

All components(including anonymous blocks) will have some of following properties;

- ID (This should be unique regardless of their component type)
- Name (Except anonymous components like `while` blocks or branching blocks)
- Author name and email (Only namespace can contain `author` statement, but child components will inherit these)
- List of child components
- Set of visible identifiers (This data will not be saved in most components except closures but this will still be cared to resolve many stuffs like name resolving)

# Semantic Execution

*WIP*

# Optimization

*WIP*

# Datapack Generation

*WIP*

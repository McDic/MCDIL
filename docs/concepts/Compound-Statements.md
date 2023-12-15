# Compound Statements

This document describes compound statements of MCDIL.

## Branch

Used with keywords `if` and `else` for branching.

```
bool x = false;
bool y = true;
int result = 0;
if(x) {
    result = 1;
} else if(y) {
    result = 2;
} else {
    result = 3;
};
```

## While Loop

Used with keyword `while`. This loop is used for typical programming loops.
You can also use `continue` or `break` like traditional languages.

```
int a = 10;
while(a > 0) {
    a -= 1;
    if(a < 5) {
        break;
    };
    continue;
};
```

## Namespace

Namespace is just a place to encapsulate static variables, functions and structs.
Use keyword `namespace` to define this.
You are allowed to define namespace everywhere, even in other compound statements.

```
namespace some_fun {
    export immutable int x = 1;
};
immutable int y = some_fun::x + 1;
```

## Execute

Used with keyword `execute`. This is used for minecraft-specific loops.
This "loop" works differently from traditional loops like `while`.
You can't `return`, `break`, or `continue` inside the chain.
This is roughly equivalent to an anonymous function with null return type
where this function is executed on potentially different executors.

```
int count = 0;
execute(as @a; positioned 3D(~-1, ~2.5, ~0); rotated 2R(0.0, 0.0)) {
    count += 1;
};
```

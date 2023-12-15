# Built-in Types

This document describes built-in types of MCDIL.

## Primitives

### Integer

Used with keyword `int`. Specifically, only 32-bit integers are supported. In most situations, this value is maintained by `/scoreboard`.

- Scoreboardable: True
- Storagable: True
- Template Parameters: None

```
int i = 1;
i += 2;
```

### Boolean

Used with keyword `bool`. There are 2 literal keywords for this type; `true` and `false`. Like `int`, this value is maintained by `/scoreboard` in most situations. `0` is considered as `false`, and non-zero values are considered as `true`.

- Scoreboardable: True
- Storagable: True
- Template Parameters: None

```
bool b = true;
```

### Null

This type is used to indicate only one value - the null. This is similar to C++'s `void` or Python's `None`.
No operator is supported to this type of operand.
Currently this is only useful when there is no return on function.

- Scoreboardable: False
- Storagable: False
- Template Parameters: None

```
function no_return() -> null {};
```

### Float

*WIP*

## Data Structures

This section enumerates list of data structure types like containers.

### String

*WIP*

### Deque

The generic deque is natively supported. Type name is `deque<T>`.
This container supports `push_back`, `push_front`, `pop_back`, `pop_front`, `empty` and indexing.
It has constructor `init()` and `init(int size, T initial_element)`.
You may already noticed that you cannot store different types of values in language-side.

- Scoreboardable: False
- Storagable: True
- Template Parameters: `<typename T>`

*WIP*

## Minecraft Specific

This section enumerates list of Minecraft-specific types.

### Target Selector

Used with special character `@`.
The syntax is slightly more generous than Minecraft's one.
You can create a variable which stores target selector, with keyword `selector`.
However, `immutable` must be specified with initialization of selector variables for performance reasons.
You should think target selector as something callable;
Holding target selector itself does not fix UUIDs to target.

- Scoreboardable: False
- Storagable: False
- Template Parameters: None

```
immutable selector all_people = @a;
```

### Location

This type is specified for 3D location coordinates in Minecraft, axes are exactly same as in game.
You can initialize with keyword `D3`.

- Scoreboardable: False
- Storagable: False
- Template Parameters: None

```
D3 absolute(2, 3.0, 5);
D3 relative(~2, ~0.1, ~-2);
D3 carpet(^2, ^3, ^-1);
```

### Rotation

This type is specified for 2D rotation coordinates in Minecraft, axes are exactly same as in game.
You can initialize with keyword `R2`.

- Scoreboardable: False
- Storagable: False
- Template Parameters: None

```
R2 some_rotation(0.0, 90.0);
```

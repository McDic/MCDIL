This document describes built-in types of MCDIL.

## Lv.0 Types

Lv.0 types are the most primitive types.
They can be used in generic template parameters,
directly stored in scoreboard objectives and data storages.

### Integer

Used with keyword `int`. Specifically, only 32-bit integers are supported. In most situations, this value is maintained by `/scoreboard`.

- Scoreboardable: True
- Storagable: True
- Template Parameters: None
- Default Initialization: 0

```
int i = 1;
i += 2;
```

### Boolean

Used with keyword `bool`. There are 2 literal keywords for this type; `true` and `false`. Like `int`, this value is maintained by `/scoreboard` in most situations. `0` is considered as `false`, and non-zero values are considered as `true`.

- Scoreboardable: True
- Storagable: True
- Template Parameters: None
- Default Initialization: `false`

```
bool b = true;
```

## Lv.1 Types

Lv.1 types are less primitive than Lv.0 types, but they are still in range of being "primitive".
Some operation regarding this types are not directly translated into just one command, due to some limitations of the Minecraft.
They do not provide any methods, but you cannot put Lv.1 types in template parameters.

### Null

This type is used to indicate only one value - the null. This is similar to C++'s `void` or Python's `None`.
No operator is supported to this type of operand.
Currently this is only useful when there is no return on function.

- Scoreboardable: False
- Storagable: False
- Template Parameters: None
- Default initialization: Null value (Cannot be written in code)

```
function no_return() -> null {};
```

### Float

*WIP*

## Lv.2 Types (General)

Lv.2 types are either data structures or Minecraft specific stuffs.
They all provide some methods and internal properties like typical structs.
However, you cannot make an inheritance from this type.

### String

*WIP*

### Deque

The generic deque is natively supported. Type name is `deque<T>`.

- `T` means an element type of this container.

Following are supported methods;

- `init()`: Constructor 1, creates an empty deque.
- `init(int size, T initial_value)`: Constructor 2, creates a deque with `size` elements filled with `initial_value`.
- `push_back(T value) -> null`: Push `value` at the back.
- `push_front(T value) -> null`: Push `value` at the front.
- `pop_back() -> T`
- `pop_front() -> T`
- `size() -> int`
- `get(int index) -> T`

Since there is no array or pointer in this language, this data structure would be very useful.
However, unlike typical deque, this data structure performs bad on `push_front` or `pop_front` in game, because this is literally implemented as raw list in Minecraft SNBT format.

- Scoreboardable: False
- Storagable: True
- Template Parameters: `<typename T>`

*WIP*

### Map

The generic mapping is natively supported.
Type name is `map<typename K, typename V>`.

- `K` means a key type where `K` should implement `key() -> string`.
- `V` means a value type.

Following are supported methods;

- `init()`
- `set(K key, V value)`
- `get(K key, V default)`
- `remove(K key)`

*WIP*

## Lv.2 Types (Minecraft Specific)

This section enumerates list of Minecraft-specific types.
All Minecraft-specific types are Lv.2 types.

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
- Template Parameters: <...>

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
- Template Parameters: <...>

```
R2 some_rotation(0.0, 90.0);
```

## Type Qualifiers

Currently there is only one type qualifier.
More might come as development progress goes further.

### Immutable

Used with keyword `immutable`.
If you initialize an immutable variable with literals or other constant variables etc,
then this variable becomes constant;
This variable will not consume memory whenever it's possible.
It is possible to specify `immutable` on function parameters and return type.

```
immutable some_int = 1;
```

## Auto Type

If you define variable with keyword `auto`,
then the compiler infer type automatically.
This works on variable definition and function return types.
`auto` can't be a generic;
If you want to specify template parameter,
then you should use a type name explicitly.
However, `auto` is compatible with type qualifiers.

```
immutable auto some_int = 1;
auto some_location = D3(2, 3.0, 5);
auto some_another_int = some_int;
```

## Reference

There is a "reference" semantic in this language,
which acts similar as in many typical programming languages.
There is only one type of reference in MCDIL, in C++'s term, "lvalue reference".
You can put `&` as suffix of a type to indicate that type as reference.
There is no pointer in this language, because Minecraft allows string based memory locations.

```
int x = 0;
int& y = x;
```

# MCDIL: McDic's Language

This language is created for easy development of Minecraft JE datapack.

## Installation

You have to prepare Python 3.11+ to use this library.
After you prepared appropriate environment, run following;

```bash
pip install mcdil
```

## Features

*WIP*

# Principles

### 1. Never trust any value as intermediates other than scoreboard integers and data storages.

The list of trustable values during the function execution are following;

- Scoreboard values.
- Data storages.

Other than the aboves, you should capture everything at the beginning of the function call whatever you need to calculate, and output those at the end of the function. Never refer those during the intermediate calculations.

### 2. Every function execution is atomic.

Minecraft ensures that every function execution is an atomic. There are few exceptions like `/worldborder` though.
Similar manners are applied in this language.
Every trustable local state should be reliable, even after delay calls.

### 3. Take more memory than sacrificing runtime performance whenever possible.

We don't care about the number of functions or duplicated commands here.
If that has much lighter runtime performance, we goes for that.

### 4. A MCDIL function does not guarantee to run code after delay call if the original target entity is killed.

Since `/schedule` does not store the information, I introduce a different way to execute various functions in same tick but under different entities.
However, the calling entity must be alive, otherwise the function will not be executed.

### 5. Not every semantics are predictable during runtime, therefore I always consider the worst case.

Suppose you conditionally call some delay.
Then the compiler always asssume the delay is always happening, even if there are some cases which does not call delay at all.

# Grammar Specifications

This section is incomplete, and always follow the exact grammar specification.
Please read `mcdil.lark` for the exact grammar.
For example programs, please have a look at `examples` folder.

## Built-in Types (Primitive)

Not many primitive types are supported for this moment. I am focusing to make working example first, and then will support floating numbers etc.

### Integer

Used with keyword `int`. Specifically, only 32-bit integers are supported. In most situations, this value is maintained by `/scoreboard`.

```
int i = 1;
i += 2;
```

### Boolean

Used with keyword `bool`. There are 2 literal keywords for this type; `true` and `false`. Like `int`, this value is maintained by `/scoreboard` in most situations. `0` is considered as `false`, non-zero values are considered as `true`.

```
bool b = true;
```

### Null

This type is used to indicate only one value - the null. This is similar to C++'s `void` or Python's `None`.

There is no way to assign anything to this value. Any operator used with null value will fail to compile, except `null == null` and `null != null`.

```
null n;
```

## Built-in Types (Non-Primitive)

### Range

Used with keyword `range`. For now, only literal ranges are supported for target selectors.

### Target Selector

Used with special character `@`. The syntax is slightly different from Minecraft target selectors.

## Control Flows

### While Loop

Used with keyword `while`. This loop is used for typical programming loops.

### For Loop

Used with keyword `as`. This loop is specifically used for iterating all entities that fits on given selectors.

# Implementation Specifications

## Data memory mechanism

Every data is represented by `int`, `float`, `bool`, `string`, `list`, or `compound` in Minecraft NBT form.
For `int`, we mix scoreboard variables and data storage.
For other types, we use data storage.

Every internal data operation will happen in either `/scoreboard players` in some reserved objectives or `/data` in `(namespace):system`.

For scoreboard, following are list of objectives getting maintained.

- `(namespace):constants`: All constants goes here. None of integers in this objective change.
- `(namespace):variables`: All internal variable goes here.

Following is the data structure of internal system.
Note that the whole structure is very similar to json syntax,
but you cannot use different types of values in list.
For this reason, `tuple` is not supported in this language.

```jsonc
{
    // All `stack` variables goes here, where `stack` means the concept from computer memory architecture.
    // Whenever async call is happened, the current stack variables move to `schedules`.
    "stack": [
        1,
        {"some_property": [1, 2, 3]}
    ],

    // Schedules is
    "schedules": {
        "0": [
            {},
        ]
    },
    //
}
```

## There is no reference

Since Minecraft does not support reference in game, we should always use function macro,
and macro is not a cheap way to access data.

# Principles

This document describes some principles and philosophies that involved into design of MCDIL.

### 1. Never trust any value as intermediates other than scoreboard integers and data storages.

The list of trustable values during the function execution are following;

- Scoreboard values.
- Data storages.

Other than the aboves, you should capture everything at the beginning of the function call whatever you need to calculate, and output those at the end of the function. Never refer those during the intermediate calculations.

### 2. Every function execution is atomic.

Minecraft ensures that every function execution is an atomic.
There are few exceptions like `/worldborder` though.
Similar manners are applied in this language.
Every trustable local state should be reliable, even after async calls.

### 3. Take more memory than sacrificing runtime performance whenever possible.

I don't care about the number of functions or duplicated commands here.
If that has much lighter runtime performance, we goes for that.

### 4. A MCDIL function does not guarantee to run code on async call if the original executor is killed.

Since `/schedule` does not store the information, I introduce a different way to execute various functions in same tick but under different entities.
However, the calling entity must be alive, otherwise the function will not be executed.

### 5. Not every semantics are predictable during runtime, therefore I always consider the worst case.

Suppose you conditionally call some delay.
Then the compiler always asssume the delay is always happening, even if there are some cases which does not call delay at all.

### 6. MCDIL don't differentiate sync and async calls.

This is because all function executions are atomic,
and sync delays are not fundamentally different from async calls in Minecraft.

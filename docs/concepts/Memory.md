# Memory Implementations

This document describes how memory structure is implemented.

## Every data has form of score or NBT

Every data is represented by `int`, `float`, `bool`, `string`, `list`, or `compound` in Minecraft NBT form.
For `int` and `bool`, we mix scoreboard variables and data storage.
For other types, we use data storage.

## Scoreboard Objectives

For scoreboard, following are list of objectives getting maintained.

- `(namespace).constants`: All constants goes here. None of integers in this objective change.
- `(namespace).variables`: All internal variable goes here.
- `(namespace).system.*`: All system objectives created by compiler intrinstic goes here.

## Data Storage

Following is the data structure of internal system, `(namespace):system`.
You must not touch this system storage manually, unless you know what you are doing.
Note that the whole structure is very similar to json syntax,
but you cannot use different types of values in list.
For this reason, `tuple` is not supported in this language.

```jsonc
{
    // All `stack` variables goes here, where `stack` means the concept from computer memory architecture.
    // Stack does not store name of variables, because MCDIL knows mapping order.
    // Whenever async call is happened, the current stack variables move to `schedules`.
    "stack": [
        1,
        {"some_property": [1, 2, 3]}
    ],

    // All temporary data goes here.
    // All data in this scope becomes volatile after the current block ends.
    "temp": {},

    // List of async calls.
    // When async call is happened, the whole variables
    // are stored here instead of `stack`.
    "async": {

        // Every async call will have two IDs.
        // Primary ID means exact location in the code,
        // and secondary ID is a randomly generated unique ID for every call.
        // which stores list of information about all local states.
        // This information terminates when awaiting is successfully completed,
        // by calling function `(namespace):system/async/resolve/(some_primary_id)`
        // with parameter `{"secondary": (some_secondary_id)}`.
        "(some_primary_id)": {
            "(some_secondary_id)": {

                // Stores an executor information.
                // Unlike `/execute`, MCDIL stores only necessary information,
                // because we can't guarantee same behaviour when
                // running exact entity selector again.
                "executor": {

                    // If the function should be executed without an entity,
                    // then `uuid` is not set.
                    "uuid": [1234567, 8901234, 5678901, 2345678],

                    // Coordinates information.
                    // These tags should be always available.
                    "location": [0.0, -2.0, 1.0],
                    "is_location_relative": true,
                    "rotation": [30.0, -30.0],
                    "is_rotation_relative": false,

                    // Optional dimension information.
                    "dimension": "minecraft:overworld",
                },

                // Every entry of this compound will be
                // something like `{variable_name: value, ...}`.
                // We don't store type information here,
                // as MCDIL is statically typed language.
                // We don't store null variable here,
                // because there is only one value.
                "data": {
                    "(some_int_variable)": 999,
                    "(some_struct_variable)": {
                        "(some_property_1)": -1234,
                        "(some_property_2)": "MCDIL is nice",
                        // ...
                    }
                }
            }
        },
        // ...
    },
    //
}
```

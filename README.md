# json-operations
Specify complex conditional operations in JSON. The conditional operations can be run securely
against a JSON value (Python dictionary) and will return a boolean. 



```python
from json_operations import execute
operations = [">", ["key", "items"], 30]
data1 = {
    "items": 31
}
data2 = {
    "items": 29
}

execute(operations, data1) # -> True
execute(operations, data2) # -> False
```

## Security
All operations are safe (no use of eval). It's good to enforce a length limit if you are taking input
from an untrusted source.

## API
```python
from json_operations import execute

execute(<operations>, <data_dictionary>)
```

## Operators
### == (Equal operator)
Check whether one value equal to another.

##### Syntax
```python
["==", <operator_or_literal>, <operator_or_literal>]
```

##### Example
```python
from json_operations import execute
operations = ["==", ["key", "items"], 30]
data1 = {
    "items": 30
}
data2 = {
    "items": 31
}

execute(operations, data1) # -> True
execute(operations, data2) # -> False
```

### != (Not equal operator)
Check whether one value is not equal to another.

##### Syntax
```python
["!=", <operator_or_literal>, <operator_or_literal>]
```

##### Example
```python
from json_operations import execute
operations = ["!=", ["key", "items"], 30]
data1 = {
    "items": 30
}
data2 = {
    "items": 31
}

execute(operations, data1) # -> False
execute(operations, data2) # -> True
```

### \> (Greater than operator)
Check whether one value is greater than another.

##### Syntax
```python
[">", <operator_or_literal>, <operator_or_literal>]
```

##### Example
```python
from json_operations import execute
operations = [">", ["key", "items"], 30]
data1 = {
    "items": 31
}
data2 = {
    "items": 29
}

execute(operations, data1) # -> True
execute(operations, data2) # -> False
```

### \>= (Greater than or equal operator)
Check whether one value is greater than or equal to another.

##### Syntax
```python
[">=", <operator_or_literal>, <operator_or_literal>]
```

##### Example
```python
from json_operations import execute
operations = [">=", ["key", "items"], 30]
data1 = {
    "items": 30
}
data2 = {
    "items": 29
}

execute(operations, data1) # -> True
execute(operations, data2) # -> False
```

### < (Less than operator)
Check whether one value is less than another.

##### Syntax
```python
["<", <operator_or_literal>, <operator_or_literal>]
```

##### Example
```python
from json_operations import execute
operations = ["<", ["key", "items"], 30]
data1 = {
    "items": 31
}
data2 = {
    "items": 29
}

execute(operations, data1) # -> False
execute(operations, data2) # -> True
```

### < (Less than or equal operator)
Check whether one value is less or equal to than another.

##### Syntax
```python
["<=", <operator_or_literal>, <operator_or_literal>]
```

##### Example
```python
from json_operations import execute
operations = ["<=", ["key", "items"], 30]
data1 = {
    "items": 31
}
data2 = {
    "items": 30
}

execute(operations, data1) # -> False
execute(operations, data2) # -> True
```

### in (In operator)
Check whether one value is contained in another.

##### Syntax
```python
["in", <operator_or_literal>, <operator_or_literal>]
```

##### Example
```python
from json_operations import execute
operations = ["in", "my_type",  ["key", "types"]]
data1 = {
    "types": [
        "type1", "type2"
    ]
}
data2 = {
    "types": [
        "my_type", "type1"
    ]
}

execute(operations, data1) # -> False
execute(operations, data2) # -> True
```

### and (And operator)
Check whether all values are True. `and` supports nesting other operation inside
it (See complex example).

##### Syntax
```python
["and", ...<operators_or_literals>]
```

##### Examples
```python
from json_operations import execute
operations = ["and", ["key", "a"],  ["key", "b"]]
data1 = {
    "a": True,
    "b": False,
}
data2 = {
    "a": True,
    "b": True,
}

execute(operations, data1) # -> False
execute(operations, data2) # -> True
```

### or (Or operator)
Check whether any values are True. `or` supports nesting other operation inside
it (See complex example).

##### Syntax
```python
["or", ...<operators_or_literals>]
```

##### Examples
```python
from json_operations import execute
operations = ["or", ["key", "a"],  ["key", "b"]]
data1 = {
    "a": False,
    "b": False,
}
data2 = {
    "a": False,
    "b": True,
}

execute(operations, data1) # -> False
execute(operations, data2) # -> True
```

## Complex Operator Example
```python
from json_operations import execute

# (a > 1 or b < 5) and (c == 0 or d != 10) and (val in e or f >= 0)
operations = ["and", 
                ["or", [">", ["key", "a"], 1], ["<", ["key", "b"], 5]], 
                ["or", ["==", ["key", "c"], 0], ["!=", ["key", "d"], 10]],
                ["or", ["in", "val",  ["key", "e"]], [">=", ["key", "f"], 0]],
              ]
data1 = {
    "a": 0,
    "b": 5,
    "c": 0,
    "d": 9,
    "e": ["val", "another_val"],
    "f": 0,
}
data2 = {
    "a": 0,
    "b": 4,
    "c": 0,
    "d": 9,
    "e": ["val", "another_val"],
    "f": -1,
}
# (0 > 1 or 5 < 5) and (0 == 0 or 9 != 10) and (val in ["val", "another_val"] or 0 >= 0)
execute(operations, data1) # -> False

# (0 > 1 or 4 < 5) and (0 == 0 or 9 != 10) and (val in ["val", "another_val"] or -1 >= 0)
execute(operations, data2) # -> True
```

## Differences from json-logic 
https://jsonlogic.com/

- Operations are always type safe (cannot compare different types). json-logic will automatically convert different types and compare them, which can lead to issues that are tough to find
- Invalid operations are errors instead of ignored. json-logic tries to avoid all errors and instead continues with unexpected input. This can lead to issues
- More compact and intuitive syntax:
```python
["or", ["key", "a"], ["key", "b"]]
``` 
vs 
```python
{"or": [{"var": ["a"]}, {"var": ["b"]}]}
```
- Only supports boolean logic. json-logic supports all types of operations (addition, subtraction, etc.), not just boolean logic

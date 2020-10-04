# typecheck
A Python utility to perform runtime type check on call arguments.

## Usage
The utility allows for multiple ways of performing type check on call arguments.

```python
from typecheck import typecheck

# One single type for arguments and keyword arguments;
@typecheck(int, int, prompt=str)
def sum_print(x, y, prompt='The sum of {} and {} is {}.'):
    print(prompt.format(str(x), str(y), str(x+y)))
 
# A valid call;
sum_print(1, 2, prompt="{} + {} = {}")

# An invalid call, as prompt is an integer rather than expected string;
# raises an InvalidArgumentType exception.
sum_print(1, 2, prompt=42)
```

Multiple types can be specified for any argument; note this is done on a per-argument basis and each individual specification is independent of other argument specifications.

```python
from typecheck import typecheck

# One single type for arguments and keyword arguments;
@typecheck(int, (int,str))
def is_answer_to_everything(x, y):
    if x == 42:
        print(y)
 
# A valid call;
is_answer_to_everything(42, 'Yes!')

# An invalid call, as the second argument is neither an integer nor a string;
# raises an InvalidArgumentType exception.
is_answer_to_everything(42, [4, 2])
```

Custom behaviour can also be specified upon a failed type check, replacing the default exception raising.

```python
from typecheck import typecheck_plus

# One single type for arguments and keyword arguments;
def on_type_failure(arg, name, types):
    import logging
    logging.warn('Invalid type received for arg {}'.format(name))

@typecheck_plus(on_type_failure, int, int, prompt=str)
def sum_print(x, y, prompt='The sum of {} and {} is {}.'):
    print(prompt.format(str(x), str(y), str(x+y)))
 
# An invalid call, as prompt is an integer rather than expected string;
# unlike the standard typecheck, it does not raise an InvalidArgumentType exception,
# instead it logs, as defined in the callback function.
sum_print(1, 2, prompt=42)
```

import six
import inspect

class InvalidArgumentType(Exception):
    
    def __init__(self, argument_index_or_name, argument, valid_types):

        """
        Initialises the exception to be thrown in case of a failed type check
        with an informative message.

        Args
            argument_index_or_name: int or str
                Either the positional index of the argument in the function
                call or the argument name, used to identify the failed argument.
            argument: object
                The value passed for the failed argument.
            validArgumentTypes: tuple(type,)
                The tuple of valid types which the argument can take.
        """

        super(InvalidArgumentType, self).__init__(
            "Argument {} ({}: {}) {}.".format(
                str(argument_index_or_name),
                str(argument),
                str(argument.__class__.__name__),
                (
                    "must be of type {}".format(str(valid_types[0].__name__))
                    if len(valid_types) == 1
                    else "must be of one type of {}".format(', '.join(str(x.__name__) for x in valid_types))
                )
            )
        )


class _typecheck(object):

    def __init__(self, on_invalid, *args, **kwargs):

        """
        Initialises the base _typecheck decorator.

        Args
            on_invalid: function
                Callback function specifying the behaviour upon a failed type
                check; receives (arg:object, nameOrIndex:str or int, valid_types:tuple(type,)).
            args: tuple(type or tuple(type,))
                Specify the allowed type(s) for each of the function arguments;
            kwargs: dict(arg_name:str, type or tuple(types,))
                Specify the allowed type(s) for each of the function arguments;
        """

        self._on_invalid = on_invalid
        self.arg_types = tuple((t if not t or isinstance(t, tuple) else tuple([t])) for t in args)
        self.kwarg_types = {k: (t if not t or isinstance(t, tuple) else tuple([t])) for k, t in six.iteritems(kwargs)}

    def __call__(self, f):

        def _should_skip_first_argument(f, args):
            # Attempts to determine if the first argument should be avoided in the check;
            # this would be the case with instance and class methods, as the first argument
            # always refers to the instance and class, respectively. To do so, it checks
            # if the argument contains an anttribute with the name of the function being
            # decorated; the result would however be incorrect if the first argument 
            # is a valid argument, but it is an object which contains a symbol with the
            # same name as the function being decorated; requires improvement.
            return bool(getattr(args[0], f.__name__, None))
        
        def _wrapper(*args, **kwargs):
            orig_args = tuple(args)
            should_skip_first_argument = _should_skip_first_argument(f, args)
            if six.PY3: argument_names = inspect.getfullargspec(f).args
            else: argument_names = [str(i) for i in range(len(args))]
            args = tuple(args[1:] if should_skip_first_argument else args)
            argument_names = tuple(argument_names[1:] if should_skip_first_argument else argument_names)
            
            for i, (argument, argument_name, valid_types) in enumerate(zip(args, argument_names, self.arg_types)):
                self._check(argument, argument_name, valid_types)
            for k, v in six.iteritems(kwargs):
                if k in self.kwarg_types:
                    self._check(v, k, self.kwarg_types[k])

            f(*orig_args, **kwargs)
            
        return _wrapper
    
    def _check(self, argument, argument_index_or_name, valid_types):
        if valid_types and not isinstance(argument, valid_types):
            self._on_invalid(argument, argument_index_or_name, valid_types)


class typecheck(_typecheck):

    """
    A decorator to enforce types of the arguments and keyword arguments of a
    function; if a function receives arguments or keyword arguments not
    compliant with the provided ones, an InvalidArgumentType exception is
    raised upon the function call.
    
    An example of its usage is:
    
        @typecheck(int, int, prompt=str)
        def sum_print(x, y, prompt='The sum of {} and {} is {}.'):
            print(prompt.format(str(x), str(y), str(x+y)))
            
    The above function sum_print expects to integers 'x' and 'y' as arguments
    and an optional string keyword argument 'prompt'; the function then prints
    the result of the sum of the two integers using the format of the prompt.
        
    The decorator enforces that the two arguments are integers and that the
    keyword argument is a string; failure to comply raises the exception.
    
        >>> sum_print(1, 2)
            The sum of 1 and 2 is 3.
            
        >>> sum_print(1, 2, prompt='{} + {} = {}')
            1 + 2 = 3

        >>> sum_print('hello', 'world')
            ...
            InvalidArgumentType: ...
    """

    def __init__(self, *args, **kwargs):
        super(typecheck, self).__init__(self._on_invalid, *args, **kwargs)

    def _on_invalid(self, argument, argumentIndexOrName, validTypes):
        raise InvalidArgumentType(argumentIndexOrName, argument, validTypes)


class typecheck_plus(_typecheck):

    """
    A decorator to enforce types of the arguments and keyword arguments of a
    function; if a function receives arguments or keyword arguments not
    compliant with the provided ones, the callback supplied as first argument
    to the decorator is triggered.
    
    An example of its usage is:

        def on_type_failure(arg, name, types):
            import logging
            logging.warn('Invalid type received for arg {}'.format(name))
    
        @typecheck(on_type_failure, int, int, prompt=str)
        def sum_print(x, y, prompt='The sum of {} and {} is {}.'):
            print(prompt.format(str(x), str(y), str(x+y)))
            
    The above function sum_print expects to integers 'x' and 'y' as arguments
    and an optional string keyword argument 'prompt'; the function then prints
    the result of the sum of the two integers using the format of the prompt.
        
    The decorator enforces that the two arguments are integers and that the
    keyword argument is a string; failure to comply raises the exception.
    
        >>> sum_print(1, 2)
            The sum of 1 and 2 is 3.
            
        >>> sum_print(1, 2, prompt='{} + {} = {}')
            1 + 2 = 3

        >>> x = sum_print('hello', 'world')
            Warning: Invalid type received for arg x.
            Warning: Invalid type received for arg y.

        >>> x == None
            True
    """
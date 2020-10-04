import unittest
from typecheck import typecheck, typecheck_plus, InvalidArgumentType

class TestTypeCheck(unittest.TestCase):

    def test_any_type(self):

        """
        Tests that when None is specified as type for an argument, no type
        check is made for the argument.
        """

        @typecheck(int, None)
        def to_string(x, y):
            x = y
            return str(x)

        try:
            to_string(1, 9)
        except InvalidArgumentType:
            self.fail("Failed typecheck while it shouldn't have, given the first argument has the correct type and no type check should be performed on the second argument.")  

    def test_multiple_valid_type(self):

        """
        Tests that when multiple valid types are specified, the check
        succeeds for any one of them.
        """

        @typecheck((str,int))
        def to_string(x):
            return str(x)

        try:
            to_string(1)
            to_string('42')
        except InvalidArgumentType:
            self.fail("Failed typecheck while it shouldn't have, given the both calls have valid types.")  
        with self.assertRaises(InvalidArgumentType):
            to_string([1,2,3])


    def test_typecheck_plus(self):

        """
        Tests typecheck_plus, by making sure the provided callback overrides
        the default raising of the exception when a mismatching type is found.
        """

        @typecheck(int, int, prompt=str)
        def sum_string(x, y, prompt='The sum of {} and {} is {}.'):
            return prompt.format(str(x), str(y), str(x+y))

        with self.assertRaises(InvalidArgumentType):
            sum_string('hello', 'world')

        x = []
        def callback(arg, name, types):
            x.append((arg, name, types))

        @typecheck_plus(callback, int, int, prompt=str)
        def sum_string(x, y, prompt='The sum of {} and {} is {}.'):
            return prompt.format(str(x), str(y), str(x+y))

        try:
            sum_string('hello', 'world')
            self.assertEquals(len(x), 2)
        except InvalidArgumentType:
            self.fail("Failed typecheck while it shouldn't have, given the raising was disabled.")    


    def test_typecheck_raises_on_failed_check(self):

        """
        Tests the typecheck decorator, to ensure an exception is either raised
        or not depending on the validity of the passed arguments.
        """
        
        @typecheck(int, int, prompt=str)
        def sum_string(x, y, prompt='The sum of {} and {} is {}.'):
            return prompt.format(str(x), str(y), str(x+y))

        try:
            sum_string(1, 2, prompt='{} + {} = {}')
        except InvalidArgumentType:
            self.fail("Failed typecheck while it shouldn't have.")
        with self.assertRaises(InvalidArgumentType):
            sum_string('hello', 'world')

    def test_typecheck_on_class(self):

        """
        Tests that the typecheck decorator works as expected on instance,
        class and static methods within a class (namely by excluding the
        "self" and "cls" arguments of instance and class methods, respectively).
        """

        class Person(object):

            @typecheck(str, int)
            def __init__(self, first_name, age):
                self.first_name = first_name
                self.age = age

            @typecheck(bool)
            def get_name(self, capitalize):
                return self.first_name.upper() if capitalize else self.first_name

            @staticmethod
            @typecheck(str, int)
            def make(first_name, age):
                return Person(first_name, age)

            @classmethod
            @typecheck(language=str)
            def h(cls, language='en'):
                return {
                    'en': 'A class to describe a person.',
                    'it': 'Una class che descrive una persona.'
                }.get(language, 'Not available.')

        try:
            Person.make('Juan', 37)
        except InvalidArgumentType:
            self.fail("Failed typecheck on static method while it shouldn't have.")
        with self.assertRaises(InvalidArgumentType):
            Person.make('Juan', '37')

        try:
            Person('Juan', 37)
        except InvalidArgumentType:
            self.fail("Failed typecheck on instance method while it shouldn't have.")
        with self.assertRaises(InvalidArgumentType):
            Person('Juan', '37')

        try:
            Person('Juan', 37).get_name(True)
        except InvalidArgumentType:
            self.fail("Failed typecheck on instance method while it shouldn't have.")
        with self.assertRaises(InvalidArgumentType): Person('Juan', '37').get_name(True)

        try:
            Person.h(language='en')
        except InvalidArgumentType:
            self.fail("Failed typecheck on instance method while it shouldn't have.")
        with self.assertRaises(InvalidArgumentType):
            Person.h(language=17)


if __name__ == '__main__':
    unittest.main()
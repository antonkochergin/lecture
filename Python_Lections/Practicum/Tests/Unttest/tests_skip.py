import unittest


def division_func(a, b):
    """Функция деления одного числа на другое."""
    return a / b


class TestExample(unittest.TestCase):

    @unittest.expectedFailure
    def test_fail(self):
        self.assertTrue(False, 'Ожидаем истинное значение')

    def test_zero_division(self):
        # Используем метод assertRaises как контекстный менеджер
        # (записываем его со словом with); указываем ожидаемый тип исключения -
        # "ошибка деления на ноль".
        with self.assertRaises(ZeroDivisionError):
            # Передаём в функцию division_func() аргументы 1 и 0. На ноль делить нельзя,
            # поэтому должна быть вызвана ошибка ZeroDivisionError.
            division_func(1, 0)
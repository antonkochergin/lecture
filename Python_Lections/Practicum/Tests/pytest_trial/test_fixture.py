import pytest


@pytest.fixture
def give_me_a_string():
    return 'Какой чудесный день!'


# Новая фикстура возвращает список со строкой из первой фикстуры.
@pytest.fixture
def pack_to_list(give_me_a_string):  # Фикстура может вызывать другие фикстуры.
    return [give_me_a_string]


# Тестовая функция использует обе фикстуры и проверяет их содержимое.
def test_string_fixture(pack_to_list, give_me_a_string):
    assert pack_to_list != [give_me_a_string]
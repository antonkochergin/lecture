import pytest

from engine_class import Engine


@pytest.fixture
def engine():
    """Фикстура возвращает экземпляр класса двигателя."""
    print('Engine factory')  # Добавьте вывод сообщения.
    return Engine()


@pytest.fixture(autouse=True)
def start_engine(engine):
    """Фикстура запускает двигатель."""
    engine.is_running = True


def test_engine_is_running(engine):  
    """Тест проверяет, работает ли двигатель."""
    assert engine.is_running


# Допишите новый тест.
def test_check_engine_class(engine):
    """Тест проверяет класс объекта."""
    assert isinstance(engine, Engine)
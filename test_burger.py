import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from unittest.mock import Mock

# Подмена модулей praktikum для корректного импорта Burger
from bun import Bun
from ingredient import Ingredient

mock_praktikum = Mock()
mock_bun_module = Mock()
mock_bun_module.Bun = Bun
mock_ingredient_module = Mock()
mock_ingredient_module.Ingredient = Ingredient

sys.modules['praktikum'] = mock_praktikum
sys.modules['praktikum.bun'] = mock_bun_module
sys.modules['praktikum.ingredient'] = mock_ingredient_module

from burger import Burger
import pytest

@pytest.fixture
def burger():
    return Burger()

@pytest.fixture
def mock_bun():
    bun = Mock(spec=Bun)
    bun.get_name.return_value = "black bun"
    bun.get_price.return_value = 100
    return bun

class TestBurger:
    def test_set_buns(self, burger, mock_bun):
        burger.set_buns(mock_bun)
        assert burger.bun == mock_bun

    def test_add_ingredient(self, burger):
        ingredient = Mock(spec=Ingredient)
        burger.add_ingredient(ingredient)
        assert len(burger.ingredients) == 1
        assert burger.ingredients[0] == ingredient

    def test_remove_ingredient_first(self, burger):
        ing1 = Mock(spec=Ingredient)
        ing2 = Mock(spec=Ingredient)
        burger.add_ingredient(ing1)
        burger.add_ingredient(ing2)
        burger.remove_ingredient(0)
        assert len(burger.ingredients) == 1
        assert burger.ingredients[0] == ing2

    def test_remove_ingredient_last(self, burger):
        ing1 = Mock(spec=Ingredient)
        ing2 = Mock(spec=Ingredient)
        burger.add_ingredient(ing1)
        burger.add_ingredient(ing2)
        burger.remove_ingredient(1)
        assert len(burger.ingredients) == 1
        assert burger.ingredients[0] == ing1

    def test_remove_ingredient_single(self, burger):
        ing = Mock(spec=Ingredient)
        burger.add_ingredient(ing)
        burger.remove_ingredient(0)
        assert len(burger.ingredients) == 0

    def test_remove_ingredient_invalid_index(self, burger):
        ing = Mock(spec=Ingredient)
        burger.add_ingredient(ing)
        with pytest.raises(IndexError):
            burger.remove_ingredient(1)

    def test_move_ingredient_same_index(self, burger):
        ing1 = Mock(spec=Ingredient)
        ing2 = Mock(spec=Ingredient)
        burger.add_ingredient(ing1)
        burger.add_ingredient(ing2)
        burger.move_ingredient(0, 0)
        assert burger.ingredients[0] == ing1
        assert burger.ingredients[1] == ing2

    def test_move_ingredient(self, burger):
        ing1 = Mock(spec=Ingredient)
        ing2 = Mock(spec=Ingredient)
        burger.add_ingredient(ing1)
        burger.add_ingredient(ing2)
        burger.move_ingredient(0, 1)
        assert burger.ingredients[0] == ing2
        assert burger.ingredients[1] == ing1

    def test_move_ingredient_from_end_to_start(self, burger):
        ing1 = Mock(spec=Ingredient)
        ing2 = Mock(spec=Ingredient)
        burger.add_ingredient(ing1)
        burger.add_ingredient(ing2)
        burger.move_ingredient(1, 0)
        assert burger.ingredients[0] == ing2
        assert burger.ingredients[1] == ing1

    def test_get_price_only_bun(self, burger, mock_bun):
        burger.set_buns(mock_bun)
        assert burger.get_price() == 200

    def test_get_price_no_bun(self, burger):
        ing = Mock(spec=Ingredient)
        burger.add_ingredient(ing)
        with pytest.raises(AttributeError):
            burger.get_price()

    def test_get_receipt_no_bun(self, burger):
        ing = Mock(spec=Ingredient)
        burger.add_ingredient(ing)
        with pytest.raises(AttributeError):
            burger.get_receipt()

    @pytest.mark.parametrize("sauce_count, filling_count, expected_price", [
        (0, 0, 200),
        (1, 0, 250),
        (1, 1, 320)
    ])
    def test_get_receipt(self, burger, mock_bun, sauce_count, filling_count, expected_price):
        burger.set_buns(mock_bun)
        for _ in range(sauce_count):
            sauce = Mock(spec=Ingredient)
            sauce.get_type.return_value = "sauce"
            sauce.get_name.return_value = "hot sauce"
            sauce.get_price.return_value = 50
            burger.add_ingredient(sauce)
        for _ in range(filling_count):
            filling = Mock(spec=Ingredient)
            filling.get_type.return_value = "filling"
            filling.get_name.return_value = "cheese"
            filling.get_price.return_value = 70
            burger.add_ingredient(filling)
        lines = [f"(==== {mock_bun.get_name()} ====)"]
        for ing in burger.ingredients:
            lines.append(f"= {ing.get_type()} {ing.get_name()} =")
        lines.append(f"(==== {mock_bun.get_name()} ====)")
        lines.append("")
        lines.append(f"Price: {expected_price}")
        expected = "\n".join(lines)
        assert burger.get_receipt() == expected
        
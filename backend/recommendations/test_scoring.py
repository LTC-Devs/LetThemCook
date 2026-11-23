"""Pure scorer tests: no DB setup is required for these cases."""
from decimal import Decimal
from django.test import SimpleTestCase
from .scoring import score_recipe


class SimpleScoringTests(SimpleTestCase):
    def test_full_pantry_and_expiring_stock_scores_100(self):
        score = score_recipe({1: Decimal('100')}, {1: Decimal('100')}, {1: Decimal('100')})
        self.assertEqual(score.total, 100)
        self.assertEqual(score.missing_count, 0)

    def test_partial_quantities_reduce_score(self):
        score = score_recipe({1: Decimal('100')}, {1: Decimal('40')}, {})
        self.assertEqual(score.total, 24)
        self.assertEqual(score.missing_count, 1)

    def test_missing_stock_scores_zero(self):
        self.assertEqual(score_recipe({1: Decimal('100')}, {}, {}).total, 0)

    def test_does_not_count_urgent_stock_above_available(self):
        score = score_recipe({1: Decimal('100')}, {1: Decimal('20')}, {1: Decimal('80')})
        self.assertEqual(score.expiring, 3)

    def test_zero_ingredient_recipes_are_not_scored(self):
        self.assertEqual(score_recipe({}, {}, {}).total, 0)

import json
import unittest
from ..app import routes


class TestWebServer(unittest.TestCase):
    def setUp(self):
        self.questions_best_is_min = [
            'Percent of adults aged 18 years and older who have an overweight classification',
            'Percent of adults aged 18 years and older who have obesity',
            'Percent of adults who engage in no leisure-time physical activity',
            'Percent of adults who report consuming fruit less than one time daily',
            'Percent of adults who report consuming vegetables less than one time daily'
        ]

        self.questions_best_is_max = [
            'Percent of adults who achieve at least 150 minutes a week of moderate-intensity '
            'aerobic physical activity or 75 minutes a week of vigorous-intensity '
            'aerobic activity (or an equivalent combination)',

            'Percent of adults who achieve at least 150 minutes a week of '
            'moderate-intensity aerobic physical activity or 75 minutes a '
            'week of vigorous-intensity aerobic physical activity and engage '
            'in muscle-strengthening activities on 2 or more days a week',

            'Percent of adults who achieve at least 300 minutes a week of '
            'moderate-intensity aerobic physical activity or 150 minutes a '
            'week of vigorous-intensity aerobic activity (or an equivalent combination)',
            'Percent of adults who engage in muscle-strengthening activities on 2 '
            'or more days a week',
        ]
        with open("small_dict.json", "r") as file:
            self.questions_dict = json.load(file)
        self.question_1 = self.questions_best_is_min[1]
        self.question_2 = self.questions_best_is_max[1]

    def test_calculate_states_mean(self):
        print(routes.calculate_states_mean(self.question_1, self.questions_dict))
        self.assertEqual('foo'.upper(), 'FOO')

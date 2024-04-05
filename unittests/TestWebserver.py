"""
Testing module for methods defined for the flask server endpoints
"""
import json
import unittest
from app.routes import calculate_states_mean, \
    calculate_state_mean, \
    calculate_best5, \
    calculate_worst5, \
    calculate_global_mean, \
    calculate_diff_from_mean, \
    calculate_state_diff_from_mean, \
    calculate_mean_by_category, \
    calculate_state_mean_by_category
from app.routes import webserver


class TestWebserver(unittest.TestCase):
    """
    Testing class for 'calculate' methods in app/routes.py
    """

    def setUp(self):
        """
        Initialize data structures that will be used for testing
        Reads from small_dict.json to create the 'all_questions'a dictionary
        """
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
        with open("unittests/small_dict.json", "r", encoding='utf-8') as file:
            self.questions_dict = json.load(file)
        self.question_1 = self.questions_best_is_min[0]
        self.question_2 = self.questions_best_is_max[0]
        self.my_logger = webserver.my_logger

    def test_calculate_states_mean(self):
        """
        Calculates the result and compares it to reference
        """
        result = calculate_states_mean(self.question_1, self.questions_dict, self.my_logger)
        self.assertEqual(result, {'Wisconsin': 29.518181818181816,
                                  'Utah': 32.725,
                                  'Vermont': 32.87777777777777,
                                  'Illinois': 34.18181818181818,
                                  'Maryland': 34.635714285714286,
                                  'North Dakota': 38.17})

    def test_calculate_state_mean(self):
        """
        Calculates the result and compares it to reference
        """
        result = calculate_state_mean(self.question_1, "Utah", self.questions_dict, self.my_logger)
        self.assertEqual(result, {'Utah': 32.725})

    def test_calculate_best5(self):
        """
        Calculates the result and compares it to reference
        """
        result = calculate_best5(self.question_1, self.questions_dict,
                                 self.questions_best_is_max, self.my_logger)
        self.assertEqual(result, {'Wisconsin': 29.518181818181816,
                                  'Utah': 32.725,
                                  'Vermont': 32.87777777777777,
                                  'Illinois': 34.18181818181818,
                                  'Maryland': 34.635714285714286})

    def test_calculate_worst5(self):
        """
        Calculates the result and compares it to reference
        """
        result = calculate_worst5(self.question_2, self.questions_dict,
                                  self.questions_best_is_min, self.my_logger)
        self.assertEqual(result, {'Puerto Rico': 27.366666666666664,
                                  'Arkansas': 43.8375,
                                  'Kansas': 47.400000000000006,
                                  'Missouri': 47.54,
                                  'Virginia': 50.64})

    def test_calculate_global_mean(self):
        """
        Calculates the result and compares it to reference
        """
        result = calculate_global_mean(self.question_2, self.questions_dict, self.my_logger)
        self.assertEqual(result, {'global_mean': 46.369565217391305})

    def test_calculate_diff_from_mean(self):
        """
        Calculates the result and compares it to reference
        """
        result = calculate_diff_from_mean(self.question_2, self.questions_dict, self.my_logger)
        self.assertEqual(result, {'Puerto Rico': 19.00289855072464,
                                  'Arkansas': 2.532065217391306,
                                  'Kansas': -1.030434782608701,
                                  'Missouri': -1.1704347826086945,
                                  'Virginia': -4.270434782608696,
                                  'Idaho': -9.5554347826087})

    def test_calculate_state_diff_from_mean(self):
        """
        Calculates the result and compares it to reference
        """
        result = calculate_state_diff_from_mean(self.question_2, "Missouri",
                                                self.questions_dict, self.my_logger)
        self.assertEqual(result, {'Missouri': -1.1704347826086945})

    def test_calculate_mean_by_category(self):
        """
        Calculates the result and compares it to reference
        """
        result = calculate_mean_by_category(self.question_2, self.questions_dict, self.my_logger)
        self.assertEqual(result,
                         {"('Idaho', 'Race/Ethnicity', 'Asian')": 49.8,
                          "('Idaho', 'Race/Ethnicity', 'American Indian/Alaska Native')": 70.9,
                          "('Idaho', 'Age (years)', '55 - 64')": 59.5,
                          "('Idaho', 'Age (years)', '45 - 54')": 56.1,
                          "('Idaho', 'Education', 'Less than high school')": 46.4,
                          "('Idaho', 'Education', 'High school graduate')": 49.1,
                          "('Puerto Rico', 'Income', '$25,000 - $34,999')": 26.6,
                          "('Puerto Rico', 'Income', 'Data not reported')": 22.0,
                          "('Puerto Rico', 'Age (years)', '65 or older')": 30.2,
                          "('Puerto Rico', 'Age (years)', '55 - 64')": 29.3,
                          "('Puerto Rico', 'Total', 'Total')": 34.1,
                          "('Arkansas', 'Race/Ethnicity', 'Non-Hispanic Black')": 38.5,
                          "('Arkansas', 'Race/Ethnicity', '2 or more races')": 51.7,
                          "('Arkansas', 'Gender', 'Female')": 42.15,
                          "('Arkansas', 'Gender', 'Male')": 48.5,
                          "('Arkansas', 'Education', 'Some college or technical school')": 47.55,
                          "('Arkansas', 'Education', 'Less than high school')": 32.6,
                          "('Virginia', 'Education', 'High school graduate')": 46.349999999999994,
                          "('Virginia', 'Education', 'Less than high school')": 37.6,
                          "('Virginia', 'Age (years)', '45 - 54')": 49.05,
                          "('Virginia', 'Age (years)', '65 or older')": 50.650000000000006,
                          "('Virginia', 'Race/Ethnicity', 'Asian')": 56.4,
                          "('Virginia', 'Race/Ethnicity', 'American Indian/Alaska Native')": 60.15,
                          "('Kansas', 'Income', '$25,000 - $34,999')": 45.35,
                          "('Kansas', 'Income', 'Data not reported')": 46.9,
                          "('Kansas', 'Gender', 'Female')": 47.9,
                          "('Kansas', 'Gender', 'Male')": 50.0,
                          "('Kansas', 'Race/Ethnicity', 'Hispanic')": 45.45,
                          "('Kansas', 'Race/Ethnicity', 'American Indian/Alaska Native')": 50.1,
                          "('Missouri', 'Race/Ethnicity', 'Asian')": 45.5,
                          "('Missouri', 'Race/Ethnicity', 'Other')": 49.8,
                          "('Missouri', 'Gender', 'Female')": 42.5,
                          "('Missouri', 'Gender', 'Male')": 49.95})

    def test_calculate_state_mean_by_category(self):
        """
        Calculates the result and compares it to reference
        """
        result = calculate_state_mean_by_category(self.question_2, "Missouri",
                                                  self.questions_dict, self.my_logger)
        self.assertEqual(result, {"Missouri": {"('Race/Ethnicity', 'Asian')": 45.5,
                                               "('Race/Ethnicity', 'Other')": 49.8,
                                               "('Gender', 'Female')": 42.5,
                                               "('Gender', 'Male')": 49.95}})

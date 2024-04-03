"""
Module for data ingestion and processing related to physical activity.

Provides the `DataIngestor` class for reading and organizing data from a CSV file
containing information about physical activity levels across various states and years.
"""

import csv


class DataIngestor:
    """
       Ingests and organizes data from a CSV file related to physical activity.

       **Attributes:**

       * `questions_dict` (dict): A nested dictionary storing the ingested data.
           - Key (outermost): Question text (string)
           - Value (inner dictionary):
               - Key (inner): State name (string)
               - Value (inner dictionary):
                   - Key (inner): Stratification category (string)
                   - Value (inner dictionary):
                       - Key (inner): Stratification (string)
                       - Value (inner dictionary):
                           - Key (inner): Year (string)
                           - Value (inner): Data value (string)
       """
    def __init__(self, csv_path: str):

        self.questions_dict = {}

        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)

            for row in csvreader:
                state_name = row['LocationDesc']
                year = row['YearStart']
                question = row['Question']
                data_value = row['Data_Value']
                stratification_category = row['StratificationCategory1']
                stratification = row['Stratification1']

                if question not in self.questions_dict:
                    self.questions_dict[question] = {}

                states_dict = self.questions_dict[question]

                if state_name not in states_dict:
                    states_dict[state_name] = {}

                stratification_categories_dict = states_dict[state_name]

                if stratification_category not in stratification_categories_dict:
                    stratification_categories_dict[stratification_category] = {}

                stratifications_dict = stratification_categories_dict[stratification_category]

                if stratification not in stratifications_dict:
                    stratifications_dict[stratification] = {}

                data_values_dict = stratifications_dict[stratification]

                if year not in data_values_dict:
                    data_values_dict[year] = data_value

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

"""
This module provides utility functions for handling and analyzing football match fixtures and predictions.
Functions:
    get_fixtures():
        Reads the fixtures data from a CSV file, drops rows with NaN values, and returns the DataFrame.
    get_weeks_fixtures(fixtures_df, matchweek_no):
        Filters the fixtures DataFrame to return only the fixtures for the specified match week.
    get_this_week(df):
        Finds and returns the fixtures for the current week based on today's date.
    highlight_rows(s):
        Highlights rows in a DataFrame based on the comparison of actual and predicted results and scores.
    get_points(df):
        Calculates and returns the total points based on the accuracy of predicted scores and results.
"""
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

def get_fixtures() -> pd.DataFrame:
    df = pd.read_csv(f'{parent_dir}/data/2024-25.csv', index_col=0)
    df.dropna(thresh=7, inplace=True) # Dropping any NaN rows in the data
    return df


def get_weeks_fixtures(fixtures_df: pd.DataFrame, matchweek_no: int) -> pd.DataFrame:
    fixtures_df = fixtures_df.loc[fixtures_df['Wk'] == matchweek_no]
    return fixtures_df


def get_this_week(df: pd.DataFrame) -> pd.DataFrame:
    ''' Get this week's results'''
    df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d").dt.date
    today = datetime.today().date()

    def find_matching_rows(date):
        matched_row = df[df['Date'] == date]
        if not matched_row.empty:
            matching_week = matched_row['Wk'].values[0]
            result_df = df[df['Wk'] == matching_week]
            return result_df, matching_week
        else:
            return None
    
    # Iterate over the last 7 days (including today)
    result_df = None
    for i in range(7):
        check_date = today - timedelta(days=i)
        result_df = find_matching_rows(check_date)
        if result_df is not None:
            break
    return result_df


def highlight_rows(s) -> pd.DataFrame:
    styles = pd.DataFrame('', index=s.index, columns=s.columns)
    styles.loc[(s['Result'] == s['PredResult']) & (s['Score'].notna()),:] = 'background-color: #FFDB58'
    styles.loc[s['Score'] == s['PredScore'],:] = 'background-color: #3CB371'
    return styles


def get_points(df: pd.DataFrame) -> int:
    """Function to calculate the points scored based on the accuracy of the predictions."""
    points = 0

    # Exact scores
    points += 3*len(df.loc[df['Score'] == df['PredScore'],:])
    
    # Close scores
    condition1 = (
        (abs(df['PredFTHG'] - df['FTHG']) <= 1) & 
        (df['PredFTAG'] == df['FTAG'])
    )

    condition2 = (
        (abs(df['PredFTAG'] - df['FTAG']) <= 1) & 
        (df['PredFTHG'] == df['FTHG'])
    )

    condition3 = (
        (abs(df['PredFTHG'] - df['FTHG']) <= 2) & 
        (df['PredFTAG'] == df['FTAG'])
    )

    condition4 = (
        (abs(df['PredFTAG'] - df['FTAG']) <= 2) & 
        (df['PredFTHG'] == df['FTHG'])
    )

    condition5 = (
        (abs(df['PredFTHG'] - df['FTHG']) <= 1) & 
        (abs(df['PredFTAG'] - df['FTAG']) <= 1)
    )
    condition6 = (abs(df['FTHG'] - df['FTAG']) == abs(df['PredFTHG'] - df['PredFTAG']))

    one_goal_out_condition = (condition1 | condition2)
    two_goals_out_condition = (condition3 | condition4 | condition5) & condition6
    # Combine conditions
    final_condition = (
        (df['Result'] == df['PredResult']) & 
        ( one_goal_out_condition | two_goals_out_condition) &
        (df['Score'] != df['PredScore']) # Can't double count the points for exact.
    )

    # Count number of rows where the conditions are met
    close_predictions_count = len(df.loc[final_condition, :])

    points += 1.5*close_predictions_count

    # Result scores

    num_result_correct = len(df.loc[(df['Result'] == df['PredResult']) & (df['Score'] != df['PredScore']) & ~final_condition,:])
    points += num_result_correct

    # Slam points
    if num_result_correct >= 10:
        points += num_result_correct
    
    elif num_result_correct >= 8:
        points += num_result_correct
    
    elif num_result_correct >= 5:
        points += num_result_correct

    return points
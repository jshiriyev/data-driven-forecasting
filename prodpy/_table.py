import calendar

import re

import pandas

class ProductionTable():

    def __init__(self,frame:pandas.DataFrame,multp:float=1.0):
        self.frame = frame*multp

    def __getitem__(self,key):
        return self.frame[key]

    def __getattr__(self,key):
        return getattr(self.frame,key)

    @property
    def monthly_rates(self):
        return self.frame.diff()

    @property
    def daily_rates(self):
        return self.frame.diff().div(self.days_in_prev_month,axis=0)

    @property
    def days_in_prev_month(self):
        return self.frame.index.to_series().apply(ProductionTable.get_previous_month_days)
    
    @staticmethod
    def get_previous_month_days(date:pandas.Timestamp) -> int:
        """
        Calculate the number of days in the previous month based on the given date.

        Parameters:
            date (pandas.Timestamp): A pandas Timestamp object representing the current date.

        Returns:
            int: The number of days in the previous month.
        """
        first_day_of_current_month = date.replace(day=1)
        last_day_of_previous_month = first_day_of_current_month-pandas.Timedelta(days=1)

        days_in_previous_month = calendar.monthrange(
            last_day_of_previous_month.year,last_day_of_previous_month.month)[1]

        return days_in_previous_month

    def drop_zero_rates(self):

        return ProductionTable(self.frame.loc[:,self.monthly_rates.sum()>0])

    def rename(self,func=None) -> pandas.DataFrame:
        """
        Renames the columns of a DataFrame based on a given function.

        Parameters:

        func (callable): A function that takes a column name as input and returns a new column name.

        Returns: frame with new column names
        """
        func = ProductionTable.extract_digits if func is None else func

        self.frame.rename(
            columns={col:func(col) for col in self.frame.columns},inplace=True)

    def subtract(self,frame:pandas.DataFrame):

        self_frame = self.frame[sorted(self.frame.columns)]

        frame = frame.reindex(self.frame.index,fill_value=0)
        frame = frame[sorted(frame.columns)]

        # Compute the difference
        difference = self_frame-frame

        # Compute the cumulative sum
        cumulative_difference = difference.sum(axis=1)

        return cumulative_difference
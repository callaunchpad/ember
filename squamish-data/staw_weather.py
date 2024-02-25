import copy
import json
import pandas as pd

import requests
from datetime import datetime
from utils import round_datetime_to_minute
import numpy as np


def parse_js_date(js_date):
    date_components = js_date.strip("Date()").split(",")
    year = int(date_components[0])
    month = int(date_components[1])
    day = int(date_components[2])
    hour = int(date_components[3])
    minute = int(date_components[4])
    second = int(date_components[5])
    date_obj = datetime(year, month, day, hour, minute, second)

    return date_obj


# Checks if date exists in df already
def date_exists(date, df):
    return date in df.index


def interpolate_series(series):
    series = series.mask(series.duplicated()).interpolate(method="linear")
    return series


# add one specific chart data to the df, like temperature_chart_data. column name is like "temperature" for example.
def add_one_chart_data_to_df(chart_data, column_name, df):
    # Convert it to a dataframe Date(2022,11,03,00,01,15)
    num_columns = len(df.columns)

    for i in range(len(chart_data["rows"])):
        row = chart_data["rows"][i]

        js_date = row["c"][0]["v"]
        parsed_date = parse_js_date(js_date)

        # round to nearest minute
        parsed_date = round_datetime_to_minute(parsed_date)

        val = row["c"][1]["v"]

        # if date doesn't exist in df, add it
        if not date_exists(parsed_date, df):
            df.loc[parsed_date] = [np.nan] * num_columns
            # df.loc[len(df)] = [""] * num_columns
            # df.at[len(df), "time"] = parsed_date

        # set temperature
        df.at[parsed_date, column_name] = float(val)


# Results get added to result_df
def read_one_day_data(df):
    url = "https://chiefcam.com/json/weather/2022-07-16"  # f"https://chiefcam.com/json/weather/{date.year}-{date.month}-{date.day}"

    response = requests.get(url)

    data = response.json()

    # Clone these otherwise GCharts changes the data format that we use elsewhere (e.g. converts dates into Date objects)
    temperature_chart_data = copy.deepcopy(data["temperature"]["chart_data"])
    humidity_chart_data = copy.deepcopy(data["humidity"]["chart_data"])
    pressure_chart_data = copy.deepcopy(data["pressure"]["chart_data"])
    precipitation_chart_data = copy.deepcopy(data["precipitation"]["chart_data"])
    wind_speed_chart_data = copy.deepcopy(data["wind"]["speed"]["chart_data"])
    wind_direction_chart_data = copy.deepcopy(data["wind"]["direction"]["chart_data"])

    add_one_chart_data_to_df(temperature_chart_data, "temperature", df)
    add_one_chart_data_to_df(humidity_chart_data, "humidity", df)
    add_one_chart_data_to_df(pressure_chart_data, "pressure", df)
    add_one_chart_data_to_df(precipitation_chart_data, "precipitation", df)
    add_one_chart_data_to_df(wind_speed_chart_data, "wind_speed", df)

    # df["pressure"] = interpolate_series(df["pressure"])

    # df = df.astype(float)
    df = df.interpolate()

    print(len(wind_speed_chart_data["rows"]))

    # temperature chart data has rows dict and columns dict
    # rows is a list
    # each row is another dict
    # ---> here's the first row {'c': [{'v': 'Date(2022,11,03,00,02,09)'}, {'v': -3.3}, {'v': '<div class="chart-tooltip"><div class="chart-tooltip-time">December 3rd, 00:02</div><div class="chart-tooltip-value">-3.3<span class="chart-tooltip-units">&deg; C</span></div>'}]}
    # if you do row['c'][index], index is which value of that row you want to get.
    # row['c'][1] seems to give the value
    # seems like for most there's 315 rows except maybe wind direction & precipitation
    # Can parse the date to get exact time - wind_direction_chart_data["rows"][0]["c"][0]['v']
    print(pressure_chart_data["rows"][0]["c"][0]["v"])

    print(df.to_string())


if __name__ == "__main__":
    df = pd.DataFrame(
        columns=[
            "temperature",
            "humidity",
            "pressure",
            "precipitation",
            "wind_speed",
        ]
    )
    # df.set_axis(
    #     ["temperature", "humidity", "pressure", "precipitation", "wind_speed"],
    #     axis="columns",
    # )

    read_one_day_data(df)

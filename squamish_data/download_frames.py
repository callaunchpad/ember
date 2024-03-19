import subprocess
import os
from datetime import datetime, timedelta
import json
import cv2
import sys

from squamish_utils import update_json, get_sunset_time, round_datetime_to_minute

date_obj_format = "%Y-%m-%d %H:%M:%S"
SQUAMISH_COORDS = (
    49.7016,
    -123.1558,  # DONT FORGET NEGATIVE
)


"""

Frames that don't exist: 10/9/18

7/2/19 - stream ended early before sunset happened :(

one that was just pure nighttime and time was way off - check for obvious nighttime'

daylight savings on november 3 2019... i think website time doesn't acct for daylight savings
maybe ignore days where daylight savings is there. don't rate those ig. or have script to comment specific days.

2023-02-26 17:48:00 has a bad image (like sunset time off ig? or daylight savings maybe)

2023-10-08 18:40:00 has a nighttime image for some reason (daylight again?

2018-02-16 17:32:00 way off (like frame is nighttime)
2018-02-18 17:35:00 way off (like frame is nighttime)
2018-03-28 just off
2018-06-19 off
2018-06-25 cooked

2019-02-09 too late
2019-03-22 cooked
2019-07-03

2022-01-07 cooked


2018-08-16


2021-07-25

2018-11-04

SUS BC TRANSITION:

2019-11-0


"""


def opencv_read_frames(m3u8_url, output_path, START_TIME, END_TIME):
    # Read JSON
    with open("json_data/data.json") as json_file:
        image_dict = json.load(json_file)

    # Set start time and end time seconds to 00 to prevent off by one errors
    START_TIME = round_datetime_to_minute(START_TIME)
    END_TIME = round_datetime_to_minute(END_TIME)

    # Read existing JSON file
    cap = cv2.VideoCapture(m3u8_url)

    if cap.isOpened() == False:
        print("---> Unable to open URL")
        return

    fps = 5  # cap.get(cv2.CAP_PROP_FPS)
    print("FPS:", fps)

    index = 0

    frame_time = datetime.strptime(
        f"{START_TIME.year}-{START_TIME.month}-{START_TIME.day} 00:00:00",
        date_obj_format,
    )

    # The timelapse starts at 23:59 the day before so have to subtract one second
    frame_time = frame_time - timedelta(minutes=1)

    # Start at last minute on previous day. Keep iterating until you're past the desired day.
    while frame_time.day <= START_TIME.day:
        # read one frame
        ret, frame = cap.read()

        # If frame not read properly
        if not ret:
            print(
                "---> Frame not read in properly! It is likely the stream is missing the necessary frames. Skipping this day. "
            )
            break

        # Format the time as HH_MM_SS
        formatted_time = frame_time.strftime("%Y-%m-%d_%H:%M:%S")

        output_name = os.path.join(output_path, f"time_{formatted_time}.jpg")

        # When you've processed a new minute in real life
        if index % fps == 0:
            frame_time += timedelta(minutes=1)

            # If the frame falls within the time bounds, save it
            if START_TIME <= frame_time <= END_TIME:
                cv2.imwrite(output_name, frame)

                # Save output name in data.json
                image_dict[output_name] = {}

        # If you've passed the end time, no need to continue reading in frames.
        if frame_time > END_TIME:
            break

        index += 1

    cap.release()
    cv2.destroyAllWindows()

    # Save new data json
    update_json(image_dict, OVERWRITE_EXISTING=True)


def build_url(year, month, day):
    return f"https://chiefcam.com/video/timelapse/{year}-{month}-{day}.m3u8"


def save_images_for_date(sunset_time, num_frames, output_dir):
    before_sunset_time = sunset_time - timedelta(minutes=num_frames // 2)
    after_sunset_time = sunset_time + timedelta(minutes=num_frames // 2)

    print("timelapse start time: ", before_sunset_time)
    print("timelapse end time: ", after_sunset_time)

    opencv_read_frames(
        build_url(sunset_time.year, sunset_time.month, sunset_time.day),
        "frames/",
        before_sunset_time,
        after_sunset_time,
    )


def store_sunset_images_in_range(
    start_date, end_date, num_frames, output_dir, OVERWRITE=False
):
    curr_date = start_date

    while curr_date <= end_date:

        sunset_time = get_sunset_time(
            curr_date, lat=SQUAMISH_COORDS[0], lon=SQUAMISH_COORDS[1]
        )

        # Check if image with this timestamp already in frames folder
        # Subtract 1 minute to match the stream which is 1 minute behind (starts at 23:59) each day.
        rounded_sunset_time = round_datetime_to_minute(sunset_time) - timedelta(
            minutes=1
        )
        formatted_time = rounded_sunset_time.strftime("%Y-%m-%d_%H:%M:%S")
        image_path = os.path.join(output_dir, f"time_{formatted_time}.jpg")

        # If image doesn't already exist, then save the frame.
        if not os.path.exists(image_path) or OVERWRITE:
            print(f"----Saving frame for {formatted_time}----")
            save_images_for_date(sunset_time, num_frames, output_dir)
        else:
            print(f"----Skipping frame for {formatted_time} as it already exists ----")

        curr_date += timedelta(days=1)


if __name__ == "__main__":
    start = datetime(2018, 1, 13)
    end = datetime(2023, 12, 31)

    store_sunset_images_in_range(start, end, num_frames=1, output_dir="frames/")

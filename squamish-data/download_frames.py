import subprocess
import os
from datetime import datetime, timedelta
import json
import cv2
import sys

from utils import update_json
from weather_utils import get_sunset_time
from utils import round_datetime_to_minute

date_obj_format = "%Y-%m-%d %H:%M:%S"


def opencv_read_frames(m3u8_url, output_path, START_TIME, END_TIME):
    # Read JSON
    with open("data.json") as json_file:
        image_dict = json.load(json_file)

    # Set start time and end time seconds to 00 to prevent off by one errors
    START_TIME = round_datetime_to_minute(START_TIME)
    END_TIME = round_datetime_to_minute(END_TIME)

    # Read existing JSON file
    cap = cv2.VideoCapture(m3u8_url)

    if cap.isOpened() == False:
        print("!!! Unable to open URL")
        sys.exit(-1)

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


def store_sunset_images_in_range(start_date, end_date, num_frames, output_dir):
    curr_date = start_date

    while curr_date <= end_date:

        sunset_time = get_sunset_time(curr_date)

        save_images_for_date(sunset_time, num_frames, output_dir)

        curr_date += timedelta(days=1)


if __name__ == "__main__":
    start = datetime(2023, 11, 8)
    end = datetime(2023, 11, 15)

    store_sunset_images_in_range(start, end, num_frames=3, output_dir="frames/")

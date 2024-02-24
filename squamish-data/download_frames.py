import subprocess
import os
from datetime import datetime, timedelta


import cv2
import sys


date_obj_format = "%Y-%m-%d %H:%M:%S"


def opencv_read_frames(m3u8_url, output_path, START_TIME, END_TIME):
    cap = cv2.VideoCapture(m3u8_url)

    if cap.isOpened() == False:
        print("!!! Unable to open URL")
        sys.exit(-1)

    fps = 5  # cap.get(cv2.CAP_PROP_FPS)
    wait_ms = int(1000 / fps)
    print("FPS:", fps)

    index = 0

    frame_time = datetime.strptime(
        f"{START_TIME.year}-{START_TIME.month}-{START_TIME.day} 00:00:00",
        date_obj_format,
    )

    # While still on this day
    while frame_time.day == START_TIME.day:
        # read one frame
        ret, frame = cap.read()

        # Format the time as HH_MM_SS
        formatted_time = frame_time.strftime("%Y-%m-%d_%H:%M:%S")

        output_name = os.path.join(output_path, f"time_{formatted_time}.jpg")

        # When you've processed a new minute in real life
        if index % fps == 0:
            # print(frame_time)

            frame_time += timedelta(minutes=1)

            # If the frame falls within the time bounds, save it
            if START_TIME <= frame_time <= END_TIME:
                cv2.imwrite(output_name, frame)

        # If you've passed the end time, no need to continue reading in frames.
        if frame_time > END_TIME:
            break

        # # display frame
        # cv2.imshow("frame", frame)
        # if cv2.waitKey(wait_ms) & 0xFF == ord("q"):
        #     break

        index += 1

    cap.release()
    cv2.destroyAllWindows()


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


if __name__ == "__main__":
    sunset_time_str = "2023-11-08 16:12:00"
    sunset_time = datetime.strptime(sunset_time_str, date_obj_format)

    save_images_for_date(sunset_time, num_frames=20, output_dir="frames/")

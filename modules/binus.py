import os
from datetime import datetime

from binusmaya_py.bimay import bimay as bimay
from decorators.rule import is_owner
from flex_templates import forum_template, scheduleTemplate
from linebot.models import TextSendMessage
from util.line_util import load_config


@is_owner
def get_next_schedule(event, **kwargs):
    bm = bimay(token=os.environ.get("BIMAY_TOKEN"))
    now = datetime.now()
    schedules = bm.get_schedule_date(now)
    schedule = sorted(
        schedules["Schedule"],
        key=lambda x: datetime.strptime(x["date_start"], "%Y-%m-%dT%H:%M:%S"),
    )
    schedule = [x for x in schedule if not x["is_ended"]]
    if len(schedule) == 0:
        return TextSendMessage(text="No schedule found for today")
    schedule = [
        x
        for x in schedule
        if datetime.strptime(x["date_start"], "%Y-%m-%dT%H:%M:%S") > now
    ][0]

    url = schedule["join_url"]
    if not url:
        url = f"https://newbinusmaya.binus.ac.id/lms/course/{schedule['class_id']}/session/{schedule['class_session_id']}"

    if schedule["location"]["location"] == None:
        location = "Virtual"
    else:
        location = schedule["location"]["location"]

    time_start_str = datetime.strptime(
        schedule["date_start"], "%Y-%m-%dT%H:%M:%S"
    ).strftime("%H:%M")
    time_end_str = datetime.strptime(
        schedule["date_end"], "%Y-%m-%dT%H:%M:%S"
    ).strftime("%H:%M")
    flex_message = scheduleTemplate(
        header="Next Schedule",
        title=schedule["course_name"],
        session=f"Session {schedule['session_number']}",
        start=time_start_str,
        end=time_end_str,
        kelas=schedule["course_class"],
        topic=schedule["topic"],
        subtopic="\n".join(f"- {sub}" for sub in schedule["subtopic"]),
        link=url,
        location=location,
    )

    return flex_message


@is_owner
def get_forum_latest_post(event, **kwargs):
    bm = bimay(token=os.environ.get("BIMAY_TOKEN"))
    line_bot = kwargs["line_bot_api"]
    forums = bm.get_forum_latest()
    forums = [x for x in forums["latestPost"] if x["isRead"]]
    for forum in forums:
        content = bm.get_forum_thread_content(
            threadId=forum["threadId"], classId=forum["classId"]
        )
        content = (
            content["threadContentText"]
            .replace("<p>", "\n")
            .replace("</p>", "")
            .replace("<br>", "\n")
            .replace("&nbsp;", " ")
        )
        post_datetime = datetime.strptime(
            forum["postDate"].strip("Z").rstrip(forum["postDate"][-1]),
            "%Y-%m-%dT%H:%M:%S.%f",
        )
        post_url = f"https://newbinusmaya.binus.ac.id/lms/course/{forum['classId']}/session/{forum['classSessionId']}/forum/thread/{forum['threadId']}"
        flex_message = forum_template(
            title=forum["threadTitle"],
            course=forum["courseName"],
            post_content=content,
            author_name=forum["authorFullName"],
            author_picture_url=forum["authorPictureUrl"],
            post_datetime=post_datetime,
            post_url=post_url,
        )
        if event == None:
            dest = load_config()["owner_id"]
        else:
            dest = event.source.user_id
        line_bot.push_message(dest, flex_message)
    if len(forums) == 0:
        return TextSendMessage(text="No unread forum post")
    return "done"

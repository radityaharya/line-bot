import os
from datetime import datetime
from binusmaya_py.bimay import bimay as bimay
import json
from flex_templates import scheduleTemplate
from decorators.rule import is_owner


@is_owner
def get_next_schedule(event, **kwargs):
    bm = bimay(token=os.environ.get("BIMAY_TOKEN"))
    # TODO: Location not working
    session_id = bm.default_classSessionId()
    class_id = bm.default_classId()
    class_info = bm.get_class_sessions_from_class_id(class_id)
    class_session_detail = bm.get_class_session_detail(session_id)

    course_name = class_info["courseTitleEn"]
    course_class = f"{class_info['classCode']} - {class_info['ssrComponent']}"
    session_number = class_session_detail["sessionNumber"]
    delivery_mode = class_session_detail["deliveryMode"]
    date_start = datetime.strptime(
        class_session_detail["dateStart"], "%Y-%m-%dT%H:%M:%S"
    )
    date_end = datetime.strptime(class_session_detail["dateEnd"], "%Y-%m-%dT%H:%M:%S")
    topic = class_session_detail["topic"]
    sub_topic = class_session_detail["courseSubTopic"]
    url = class_session_detail["joinUrl"]
    location = 'location'
    
    if not url:
        url = f"https://newbinusmaya.binus.ac.id/lms/course/{class_id}/session/{session_id}"
    
    flex_message = scheduleTemplate(
        header="Next Schedule",
        title=course_name,
        session=f"Session {session_number}",
        start=date_start.strftime("%I:%M %p"),
        end=date_end.strftime("%I:%M %p"),
        kelas=course_class,
        topic=topic,
        subtopic="\n".join(f"- {sub}" for sub in sub_topic),
        link=url,
        location=location,
    )
    
    return flex_message

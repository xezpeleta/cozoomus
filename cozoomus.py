import os
import logging
import json
from zoomus import ZoomClient
from datetime import datetime, timezone

def user_update_type(client, user, user_type):
    user_data = {
        "id": user['id'],
        "type": user_type
    }

    response = client.user.update(**user_data)
    if response.status_code == 204:
        return True
    else:
        logging.error("ERROR: cannot assign/unassign the license. More info: {}".format(response.text))
        return False

def is_meeting_soon(meeting):
    try:
        meeting_id = meeting['id']
    except:
        meeting_id = meeting['occurrence_id']

    try:
        start_time = datetime.strptime(meeting['start_time'], '%Y-%m-%dT%H:%M:%SZ')
    except:
        raise ValueError('Invalid meeting start_time: %s' % meeting['start_time'])
    logging.debug('is_meeting_soon({}) :: start_time = {}'.format(meeting_id, start_time))
    #print('test: {}'.format(utc_to_local(start_time).strftime("%H:%M:%S")))
    now = datetime.now()
    delta = abs(start_time - now).total_seconds() // 3600
    logging.debug('is_meeting_soon({}) :: delta = {} hours'.format(meeting_id, delta))
    # Match meetings before and after TIME_DELTA
    # TODO: allow using diffent deltas (TIME_DELTA_BEFORE & TIME_DELTA_AFTER)
    if delta < TIME_DELTA:
        return True
    else:
        return False

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

if __name__ == "__main__":
    # Set log level
    loglevel = os.getenv('LOGLEVEL', 'warning')
    numeric_loglevel = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_loglevel, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_loglevel)
    logging.info("SETTINGS :: LOGLEVEL = {}".format(numeric_loglevel))

    # Required enironment variables
    if "ZOOM_API_KEY" not in os.environ or "ZOOM_API_SECRET" not in os.environ:
        logging.critical("Cannot find required environment variables")
        print("[ERROR] Cannot find required environment variables:")
        print(" - ZOOM_API_KEY")
        print(" - ZOOM_API_SECRET")
        exit()

    API_KEY = os.getenv('ZOOM_API_KEY')
    API_SECRET = os.getenv('ZOOM_API_SECRET')

    # Time delta (in hours)
    # TODO: allow using diffent deltas (TIME_DELTA_BEFORE & TIME_DELTA_AFTER)
    TIME_DELTA = int(os.getenv('ZOOM_TIME_DELTA', default=24))
    logging.info("SETTINGS :: TIME_DELTA = {} (hours)".format(TIME_DELTA))

    # Available licenses
    LICENSES = int(os.getenv('ZOOM_LICENSES', default=20))
    logging.info("SETTINGS :: LICENSES = {}".format(LICENSES))

    # The following users will always keep their license
    WHITELISTED_USERS = list(os.getenv('ZOOM_WHITELISTED_USERS', default="").strip('"').split(" "))
    logging.info("SETTINGS :: WHITELISTED_USERS = {}".format(WHITELISTED_USERS))

    # User type values (ZOOM API)
    USER_NON_LICENSED = 1
    USER_LICENSED = 2

    # Meeting type values (ZOOM API)
    MEETING_TYPE_INSTANT = 1
    MEETING_TYPE_SCHEDULED = 2
    MEETING_TYPE_RECURRING_WITHOUT_TIME = 3
    MEETING_TYPE_RECURRING_WITH_TIME = 8
    
    client = ZoomClient(API_KEY, API_SECRET)
    users = json.loads(client.user.list().content)['users']

    required_licenses = 0
    recurring_meetings = 0
    recurring_meetings_notime = 0
    scheduled_meetings = 0
    for user in users:
        if user['email'] in WHITELISTED_USERS:
            if user['type'] == USER_NON_LICENSED:
                user_update_type(client, user, USER_LICENSED)
                print("[%s] User whitelisted. License assigned" % user['email'])
            else:
                logging.debug("[%s] User whitelisted. Nothing to do, already licensed" % user['email'])
            required_licenses += 1
            continue
        try:
            meetings = json.loads(client.meeting.list(user_id=user['id']).content)['meetings']
        except:
            continue
        
        for meeting in meetings:
            if meeting['type'] == MEETING_TYPE_RECURRING_WITHOUT_TIME:
                # Recurring meeting, with no fixed time
                if user['type'] == USER_NON_LICENSED:
                    user_update_type(client, user, USER_LICENSED)
                    print("[%s] Recurring meeting with no fixed time. License assigned" % user['email'])
                else:
                    print("[%s] Recurring meeting with no fixed time. Nothing to do, already licensed" % user['email'])
                required_licenses += 1
                recurring_meetings_notime += 1
                break
            if meeting['type'] == MEETING_TYPE_RECURRING_WITH_TIME:
                # Recurring meeting with fixed time
                ## We need to query for meeting occurrences
                ## and in order to do that we load "full" meeting info
                meeting = json.loads(client.meeting.get(id=meeting['id']).content)
                if 'occurrences' in meeting:
                    for occurrence in meeting['occurrences']:
                        if is_meeting_soon(occurrence):
                            if user['type'] == USER_NON_LICENSED:
                                user_update_type(client, user, USER_LICENSED)
                                print("[%s] Recurring meetings scheduled. License assigned" % user['email'])
                            else:
                                print("[%s] Recurring meetings scheduled. Nothings to do, already licensed" % user['email'])
                            required_licenses += 1
                            recurring_meetings += 1
                            break
                    else:
                        continue # all occurrences are far
                    break # there is a close occurrence
            else:
                # Scheduled meeting or instant meeting
                if is_meeting_soon(meeting):
                    if user['type'] == USER_NON_LICENSED:
                        user_update_type(client, user, USER_LICENSED)
                        print("[%s] Meetings scheduled. License assigned" % user['email'])
                    else:
                        print("[%s] Meetings scheduled. Nothing to do, already licensed" % user['email'])
                    required_licenses += 1
                    scheduled_meetings += 1
                    break
        else:
            if user['type'] == USER_LICENSED:
                user_update_type(client, user, USER_NON_LICENSED)
                print("[%s] No meetings scheduled. License removed" % user['email'])
            else:
                logging.debug("[%s] No meetings scheduled. Nothing to do" % user['email'])

    print("\n")
    print("~ SUMMARY ~")
    print("Users: %i" % len(users))
    print("Whitelisted users: %i" % len(WHITELISTED_USERS))
    print("Users with meetings: %i" % (required_licenses - len(WHITELISTED_USERS)))
    print("- Recurring meetings (no fixed time): %i" % (recurring_meetings_notime))
    print("- Recurring meetings (fixed time): %i" % (recurring_meetings))
    print("- Scheduled or live meetings: %i" % (scheduled_meetings))
    print("Assigned licenses: %i/%i" % (required_licenses, LICENSES))
    print("Available licenses: %i/%i" % ((LICENSES - required_licenses), LICENSES))
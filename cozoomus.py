import os
import json
from zoomus import ZoomClient
import datetime

def user_update_type(client, user, user_type):
    user_data = {
        "id": user['id'],
        "type": user_type
    }

    response = client.user.update(**user_data)
    if response.status_code == 204:
        return True
    else:
        print("ERROR: cannot assign/unassign the license. More info: {}".format(response.text))
        return False

def is_meeting_soon(meeting):
    try:
        start_time = datetime.datetime.strptime(meeting['start_time'], '%Y-%m-%dT%H:%M:%SZ')
    except:
        return False
    now = datetime.datetime.now()
    delta = abs(start_time - now).total_seconds() // 3600
    # Match meetings before and after TIME_DELTA
    # TODO: allow using diffent deltas (TIME_DELTA_BEFORE & TIME_DELTA_AFTER)
    if delta < TIME_DELTA:
        return True
    else:
        return False

if __name__ == "__main__":
    # Required enironment variables
    if "ZOOM_API_KEY" not in os.environ or "ZOOM_API_SECRET" not in os.environ:
        print("[ERROR] Cannot find required environment variables:")
        print(" - ZOOM_API_KEY")
        print(" - ZOOM_API_SECRET")
        exit()

    API_KEY = os.getenv('ZOOM_API_KEY')
    API_SECRET = os.getenv('ZOOM_API_SECRET')

    # Time delta (in hours)
    # TODO: allow using diffent deltas (TIME_DELTA_BEFORE & TIME_DELTA_AFTER)
    TIME_DELTA = int(os.getenv('TIME_DELTA', default=24))

    # Available licenses
    LICENSES = int(os.getenv('ZOOM_LICENSES', default=20))

    # The following users will always keep their license
    WHITELISTED_USERS = list(os.getenv('ZOOM_WHITELISTED_USERS', default="").strip('"').split(" "))

    # User type values (ZOOM API)
    USER_NON_LICENSED = 1
    USER_LICENSED = 2

    client = ZoomClient(API_KEY, API_SECRET)
    users = json.loads(client.user.list().content)['users']

    required_licenses = 0
    for user in users:
        if user['email'] in WHITELISTED_USERS:
            if user['type'] == USER_NON_LICENSED:
                user_update_type(client, user, USER_LICENSED)
                print("[%s] User whitelisted. License assigned" % user['email'])
            else:
                #print("[%s] User whitelisted. Nothing to do, already licensed" % user['email'])
                pass
            required_licenses += 1
            continue
        try:
            meetings = json.loads(client.meeting.list(user_id=user['id']).content)['meetings']
        except:
            continue
        
        for meeting in meetings:
            if is_meeting_soon(meeting):
                #print("-%s (%s)" % (meeting['topic'], meeting['start_time']))
                if user['type'] == USER_NON_LICENSED:
                    user_update_type(client, user, USER_LICENSED)
                    print("[%s] Meetings scheduled. License assigned" % user['email'])
                else:
                    print("[%s] Meetings scheduled. Nothing to do, already licensed" % user['email'])
                required_licenses += 1
                break
        else:
            if user['type'] == USER_LICENSED:
                user_update_type(client, user, USER_NON_LICENSED)
                print("[%s] No meetings scheduled. License removed" % user['email'])
            else:
                #print("No meetings scheduled. Nothing to do")
                pass

    print("\n")
    print("~ SUMMARY ~")
    print("Users: %i" % len(users))
    print("Whitelisted users: %i" % len(WHITELISTED_USERS))
    print("Users with scheduled meetings: %i" % (required_licenses - len(WHITELISTED_USERS)))
    print("Assigned licenses: %i/%i" % (required_licenses, LICENSES))
    print("Available licenses: %i/%i" % ((LICENSES - required_licenses), LICENSES))
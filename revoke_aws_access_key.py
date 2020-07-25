import boto3
import sys
import datetime
import time
import os
from slacker import Slacker

DAYS87 = 87
DAYS90 = 90
DAYS93 = 93
ORG_DOMAIN_NAME = YOUR_ORG_DOMAIN_NAME_HERE
SLACK_API_TOKEN = os.getenv('SLACK_API_TOKEN')
slack = Slacker(SLACK_API_TOKEN)
ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
SECRET_KEY = os.getenv('AWS_SECRET_KEY')
client = boto3.client('iam', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
response = client.generate_credential_report()
time.sleep(120)
response = client.get_credential_report()
credential_report = response['Content'].decode().split('\n')
timedelta87 = datetime.date.today() - datetime.timedelta(days=DAYS87)
timedelta90 = datetime.date.today() - datetime.timedelta(days=DAYS90)
timedelta93 = datetime.date.today() - datetime.timedelta(days=DAYS93)
stale_users = list()
slack_user_id = {}


def get_slack_user():
    response = slack.users.list()
    for user in response.body['members']:
        try:
            slack_user_id[user['profile']['email']] = user['id']
        except Exception as e:
            print(e)

    if len(slack_user_id) > 0:
        print('user from slack extracted')
    else:
        sys.exit(0)


def notify_user(user_id, msg):
    slack.chat.post_message(user_id, text=msg, username="AWS Bot")


def deactivate(user, AccessKeyId):
    client.update_access_key(UserName=user, AccessKeyId=AccessKeyId, Status='Inactive')


def delete(user, AccessKeyId):
    client.delete_access_key(UserName=user, AccessKeyId=AccessKeyId)


def alert_user():
    for user in stale_users:
        try:
            user_details = client.list_access_keys(UserName=user)
        except Exception as e:
            print("{0} : {1}".format(user, e))
            continue
        for user_detail in user_details['AccessKeyMetadata']:
            last_used = client.get_access_key_last_used(AccessKeyId=user_detail['AccessKeyId'])
            if 'LastUsedDate' not in last_used['AccessKeyLastUsed'].keys():
                last_used_date = user_detail['CreateDate']
            else:
                last_used_date = last_used['AccessKeyLastUsed']['LastUsedDate']
            if last_used_date.date() <= timedelta87:
                email = str(user) + "@" + ORG_DOMAIN_NAME
                if email not in slack_user_id.keys():
                    print(email)
                    continue
                else:
                    user_id = slack_user_id[email]
                try:
                    msg = "Hi `{0}`,\n We have found that your AWS Access Key ID `{1}` has not been used in the last *_87 days_*.\nFor security reasons, this key will be deactivated after 3 days.\nIn case of any query please reach out to the security team".format(user, user_detail['AccessKeyId'])
                    notify_user(user_id, msg)
                    print("{0}: {1}".format(user, user_detail['AccessKeyId']))
                except Exception as e:
                    print("{0}: {1}".format(user, e))


def make_inactive(stale_users):
    for user in stale_users:
        try:
            user_details = client.list_access_keys(UserName=user)
        except Exception as e:
            print("{0} : {1}".format(user, e))
            continue
        for user_detail in user_details['AccessKeyMetadata']:
            last_used = client.get_access_key_last_used(AccessKeyId=user_detail['AccessKeyId'])
            if 'LastUsedDate' not in last_used['AccessKeyLastUsed'].keys():
                last_used_date = user_detail['CreateDate']
            else:
                last_used_date = last_used['AccessKeyLastUsed']['LastUsedDate']
            if last_used_date.date() <= timedelta90:
                email = str(user) + "@" + ORG_DOMAIN_NAME
                if email not in slack_user_id.keys():
                    print(email)
                    continue
                else:
                    user_id = slack_user_id[email]
                try:
                    deactivate(user, user_detail['AccessKeyId'])
                    msg = "Hi `{0}`,\n We have found that your AWS Access Key ID `{1}` has not been used in the last *_90 days_*.\nFor security reasons, we have deactivated your key.\nIn case of any query please reach out to the security team".format(user, user_detail['AccessKeyId'])
                    notify_user(user_id, msg)
                    print("{0}: {1}".format(user, user_detail['AccessKeyId']))
                except Exception as e:
                    print("{0}: {1}".format(user, e))


def delete_user(stale_users):
    for user in stale_users:
        try:
            user_details = client.list_access_keys(UserName=user)
        except Exception as e:
            print("{0} : {1}".format(user, e))
            continue
        for user_detail in user_details['AccessKeyMetadata']:
            last_used = client.get_access_key_last_used(AccessKeyId=user_detail['AccessKeyId'])
            if 'LastUsedDate' not in last_used['AccessKeyLastUsed'].keys():
                last_used_date = user_detail['CreateDate']
            else:
                last_used_date = last_used['AccessKeyLastUsed']['LastUsedDate']
            if last_used_date.date() <= timedelta93:
                email = str(user) + "@" + ORG_DOMAIN_NAME
                if email not in slack_user_id.keys():
                    print(email)
                    continue
                else:
                    user_id = slack_user_id[email]
                try:
                    delete(user, user_detail['AccessKeyId'])
                    msg = "We have found `{0}` AWS access key `{1}` being unused for more than *_93 days_* so we are deleting them. In case of any query please reach out to the security team".format(user, user_detail['AccessKeyId'])
                    notify_user(user_id, msg)
                    print("{0}: {1}".format(user, user_detail['AccessKeyId']))
                except Exception as e:
                    print("{0}: {1}".format(user, e))


def main():
    for i in range(0, len(credential_report)):
        fields = credential_report[i].split(',')
        flag = True
        if fields[10] != 'N/A' and fields[10] != 'access_key_1_last_used_date':
            if datetime.datetime.fromisoformat(fields[10]).date() <= timedelta87 and fields[8] == 'true':
                stale_users.append(fields[0])
                flag = False
        elif fields[10] == 'N/A' and datetime.datetime.fromisoformat(fields[2]).date() <= timedelta87:
            stale_users.append(fields[0])
            flag = False

        if fields[15] != 'N/A' and fields[15] != 'access_key_2_last_used_date':
            if datetime.datetime.fromisoformat(fields[15]).date() <= timedelta87 and fields[13] == 'true':
                if flag:
                    stale_users.append(fields[0])
        elif fields[15] == 'N/A' and datetime.datetime.fromisoformat(fields[2]).date() <= timedelta87:
            if flag:
                stale_users.append(fields[0])

    get_slack_user()
    alert_user()
    # deactivate 90 days old access keys
    make_inactive(stale_users)
    # delete 93 days old access keys
    delete_user(stale_users)


if __name__ == "__main__":
    main()

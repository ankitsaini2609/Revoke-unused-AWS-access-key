# Revoke-unused-access-key

## What does this project do?
This script will revoke all the unused access key from aws.

## Why is this project useful?
We all want our AWS infrastructure to be secured so disabling or removing unnecessary credentials will reduce the window of opportunity for credentials associated with a compromised or abondoned account to be used. It will also enforce good practice.

## How do I get started?
There are few requirements before running the script:<br />
1- ```YOUR_ORG_DOMAIN_NAME_HERE``` -> Change it in the script.example: google.com <br />
2- ```SLACK_API_TOKEN``` -> It is used to fetch the users from the slack and send the alert. <br />
3- ```AWS_ACCESS_KEY and AWS_SECRET_KEY``` -> AWS key to fetch the credential report and find users whose key is unused.

## How the Script is working?
1- First It will fetch the credential report from the AWS then find out those users whose access key is being unused from last ```87 days```.<br />
2- Fetch the users from the slack.<br />
3- It will first call the ```alert_user()``` function which will inform user on the slack about their key is being unused from last 87 days.<br />
4- Secondly It will call ```make_inactive()``` function which will inform user that their key is being deactivated since It wasn't used from last 90 days.<br />
5- ```delete_user()``` function will delete the user keys If they are being unused from last 93 days.<br />
6- Set the ```SLACK_API_TOKEN```, ```AWS_ACCESS_KEY``` and ```AWS_SECRET_KEY``` in environment variable and open the script, set ```YOUR_ORG_DOMAIN_NAME_HERE``` then run the script as:<br /> ```python3.8 revoke_aws_access_key```.
 
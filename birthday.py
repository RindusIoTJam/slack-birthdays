import os
import urllib, json
import datetime

import config
# Date Format
dateFormat = "%b %d"

# Date formatting
def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')
def custom_strftime(format, t):
	return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

# Retrieve data
json_url = urllib.urlopen(config.EMPLOYEES_URL)
employees = json.loads(json_url.read())

# Filtering function to find today's Birthdays
today = datetime.date.today()
def isBirthdayToday(employee):
	if (employee and 'birthday' in employee and employee['birthday'] != '' and datetime.datetime.strptime(employee['birthday'], dateFormat).strftime(dateFormat) == today.strftime(dateFormat)): 
		return True
	else: 
		return False

birthdayEmployees = filter(isBirthdayToday, employees)

birthdayEmployees.sort(key=lambda x: x['first_name'])

if (len(birthdayEmployees) == 0):
	exit()

# Slack payload
data = {
	"blocks": [
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": "Today`s Birthdays :tada:\n"
			}
		},
		{
			"type": "header",
			"text": {
				"type": "plain_text",
				"text": custom_strftime("{S} %B", today)
			}
		}
	]
}

divider = {
	"type": "divider"
}

for employee in birthdayEmployees:
	employeeData = {
		"type": "section",
		"text": {
			"type": "mrkdwn",
			"text": "*" + employee["display_name"] + "*\n<@" + employee['slack_id'] + ">\n_Team_: " + employee['department'] + "\n_Position_: " + employee['title']
		},
		"accessory": {
			"type": "image",
			"image_url": "" + employee["image_192"],
			"alt_text": "" + employee["display_name"]
		}
	}
	data["blocks"].append(divider)
	data["blocks"].append(employeeData)

data["blocks"].append(divider)

# Slack POST
command = "curl --silent -X POST -H 'Content-type: application/json'"
command += " --data '" + json.dumps(data) + "'"
command += " " + config.SLACK_WEBHOOK_URL
command += " > /dev/null"

os.system(command)

import datetime
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import secrets
from datetime import date, time, datetime
import zoneinfo
kaeley_test = "G01JE299T6V"
last_user_linux_install = ""
last_date_linux_install = "Jul 15, 2025"
last_time_linux_install = "12:00 PM"
tally = []


# Initializes your app with your bot token and socket mode handler
app = App(token=secrets.slack_bot_token)
# Listens to incoming messages that contain "hello"
# To learn available listener arguments,
# visit https://tools.slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html


# this works
@app.message("testa")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>, did you need to reinstall your operating system?"},
                "accessory":
                    {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "I reinstalled"},
                    "action_id": "button_click"
                },
            }
        ],
        text=f"Hey there <@{message['user']}>, did you need to reinstall your operating system?"
    )


## works!! ### case agnostic!! ####
@app.action("reinstall")
def action_button_click(body, ack, say):
    global last_user_linux_install, last_date_linux_install, last_time_linux_install, tally
    ack()
    current_user = f"<@{body['user']['id']}>"
    current_datetime = datetime.now()
    today = current_datetime.strftime("%b %d, %Y")
    current_time = current_datetime.time().strftime("%I:%M %p")
    # print("time:", current_time)
    # print(today)
    if len(tally) != 0:
        for key, value in tally[0].items():
            print(key, value)
            if current_user == tally[0][key]:
                tally[0][current_user] += 1
            else:
                new_entry = {current_user: 0}
                new_entry[current_user] += 1
                tally.append(new_entry)
    print("tally:", tally)
    if last_user_linux_install == "":
        say(f"{current_user} reinstalled their operating system.")
        last_date_linux_install = today
        last_user_linux_install = current_user
        print("last_user_linux_install == ''")
    elif current_user == last_user_linux_install:
        if last_date_linux_install == today:
            print("current time:", current_time)
            print("last time:", last_time_linux_install)
            if last_time_linux_install < current_time:
                print("true")
                say(f"{current_user} reinstalled their operating system. They have installed their OS already today--the last time was at {last_time_linux_install}")
                last_date_linux_install = today
                last_user_linux_install = current_user
                last_time_linux_install = current_time
                print("new time:", last_time_linux_install)
                print("current_user == last_user_linux_install or current_user == ")
            else:
                say(f"{current_user} reinstalled their operating system. They were also the last person to reinstall on " + last_date_linux_install)
                last_date_linux_install = today
                last_user_linux_install = current_user
    elif current_user != last_user_linux_install:
        say(f"{current_user} reinstalled their operating system. The last person to reinstall is {last_user_linux_install}")
        last_date_linux_install = today
        last_user_linux_install = current_user
        print("last user: " + last_user_linux_install)
        print("current_user != last_user_linux_install")
    else:
        pass
    '''if current_user == last_user_linux_install or last_user_linux_install == "":
        if last_date_linux_install == today:
            if last_time_linux_install < current_time:
                say(f"{current_user} reinstalled their operating system. They have installed their OS already today--the last time was at {last_time_linux_install}")
                last_date_linux_install = today
                last_user_linux_install = current_user
                print("current_user == last_user_linux_install or current_user == ")
            else:
                say(f"{current_user} reinstalled their operating system. They were also the last person to reinstall on " + last_date_linux_install)
                last_date_linux_install = today
                last_user_linux_install = current_user
        elif last_user_linux_install == "":
            say(f"{current_user} reinstalled their operating system.")
            last_date_linux_install = today
            last_user_linux_install = current_user
            print("last_user_linux_install == ''")'''














@app.action("Nevermind")
def action_button_click(body, ack, say):
    ack()
    print(ack())
    say(f"<@{body['user']['id']}> clicked the button in error")

## experimental
@app.message("--helplinux")
def say_hello(client, message):
    if message["channel"] == kaeley_test:
       print("in correct channel")
    target_user = message["user"]
    channel_id = message["channel"]
    client.chat_postEphemeral(
        channel=channel_id,
        text=f"Hi there, do you need to declare you have reinstalled your operating system, <@{message['user']}>?",
        user=target_user,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Hi there, <@{message['user']}>. Do you need to declare that you've reinstalled your OS?"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "I reinstalled"},
                        "action_id": "reinstall"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "No, I'm good"},
                        "action_id": "Nevermind"
                    }
                ]
            }
        ]
    )



## this one works
'''@app.message("wake me up")
def say_hello(client, message):
    if message["channel"] == kaeley_test:
       print("in correct channel")
    target_user = message["user"]
    channel_id = message["channel"]
    client.chat_postEphemeral(
        channel=channel_id,
        text=f"Summer has come and passed <@{message['user']}>",
        user=target_user,
        blocks= {
        "type": "button",
        "text": {"type": "plain_text",
                 "text": "Nevermind"},
            "action_id": "Tevermind",
        }
    )
'''

### does not work
'''@app.command("--testa")
def repeat_text(ack, respond, command):
    ack()
    respond(f"{command['text']}")

## does not work
@app.command("--linux")
def ask_for_info(client, message):
    # Unix Epoch time for September 30, 2020 11:59:59 PM
    target_user = message["user"]
    channel_id = message["channel"]
    client.chat_postEphemeral(
        channel=channel_id,
        text=f"Summer has come and passed <@{message['user']}>",
        user=target_user
    )

# something wrong with this one
@app.message("Tevermind")
def message_hello(message, say):
    # say() sends a message to the channel where the event was triggered
    say(
        blocks=[
            {
                "type": "actions",
                "text": {"type": "mrkdwn", "text": f"Hey there <@{message['user']}>, nothing's happening"},
                "accessory":
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Nevermind"},
                        "action_id": "Tevermind"
                    },
            }
        ],
        text=f"Hey there <@{message['user']}>, nothing's happening?"
    )
'''


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


# Start your app
if __name__ == "__main__":
    SocketModeHandler(app, secrets.test2_slack_app_token).start()




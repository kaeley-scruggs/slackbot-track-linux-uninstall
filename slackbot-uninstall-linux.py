import datetime
import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import secrets
from datetime import date, time, datetime
import zoneinfo
import sqlite3
import requests
kaeley_test = "G01JE299T6V"

# Initializes your app with your bot token and socket mode handler
app = App(token=secrets.slack_bot_token)
# Listens to incoming messages that contain "hello"
# To learn available listener arguments,
# visit https://tools.slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html

# SQL functions:

def last_installed():
    conn = sqlite3.connect("tally_db.db")
    my_cursor = conn.cursor()
    with conn:
        my_cursor.execute("SELECT * FROM Linux_Reinstall ORDER BY last_date ASC")
        return my_cursor.fetchone()

def most_installed():
    def last_install():
        conn = sqlite3.connect("tally_db.db")
        my_cursor = conn.cursor()
        with conn:
            my_cursor.execute("SELECT * FROM Linux_Reinstall ORDER BY count ASC")
            return my_cursor.fetchone()


def add_count_to_existing_entry(table, username):
    conn = sqlite3.connect(table)
    my_cursor = conn.cursor()
    with conn:
        my_cursor.execute("UPDATE " + table + " SET count = count + 1 WHERE username ='" + username + "';")

def create_row_entry(table, username):
    conn = sqlite3.connect("tally_db.db")
    my_cursor = conn.cursor()
    with conn:
        my_cursor.execute(
        f"INSERT INTO " + table + " VALUES ('Test', '" + username + "', '{today}', '{current_time}', 1)")

# Begin Slack commands
# Command to kick off flow
@app.message("--helplinux")
def say_hello(client, message):
    if message["channel"] == kaeley_test:
       pass
       # print("in correct channel")
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
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Clear tables"},
                        "action_id": "clear_tables"
                    }
                ]
            }
        ]
    )


@app.action("reinstall")
def action_button_click(client, body, ack, say):
    linux_reinstall_table = "Linux_Reinstall"
    ack()
    current_user_data = client.users_info(user=body['user']['id'])
    current_user_id = current_user_data['user']['id']
    current_user_formatted = f"<@{current_user_id}>"
    current_user_display = current_user_data['user']['real_name']
    current_datetime = datetime.now()
    today = current_datetime.strftime("%F")
    current_time = current_datetime.time()
    conn = sqlite3.connect("tally_db.db")
    my_cursor = conn.cursor()
    last_install_data = last_installed()
    with conn:
        print(last_install_data)
        print("begin conditions")
        if last_install_data == None:
            create_row_entry(table=linux_reinstall_table, username=current_user_id)
            print("new user")
        else:
            last_install_data = last_installed()
            last_install_username = last_install_data[1]
            last_install_date = last_install_data[2]
            last_install_time = last_install_data[3]
            if last_install_username == current_user_id:
                if last_install_date == today:
                    print("current time:", current_time)
                    print("last time:", last_install_time)
                    say(f"{current_user_formatted} reinstalled their operating system. They have installed their OS already today--the last time was at {last_install_time}")
                    print("new time:", last_install_time)
                    print("same user, same day, ")
                else:
                    say(f"{current_user_formatted} reinstalled their operating system. They were also the last person to reinstall on " + last_install_date)

            elif current_user_formatted != last_install_username:
                say(f"{current_user_formatted} reinstalled their operating system. The last person to reinstall is {last_install_username}")

                print("last user: " + last_install_username)
                print("current_user != last_install_username")
            else:
                pass


@app.action("clear_tables")
def action_button_click(body, ack, say):
    ack()
    print(f"Tables were cleared")
    conn = sqlite3.connect("tally_db.db")
    my_cursor = conn.cursor()
    with conn:
        my_cursor.execute("DELETE FROM Linux_Reinstall")


@app.action("Nevermind")
def action_button_click(body, ack, say):
    ack()
    print(ack())
    say(f"<@{body['user']['id']}> clicked the button in error.")

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

@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


if __name__ == "__main__":
    SocketModeHandler(app, secrets.test2_slack_app_token).start()




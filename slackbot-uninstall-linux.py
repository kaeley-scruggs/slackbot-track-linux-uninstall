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
def _connect():
    return sqlite3.connect(secrets.db_path)

def last_installed(table):
    with _connect() as conn:
        my_cursor = conn.cursor()
        my_cursor.execute("SELECT * FROM " + table + " ORDER BY last_date ASC")
        return my_cursor.fetchone()


def most_installed(table):
    with _connect() as conn:
        my_cursor = conn.cursor()
        my_cursor.execute("SELECT * FROM " + table + " ORDER BY reinstall_count ASC")
        return my_cursor.fetchone()

# use parameterized variable substitution in a sqlite3 query to prevent sql injection attacks
def add_count_to_existing_entry(table, display_name, username, date, time):
    with _connect() as conn:
        my_cursor = conn.cursor()
        my_cursor.execute(
            "UPDATE " + table + " SET last_date = ?, last_time = ?, reinstall_count =  COALESCE(reinstall_count, 0) + 1 WHERE username = ? AND display_name = ?;",
            (date, time, username, display_name))


def create_row_entry(table, display_name, username, date, time,):
    with _connect() as conn:
        my_cursor = conn.cursor()
        my_cursor.execute(
            "INSERT INTO " + table + " VALUES (display_name = ?, username = ?, last_date = ?, last_time = ?, 1)",
            (display_name, username, date, time,))


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
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Clear tables"},
                        "action_id": "print_tables"
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
    today = str(current_datetime.strftime("%F"))
    current_time = str(current_datetime.strftime("%I:%M:%S %p"))
    last_install_data = last_installed(linux_reinstall_table)
    with _connect() as conn:
        my_cursor = conn.cursor()
        print("last install", last_install_data)
        print("begin conditions")
        if last_install_data is None:
            create_row_entry(table=linux_reinstall_table, display_name=current_user_display, username=current_user_id, date=today, time=current_time)
            say(f"{current_user_formatted} reinstalled their operating system.")
            print(f"{current_user_formatted} reinstalled their operating system.")
        else:
            last_install_data = last_installed(linux_reinstall_table)
            last_install_date = last_install_data[1]
            last_install_time = last_install_data[2]
            last_install_username = last_install_data[3]
            if last_install_username == current_user_id:
                if last_install_date == today:
                    # create_row_entry(table, username, date, time)
                    add_count_to_existing_entry(table=linux_reinstall_table, display_name=current_user_display, username=current_user_id, date=today, time=current_time)
                    say(f"{current_user_formatted} reinstalled their operating system. They also were the last person to reinstall--the last time was today at {last_install_time}")
                    print(f"{current_user_formatted} reinstalled their operating system. They also were the last person to reinstall--the last time was today at {last_install_time}")
                else:
                    add_count_to_existing_entry(table=linux_reinstall_table, display_name=current_user_display, username=current_user_id, date=today, time=current_time)
                    say(f"{current_user_formatted} reinstalled their operating system. They were also the last person to reinstall on " + last_install_date)
                    print(f"{current_user_formatted} reinstalled their operating system. They were also the last person to reinstall on " + last_install_date)

            elif current_user_id != last_install_username:
                add_count_to_existing_entry(table=linux_reinstall_table, display_name=current_user_display, username=current_user_id, date=today, time=current_time)
                say(f"{current_user_formatted} reinstalled their operating system. The last person to reinstall is ,@<{last_install_username}>")
                print(f"{current_user_formatted} reinstalled their operating system. The last person to reinstall is @<{last_install_username}>")


@app.action("clear_tables")
def action_button_click(body, ack, say):
    ack()
    print(f"Tables were cleared")
    with _connect() as conn:
        my_cursor = conn.cursor()
        my_cursor.execute("DELETE FROM Linux_Reinstall")

@app.action("print_tables")
def action_button_click(client, body, ack, say):
    ack()
    with _connect() as conn:
        my_cursor = conn.cursor()
        my_cursor.execute("SELECT FROM sqlite_master WHERE type='table'")
        tables = my_cursor.fetchall()
    print("tables in the database")
    for table in tables:
        print(table)

@app.action("Nevermind")
def action_button_click(body, ack, say):
    ack()
    print(ack())
    say(f"<@{body['user']['id']}> clicked the button in error.")


@app.event("message")
def handle_message_events(body, logger):
    logger.info(body)


if __name__ == "__main__":
    SocketModeHandler(app, secrets.test2_slack_app_token).start()




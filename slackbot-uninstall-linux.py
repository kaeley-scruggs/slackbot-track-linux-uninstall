import datetime
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import secrets
from datetime import datetime
import sqlite3

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
        my_cursor.execute("SELECT * FROM " + table + " ORDER BY last_date DESC")
        find = my_cursor.fetchone()
        print("last installed in function", find)
        return find


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
        print("add count to existing row entry", my_cursor.fetchone())


def create_row_entry(table, display_name, username, date, time,):
    with _connect() as conn:
        my_cursor = conn.cursor()
        my_cursor.execute(
            "INSERT INTO " + table + " (display_name, username, last_date, last_time, reinstall_count) "
            "VALUES (?,?,?,?,?)",
            (display_name, username, date, time, 1))
        my_cursor.execute("SELECT * FROM " + table + " ORDER BY id DESC LIMIT 1")
        print("create row entry", my_cursor.fetchone())


def find_row_entry(table, username):
    with _connect() as conn:
        my_cursor = conn.cursor()
        my_cursor.execute("SELECT * FROM " + table + " WHERE username = ? LIMIT 1", (username,))
        find = my_cursor.fetchone()
        print("find row entry function:", find)
        return find


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
                        "text": {"type": "plain_text", "text": "Print tables"},
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
    ######################## active user data ########################
    current_user_data = client.users_info(user=body['user']['id'])
    current_user_id = current_user_data['user']['id']
    current_user_formatted = f"<@{current_user_id}>"
    current_user_display = current_user_data['user']['real_name']
    ######################## active time data ########################
    current_datetime = datetime.now()
    today = str(current_datetime.strftime("%F"))
    current_time = str(current_datetime.strftime("%I:%M:%S %p"))
    ######################## Open DB connection ########################
    last_install_data = last_installed(linux_reinstall_table)
    print("last install data out of function:", last_install_data)
    ######################## last install data ########################
    if last_install_data is not None:
        last_install_username = last_install_data[1]
        last_install_date = last_install_data[2]
        last_install_time = last_install_data[3]
        last_install_count = last_install_data[4]
    print("begin conditions")
    if last_install_data is None: # finds none rows
        print("finds no rows")
        create_row_entry(table=linux_reinstall_table, display_name=current_user_display, username=current_user_id, date=today, time=current_time)
        say(current_user_formatted + " reinstalled their operating system.")
    elif find_row_entry(table=linux_reinstall_table, username=current_user_id) is None: # current user has no entry
        create_row_entry(table=linux_reinstall_table, display_name=current_user_display, username=current_user_id,
                         date=today, time=current_time)
        say(current_user_formatted + " reinstalled their operating system. The last person to reinstall was @" + last_install_username)
    elif current_user_id != last_install_username: # current user does not match last user
        print("current user does not match last user")
        add_count_to_existing_entry(table=linux_reinstall_table, display_name=current_user_display, username=current_user_id, date=today, time=current_time)
        say(current_user_formatted + " reinstalled their operating system. The last person to reinstall was @" + last_install_username)
    elif last_install_username == current_user_id: # current user matches last user
        if last_install_date == today: # current user matches last user if it was the same day
            # create_row_entry(table, username, date, time)
            print("current user matches last user if it was the same day")
            add_count_to_existing_entry(table=linux_reinstall_table, display_name=current_user_display, username=current_user_id, date=today, time=current_time)
            say(current_user_formatted + " reinstalled their operating system." +
                " They were also the last person to reinstall at " + str(last_install_time)
                + ". Total install count: " + str(last_install_count + 1))
        else: # current user matches last user if it wasn't the same day
            print("current user matches last user if it wasn't the same day")
            add_count_to_existing_entry(table=linux_reinstall_table, display_name=current_user_display, username=current_user_id, date=today, time=current_time)
            say(current_user_formatted + " reinstalled their operating system." +
                " They were also the last person to reinstall on " + str(last_install_date)
                + ". Total install count: " + str(last_install_count + 1))


@app.action("clear_tables")
def action_button_click(ack):
    ack()
    print(f"Tables were cleared")
    with _connect() as conn:
        my_cursor = conn.cursor()
        my_cursor.execute("DELETE FROM Linux_Reinstall")

@app.action("print_tables")
def action_button_click(ack):
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




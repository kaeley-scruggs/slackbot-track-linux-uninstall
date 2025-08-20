import sqlite3

conn = sqlite3.connect("tally_db.db")

my_cursor = conn.cursor()

# create the table for Linux
def create_linux_table():
    my_cursor.execute("""CREATE TABLE Linux_Reinstall (
                        display_name text,
                        username text, 
                        last_date text,
                        last_time text,
                        count integer
                        )
        """)

# create the table for 1Password
def create_1pass_table():
    my_cursor.execute("""CREATE TABLE '1Password_Recovery' (
                        display_name text,
                        username text, 
                        last_date text,
                        last_time text,
                        count integer
                        )
        """)
my_cursor.execute("INSERT INTO Linux_Reinstall VALUES ('kaeley', '<@UDSERSAS9D>', '2025-08-05', '08:25:18.922434', 2)")
my_cursor.execute("INSERT INTO Linux_Reinstall VALUES ('test', '<@TEST>', '2025-08-02', '08:25:18.922434', 2)")
my_cursor.execute("INSERT INTO Linux_Reinstall VALUES ('testing', '<@TESTING>', '2025-07-15', '08:25:18.922434', 2)")
conn.commit()
conn.close()
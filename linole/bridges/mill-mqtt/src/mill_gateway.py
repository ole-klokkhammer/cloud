from mill import Mill
from dotenv import load_dotenv
import os


def read_data():
    load_dotenv()
    mill_data_connection = Mill(
        os.getenv('EMAIL'),
        os.getenv('PASSWORD')
    )
    mill_data_connection.sync_connect()
    mill_data_connection.sync_update_heaters()

    for heater in mill_data_connection.heaters.values():
        print(heater)

    mill_data_connection.sync_close_connection()


if __name__ == "__main__":
    read_data()

import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# import pandas as pd

# gp = gspread.service_account(filename='services/test.json')
gp = gspread.service_account(filename='services/svetoch.json')
#Open Google spreadsheet
gsheet = gp.open('svetoch')


#Select worksheet
list_record_sheet = gsheet.worksheet("list_record")


# добавить значения
def append_client(id_telegram, user_name, name, phone, info):
    list_record_sheet.append_row([id_telegram, user_name, name, phone, info])


if __name__ == '__main__':
    append_client(id_telegram=000, user_name='user_name', name='name', phone=1111)


# HappyClickService
安裝方式： pip install -r requirement.txt
# Database Architecture

## UserData
    ID = 工號 (integer)
    Name = 名字 (string)
    password = 密碼 (integer)
    identity = 身分類別 (staff, employee, med) (string)
    division = 廠區 (string)
    department = 部門 (string)
    email = 信箱 (string)
## FormData
    form_id = 表單id (integer)
    user_id = 工號 (integer)
    username = 預約的使用者 (string)
    vaccine_type = 預約的疫苗類別 (string)
    vaccine_date = 預約的接種日期 (date 年月日, ex. 2021/08/02)
## VaccineData
    vaccine_id = 疫苗id (integer)
    date = 日期 (date 年月日, ex. 2021/08/02)
    vaccine_type = 疫苗類別 (string)
    vaccine_amount = 疫苗存量 (integer)
## VaccinatedData
    vaccinated_id = 接種人工號 (integer)   
    vaccinated_name = 接種者名字 (string)
    vaccine_type = 接種疫苗類別 (string)
    vaccine_date = 接種疫苗日期 (date 年月日, ex. 2021/08/02)

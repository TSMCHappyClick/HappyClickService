
# HappyClickService
安裝方式： pip install -r requirement.txt
# Database Architecture

## UserData
    ID = 工號 (integer)
    Name = 名字 (string)
    password = 密碼 (hash)
    identity = 身分類別 (staff, employee, med) (string)
    division = 廠區 (string)
    email = 信箱 (string)
## FormData
    form_id = 表單id (integer)
    ID = 工號 (integer)
    Name = 預約的使用者 (string)
    vaccine_type = 預約的疫苗類別 (string)
    date = 預約的接種日期 (string, ex. 2021/08/02)
    status = 是否接種(boolean, 預設false)
## VaccineData
    vaccine_id = 疫苗id (integer)
    date = 日期 (string, ex. 2021/08/02)
    vaccine_type = 疫苗類別 (string)
    vaccine_amount = 疫苗存量 (integer)
    reserve_amount = 預約數量 (integer)
## VaccinatedData
    ID = 接種人工號 (integer)   
    Name = 接種者名字 (string)
    vaccinated_times = 接種疫苗次數 (int)
## StaffData
    ID = 主管工號 (integer)   
    employees = 下屬們的工號 [xxx,xxx,....,xxx]（integer）
    division = 主管所屬廠區（string）

# Reserve API

### 新增預約 (SaveReserve) : ./Reserve  (POST)
- Input : 
    - ID (integer)
    - Name (string)
    - date (string)
    - vaccine_type (string)
- Output : 
	- 可預約 --> 
	    - msg (string)
	- 不能預約 --> 
    	- msg (string)


### 查詢紀錄 (CheckReserve) : ./Check  (POST)
- Input : 
    - ID (integer)
- Output : 
	- 有查到 --> 
    	- msg (string)
    	- vaccine_type (string)
    	- date (string)
	- 沒查到 --> 
	    - msg (string)

### 刪除預約 (RemoveReserve) : ./Remove  (POST)
- Input : 
    - ID (integer)
    - date (string)
    - vaccine_type (string)
- Output : 
	- 有查到 --> 
	    - msg (string)
	- 沒查到 -->
	    - msg (string)

### 回傳可預約時段 (ReturnAvailable) : ./ReturnAvailable  (GET)
- Call : 
	- 可預約 --> 
	    - List of {
	   	 - date (string), 
	  	 - vaccine_type (string), 
	   	 - vaccine_remaining (integer)
	    - }
	- 不可約 --> 
	    - 不列入


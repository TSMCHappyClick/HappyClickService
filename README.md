
# HappyClickService
安裝方式： pip install -r requirement.txt
server on heroku
- url : https://happyclick-healthcenter.herokuapp.com/{api_url}
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

# 登入＆登出 API
### Login (POST)
- Input : {'ID':int, 'password':string}
- Output : 
    - 登入成功：
      - 是醫護人員：{'identity':'med'}
      - 不是醫護人員：{'identity':'employee'}
    - 登入失敗：{'identity':'Wrong id or password!'}
### logout (GET)
- Input : 無
- Output : 
    - {'msg':'Logged out successfully!'}


# 疫苗使用率狀況 API. (dashboard頁面直接顯示出以下三個）
### 廠區施打率
- Input : 無
- Output : 
## 主管底下員工的施打狀況 find_employees_under_staff (GET)
- Input : 無
- Output : 
    - {'shot': [XXX,...,XXX], 'not_shot': [XXX,XXX,XXX,...,XXX]}
### 各種疫苗的施打率
- Input : 無
- Output : 

# Health center API
### SearchFormData 查詢預約接種名單 (POST)
- Input : 
    - date (string, ex. {"date":"2021/08/12"})
- Output : 
    - 有資料 
        - list[{form_id(integer), vaccine_type(string), ID(integer), Name(string)}, .....]
    - 沒資料 
        - {'msg' : 'No FormData data!'}
### UpdateVaccinated 上傳接種資料 (POST)
- Input : 
    - {form_id(integer), ID(integer), Name(string)}
- Output : 
    - {'msg' : 'Update Vaccinated successful!'}


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


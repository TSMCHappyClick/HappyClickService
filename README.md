# HappyClickService
安裝方式： pip install -r requirement.txt

# Reserve API

### 新增預約 (SaveReserve) : ./Reserve
- Input : ID(int), Name(str), date(str), vaccine_type(str)
- Output : 可預約 --> msg(str)
	   不能預約 --> msg(str)


### 查詢紀錄 (CheckReserve) : ./Check
- Input : ID(int)
- Output : 有查到 --> msg(str), vaccine_type(str), date(str)
	   沒查到 --> msg(str)

### 刪除預約 (RemoveReserve) : ./Remove
- Input : ID(int), date(str), vaccine_type(str)
- Output : 有查到 --> msg(str)
	   沒查到 --> msg(str)

### 回傳可預約時段 (ReturnAvailable) : ./ReturnAvailable
- Call : 可預約 --> List of {date(str), vaccine_type(str), vaccine_remaining(int)}
	 不可約 --> 不列入


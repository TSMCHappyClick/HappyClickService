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
## 廠區施打率
- Input : 無
- Output : 
## 主管底下員工的施打狀況 find_employees_under_staff (GET)
- Input : 無
- Output : 
    - {'shot': [XXX,...,XXX], 'not_shot': [XXX,XXX,XXX,...,XXX]}
## 各種疫苗的施打率
- Input : 無
- Output : 


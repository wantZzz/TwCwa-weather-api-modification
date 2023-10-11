# TwCwa-weather-api-modification
在原先台灣氣象署 F-C0032-001 API 基礎上增加圖片與資料整理功能

提供目前開放資料之擷取API
資料來源: [中央氣象局開放資料平臺之資料擷取API](https://opendata.cwb.gov.tw/dist/opendata-swagger.html)

資料更新頻率觀察為一天四次，分別在上午/下午6、12點更新，首頁網址: <https://weatherapiv2.10935179.repl.co>
若連上首頁網址且顯示 `API site is aLive!` 即代表 API 正常運作，驗證網站在線請用首頁網址以節省主機資源
當前API版本 : v1.0.2

## 最近變更與更新

> 08/18 解決 [[GET] /today_file](#GET-today_file) 與 [[GET] /today_file_auto](#GET-today_file_auto) 在更新中央氣象局開放資料時會有一段沒有資料的空窗期(v1.0.2)

> 08/07 API 開放使用(v1.0.1)

## 如何利用 Github 裡的開源文件 
> 備註: 由於本人在架設本服務時有特殊條件，故將主對外服務與製圖端: `MainExternalServer_api`、`PictureMaker_api`兩個子服務分別掛載不同的伺服器，若您需將兩個子服務掛在同一伺服器或機器時請自行整合(API 都是用 flask 寫的)

- `MainExternalServer_api` 這資料夾內是主對外服務的 API 程式，負責與外部使用者處理、發配資料
  - 主 API 程式碼為 `main.py`
  - 請記得去申請 氣象署資料開放平臺 的 API key 並自行填入 `main.py` 的第16行的變數裡
  - 標尺的圖片檔為 `color_bar_1.png`, `color_bar_2.png`
  - 降雨量圖與相關文件、天氣溫度圖與相關文件、合成圖的資料夾分別為 `pop_plots`, `pop_files`, `v2_plots`, `v2_files`, `map_plots`
  - 當各資料夾裡圖片與相關文件太多時可執行程式碼 `files_cleaner.py` ，會移除各資料夾內建立時間在最近15天外的檔案刪除

- `PictureMaker_api` 這資料夾內是製圖端的 API 程式，接受主對外服務的資料並返回處理好的圖片資料(不負責合成圖片)
  - 主 API 程式碼檔為 `PictureMaker_flask.py`
  - 製圖的程式碼檔為 `python_html2img.py`
  - 降雨量圖、天氣溫度圖的製圖的範本的html檔為 `tw_map_v1.html`, `tw_map_v2.html`

## \[GET] /today_file_auto
> 取得今日預處理好天氣資訊

對文字資料已經做好預處理的API，讀取圖片請參考 - [[GET] /map_plots/<aggregation_map_data>](#GET-map_plotsltaggregation_map_datagt)

##### 資料輸入值
- 無輸入值或參數

##### 資料結構
`https://weatherapiv2.10935179.repl.co/today_file_auto`

```json
{"PoP_map_data":["pop_plots/2023-07-31_07_0.png"...],
 "Tem_weather_map_data":["v2_plots/2023-07-31_07_0.png"...],
 "aggregation_map_data":["map_plots/2023-07-31_07_0.png"...],
 "str_from_of_data":{"2023-07-31 06:00:00":{"start_time":"2023-07-31 06:00:00",
                                            "end_time":"2023-07-31 18:00:00",
                                            "time_range":"07月31日 06點 - 07月31日 18點",
                                            "str_from_of_Tmp":"嘉義縣 - 33-26°C...",
                                            "str_from_of_Wx":"嘉義縣 - 多雲短暫陣雨...",
                                            "str_from_of_pop":"嘉義縣 - 30%..."
                                           },...
                    }
}
```
##### 資料說明

| 資料名稱 key   | 類型 type    | 長度 length  | 簡介                            |
| ------------ | ------------ | -------- | ------------------------------ |
| PoP_map_data | list\<str>    | 3        | 繪製好的各縣市降雨率地圖API連結與其對應參數(無標尺) |
| Tem_weather_map_data | list\<str>    | 3        | 繪製好的各縣市平均溫度、最高/最低溫、天氣概況<br>地圖連結與其對應參數(無標尺) |
| aggregation_map_data | list\<str>    | 3        | 將以上繪製好的地圖附上標尺的圖片連結與其對應參數 |
| str_from_of_data | dict\<dict>    | 3        | 將文字資料已經做好預處理並以`start_time`作為key分類 |
| start_time | str    | -        | 該資料開頭時間 |
| end_time   | str    | -        | 該資料結尾時間 |
| time_range | str    | -        | 該資料所涵蓋時間區間 |
| str_from_of_Tmp | str    | -        | 預處理完的各縣市最高/最低溫文字資訊<br>格式為: `縣市名` - `最高-最低`°C\n|
| str_from_of_Wx | str    | -        | 預處理完的各縣市天氣概況文字資訊<br>格式為: `縣市名` - `天氣概況`\n|
| str_from_of_Tmp | str    | -        | 預處理完的各縣市降雨率文字資訊<br>格式為: `縣市名` - `降雨率`%\n|
    
備註: `PoP_map_data`, `Tem_weather_map_data`, `aggregation_map_data`, `str_from_of_data`的同一位置資料是互相對應的
    
---
    
## \[GET] /today_file
> 取得今日天氣資訊

取得今日天氣資訊的API，讀取圖片請參考 - [[GET] /map_plots/<aggregation_map_data>](#GET-map_plotsltaggregation_map_datagt) 

##### 資料輸入值
- 無輸入值或參數

##### 資料結構
`https://weatherapiv2.10935179.repl.co/today_file`
    
```json
{"PoP_map_data":["pop_plots/2023-07-31_07_0.png"...],
 "Tem_weather_map_data":["v2_plots/2023-07-31_07_0.png"...],
 "aggregation_map_data":["map_plots/2023-07-31_07_0.png"...],
 "list_from_of_data":{"2023-07-31 06:00:00":{"start_time":"2023-07-31 06:00:00",
                                             "end_time":"2023-07-31 18:00:00",
                                             "time_range":"07月31日 06點 - 07月31日 18點",
                                             "location_name":["嘉義縣"...],
                                             "Tmp":["33-26°C"...],
                                             "Wx":["多雲短暫陣雨"...],
                                             "pop":["30%"...]},...
                    }
}
```
##### 資料說明

| 資料名稱 key   | 類型 type    | 長度 length  | 簡介                            |
| ------------ | ------------ | -------- | ------------------------------ |
| PoP_map_data | list\<str>    | 3        | 繪製好的各縣市降雨率地圖API連結與其對應參數(無標尺) |
| Tem_weather_map_data | list\<str>    | 3        | 繪製好的各縣市平均溫度、最高/最低溫、天氣概況<br>地圖連結與其對應參數(無標尺) |
| aggregation_map_data | list\<str>    | 3        | 將以上繪製好的地圖附上標尺的圖片連結與其對應參數 |
| list_from_of_data | dict\<dict>    | 3        | 各縣市的名稱資訊並以`start_time`作為key分類 |
| start_time | str    | -        | 該資料開頭時間 |
| end_time   | str    | -        | 該資料結尾時間 |
| time_range | str    | -        | 該資料所涵蓋時間區間 |
| location_name | list\<str>    | 22        | 各縣市名稱資訊<br>格式為: `縣市名`|
| Tmp           | list\<str>    | 22        | 各縣市降雨率資訊<br>格式為: `最高-最低`°C|
| Wx            | list\<str>    | 22        | 各縣市天氣概況資訊<br>格式為: `天氣概況`|
| pop           | list\<str>    | 22        | 各縣市降雨率資訊<br>格式為: `降雨率`%|
    
備註: `PoP_map_data`, `Tem_weather_map_data`, `aggregation_map_data`, `list_from_of_data`的同一位置資料是互相對應的
    `location_name`, `Tmp`, `Wx`, `pop`的同一位置資料是互相對應的

---
    
## \[GET] /pop_plots/<PoP_map_data>
> 取得今日降雨量圖片資料

取得今日降雨量圖片資料
##### 資料輸入值
PoP_map_data: 請先取得 [[GET] /today_file](#GET-today_file) 與 [[GET] /today_file_auto](#GET-today_file_auto) 的資料，其中的`PoP_map_data`的連結與此處參數是相對應的

##### 範例資料
`https://weatherapiv2.10935179.repl.co/pop_plots/2023-10-07_08_0.png`
    
![pop_plots範例](https://weatherapiv2.10935179.repl.co/pop_plots/2023-10-07_08_0.png)
    
---
    
## \[GET] /v2_plots/<Tem_weather_map_data>
> 取得今日平均溫度、最高/最低溫、天氣概況圖片資料

取得今日平均溫度、最高/最低溫、天氣概況圖片資料
##### 資料輸入值
Tem_weather_map_data: 請先取得 [[GET] /today_file](#GET-today_file) 與 [[GET] /today_file_auto](#GET-today_file_auto) 的資料，其中的`Tem_weather_map_data`的連結與此處參數是相對應的

##### 範例資料
`https://weatherapiv2.10935179.repl.co/v2_plots/2023-10-07_08_0.png`
    
![v2_plots範例](https://weatherapiv2.10935179.repl.co/v2_plots/2023-10-07_08_0.png)
    
---
    
## \[GET] /map_plots/<aggregation_map_data>
> 取得今日`/v2_plots`與`/pop_plots`的組合圖片資料

取得今日`/v2_plots`與`/pop_plots`的組合圖片資料
##### 資料輸入值
aggregation_map_data: 請先取得 [[GET] /today_file](#GET-today_file) 與 [[GET] /today_file_auto](#GET-today_file_auto) 的資料，其中的`aggregation_map_data`的連結與此處參數是相對應的

##### 範例資料
`https://weatherapiv2.10935179.repl.co/map_plots/2023-10-07_08_0.png`
    
![map_plots範例](https://weatherapiv2.10935179.repl.co/map_plots/2023-10-07_08_0.png)

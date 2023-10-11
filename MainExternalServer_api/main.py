import os, sys
import json
import requests
import time
import asyncio
from datetime import datetime, timedelta

from colour import Color

from PIL import Image

from flask import Flask, abort, send_from_directory, request
from threading import Thread
import traceback

api_key = "在這填入 API_KEY"

PoP = {}
Tmp = {}
Wx = {}
Wx_str = {}

time_interval = []
is_crossline = True

PoPdata_path = ""
v2data_path = ""
mapdata_path = ""
data_time_interval = []

html2img_getv1_api_url = "http://wannazzz.pythonanywhere.com/pop_img"
html2img_getv2_api_url = "http://wannazzz.pythonanywhere.com/v2_img"

data_isdone = False

location_id = {'宜蘭縣': '001', '桃園市': '005', '新竹縣': '009', '苗栗縣': '013', '彰化縣': '017',
               '南投縣': '021', '雲林縣': '025', '嘉義縣': '029', '屏東縣': '033', '臺東縣': '037',
               '花蓮縣': '041', '澎湖縣': '045', '基隆市': '049', '新竹市': '053', '嘉義市': '057',
               '臺北市': '061', '高雄市': '065', '新北市': '069', '臺中市': '073', '臺南市': '077',
               '連江縣': '081', '金門縣': '085'}

data_list = {'連江縣': 'C09007', '金門縣': 'C09020', '澎湖縣': 'C10016', '宜蘭縣': 'C10002', '臺東縣': 'C10014', '台東縣': 'C10014', '屏東縣': 'C10013', '高雄市': 'C64', '臺南市': 'C67', '台南市': 'C67', '嘉義市': 'C10020', '嘉義縣': 'C10010', '雲林縣': 'C10009', '彰化縣': 'C10007', '花蓮縣': 'C10015', '南投縣': 'C10008', '臺中市': 'C66', '台中市': 'C66', '苗栗縣': 'C10005', '新竹市': 'C10004', '新竹縣': 'C10018', '桃園市': 'C68', '臺北市': 'C63', '台北市': 'C63', '新北市': 'C65', '基隆市': 'C10017'}

def except_info(e):
  error_class = e.__class__.__name__ #取得錯誤類型
  detail = e.args[0] #取得詳細內容
  cl, exc, tb = sys.exc_info() #取得Call Stack
  lastCallStack = traceback.extract_tb(tb)[-1] #取得Call Stack的最後一筆資料
  fileName = lastCallStack[0] #取得發生的檔案名稱
  lineNum = lastCallStack[1] #取得發生的行號
  funcName = lastCallStack[2] #取得發生的函數名稱
  errMsg = "File \"{}\", line {}, in {}: [{}] {}".format(fileName, lineNum, funcName, error_class, detail)
  return errMsg

def load_newest_api_data():
  global PoP, Tmp, Wx, Wx_str, time_interval, is_crossline, data_list, api_key

  today_weather_api_url = f"https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={api_key}"
  
  today_weather_api = requests.get(today_weather_api_url)
  
  if today_weather_api.status_code == requests.codes.ok:
    api_get_time = (datetime.now() + timedelta(hours=8)).hour
    
    if 3 <= api_get_time and api_get_time < 15:
      is_crossline = True
    else:
      is_crossline = False

    today_weather = today_weather_api.json()['records']['location']
    
    time_example = today_weather[0]['weatherElement'][0]['time']

    time_interval = []
    time_interval.append(time_example[0]['startTime'])
    for example in time_example:
      time_interval.append(example['endTime'])

    print(time_interval)

    PoP = {time_interval[0]: {}, time_interval[1]: {}, time_interval[2]: {}}
    Tmp = {time_interval[0]: {}, time_interval[1]: {}, time_interval[2]: {}}
    Wx = {time_interval[0]: {}, time_interval[1]: {}, time_interval[2]: {}}
    Wx_str = {time_interval[0]: {}, time_interval[1]: {}, time_interval[2]: {}}
      
    for location_data in today_weather:
      for element_data in location_data["weatherElement"]:
        if element_data["elementName"] == "PoP":
          for i in range(3):
            PoP[time_interval[i]][location_data["locationName"]] = int(element_data["time"][i]["parameter"]["parameterName"])
            
        elif element_data["elementName"] == "MinT":
          try:
            for i in range(3):
              Tmp[time_interval[i]][location_data["locationName"]][0] = int(element_data["time"][0]["parameter"]["parameterName"])
          except:
            for i in range(3):
              Tmp[time_interval[i]][location_data["locationName"]] = [0,0]
              Tmp[time_interval[i]][location_data["locationName"]][0] = int(element_data["time"][i]["parameter"]["parameterName"])
              
        elif element_data["elementName"] == "MaxT":
          try:
            for i in range(3):
              Tmp[time_interval[i]][location_data["locationName"]][1] = int(element_data["time"][i]["parameter"]["parameterName"])
          except:
            for i in range(3):
              Tmp[time_interval[i]][location_data["locationName"]] = [0,0]
              Tmp[time_interval[i]][location_data["locationName"]][1] = int(element_data["time"][i]["parameter"]["parameterName"])
              
        elif element_data["elementName"] == "Wx":
          for i in range(3):
            Wx[time_interval[i]][location_data["locationName"]] = int(element_data["time"][i]["parameter"]["parameterValue"])
            Wx_str[time_interval[i]][location_data["locationName"]] = element_data["time"][i]["parameter"]["parameterName"]
          
    return True
    
  else:
    print("error!", today_weather_api.status_code)
    return False
    
def run_PoPdata(now_datetime):
  global PoP, Tmp, Wx, Wx_str, time_interval, PoPdata_path, html2img_getv1_api_url, data_list
  
  pop_colors = ["#97cbff", "#84c1ff", "#66b3ff", "#46a3ff", "#2894ff", "#0080ff", "#0072e3", "#0066cc", "#005ab5", "#004b97"]
  
  pop_translate = {time_interval[0]: {}, time_interval[1]: {}, time_interval[2]: {}}

  def pop_color(pop_leval):
    if pop_leval > 9:
      return 9
    elif pop_leval < 0:
      return 0
    else:
      return pop_leval
  
  for i in range(3):
    for pop_value in PoP[time_interval[i]].keys():
      pop_translate[time_interval[i]][data_list[pop_value]] = pop_colors[pop_color(PoP[time_interval[i]][pop_value] // 10)]

  #now_datetime = datetime.now() + timedelta(hours=8)
  for i in range(3):
    html2img_api = requests.get(html2img_getv1_api_url,json = pop_translate[time_interval[i]])
    
    if html2img_api.status_code == requests.codes.ok:
      with open(f'pop_plots/{now_datetime.strftime("%Y-%m-%d_%H")}_{i}.png','wb') as f:
        f.write(html2img_api.content)
        
    else:
      with open('error.png','r') as f:
        error_img = f.read()
      with open(f'pop_plots/{now_datetime.strftime("%Y-%m-%d_%H")}_{i}.png','w') as f:
        f.write(error_img)
    
  PoPdata_path = f'{now_datetime.strftime("%Y-%m-%d_%H")}'
  
  with open(f'pop_files/{now_datetime.strftime("%Y-%m-%d_%H")}.json','w') as f:
    f.write(json.dumps(PoP))
        
def run_Tmp_Wx_data(now_datetime):
  global PoP, Tmp, Wx, Wx_str, time_interval, is_crossline, v2data_path, html2img_getv2_api_url, data_list
  
  tmp_colors = ['#127287', '#1e7b94', '#2f8b9d', '#3a92a6', '#4e9fb1', '#5facbf', '#68b5c4', '#78c0ce', '#88cbd8', '#98d5e2', '#74e0ec', '#b8e9f9', '#0c9248', '#1c9b53', '#31a056', '#42a95f', '#53b262', '#61b869', '#76c270', '#85c973', '#96d07c', '#a6d982', '#b8df86', '#cce68e', '#d8f193', '#f2f4c3', '#f8e787', '#f2d673', '#f3c362', '#efb14e', '#eb9a37', '#e68d2d', '#db7b06', '#ed5031', '#ed1257', '#a90438', '#76050b', '#9b69ab', '#874f96', '#7e239f']
  
  if is_crossline:
    v2_translate = {time_interval[0]: {'time': 'day'}, time_interval[1]: {'time': 'night'}, time_interval[2]: {'time': 'day'}}
    v2_translate_original = {time_interval[0]: {'time': 'day'}, time_interval[1]: {'time': 'night'}, time_interval[2]: {'time': 'day'}}
  else:
    v2_translate = {time_interval[0]: {'time': 'night'}, time_interval[1]: {'time': 'day'}, time_interval[2]: {'time': 'night'}}
    v2_translate_original = {time_interval[0]: {'time': 'night'}, time_interval[1]: {'time': 'day'}, time_interval[2]: {'time': 'night'}}

  def tmp_color(tmp):
    if tmp < -1:
      return -1
    elif tmp > (len(tmp_colors) - 2):
      return len(tmp_colors) - 1
    else:
      return tmp
  
  for i in range(3):
    for tmp_value in Tmp[time_interval[i]].keys():
      avg_tmp = round(sum(Tmp[time_interval[i]][tmp_value]) / 2)
      v2_translate[time_interval[i]][data_list[tmp_value]] = [0,"",""]
      v2_translate_original[time_interval[i]][tmp_value] = [0,"",""]
      
      v2_translate[time_interval[i]][data_list[tmp_value]][0] = tmp_colors[avg_tmp + 1]
      v2_translate_original[time_interval[i]][tmp_value][0] = tmp_colors[avg_tmp + 1]
      
      v2_translate[time_interval[i]][data_list[tmp_value]][1] = f"{Tmp[time_interval[i]][tmp_value][1]}-{Tmp[time_interval[i]][tmp_value][0]}"
      v2_translate_original[time_interval[i]][tmp_value][1] = f"{Tmp[time_interval[i]][tmp_value][1]}-{Tmp[time_interval[i]][tmp_value][0]}"
      
      v2_translate[time_interval[i]][data_list[tmp_value]][2] = str(Wx[time_interval[i]][tmp_value]).zfill(2)
      v2_translate_original[time_interval[i]][tmp_value][2] = Wx_str[time_interval[i]][tmp_value]

  #now_datetime = datetime.now() + timedelta(hours=8)
  for i in range(3):
    html2img_api = requests.get(html2img_getv2_api_url,json = v2_translate[time_interval[i]])
    
    if html2img_api.status_code == requests.codes.ok:
      
      with open(f'v2_plots/{now_datetime.strftime("%Y-%m-%d_%H")}_{i}.png','wb') as f:
        f.write(html2img_api.content)
    else:
      with open('error.png','r') as f:
        error_img = f.read()
      with open(f'v2_plots/{now_datetime.strftime("%Y-%m-%d_%H")}_{i}.png','w') as f:
        f.write(error_img)
  
  v2data_path = f'{now_datetime.strftime("%Y-%m-%d_%H")}'
  
  with open(f'v2_files/{now_datetime.strftime("%Y-%m-%d_%H")}.json','w') as f:
    f.write(json.dumps(v2_translate_original))  

# --- main loop ---  
async def clock():
  global PoPdata_path, v2data_path, mapdata_path, time_interval, data_time_interval, data_isdone
  
  now_datetime = datetime.now() + timedelta(hours=8)
  last_datetime = datetime.now() + timedelta(hours=8)

  time.sleep(5)
  
  print("load newest api data......")
  if not load_newest_api_data():
    quit()
  else:
    print("done!")

  print("run newest data image......")
  try:
    run_PoPdata(now_datetime)
    run_Tmp_Wx_data(now_datetime)
    
    for i in range(3):
      bg = Image.new('RGB',((457 + 30)*2 + 60, 616 + 60 + 10), '#ffffff')
      
      pop_img = Image.open(f'pop_plots/{PoPdata_path}_{i}.png')
      bg.paste(pop_img,(0,50))
      
      v2_img = Image.open(f'v2_plots/{v2data_path}_{i}.png')
      bg.paste(v2_img,((457 + 30 + 30),0))

      bar = Image.open('color_bar_1.png')
      bg.paste(bar,(380,420))

      bar = Image.open('color_bar_2.png')
      bg.paste(bar,(944,340))
      
      bg.save(f'map_plots/{now_datetime.strftime("%Y-%m-%d_%H")}_{i}.png')
      data_time_interval = time_interval
    
    mapdata_path = now_datetime.strftime("%Y-%m-%d_%H")
    print("done!")
  except Exception as e:
    print(except_info(e))
    quit()

  data_isdone = True

  print("now clock is runing!")
  while True:
    now_datetime = datetime.now() + timedelta(hours=8)
    
    print(f"now time is {now_datetime.strftime('%Y-%m-%d_%H:%M:%S')} (GMT+8)")
    
    if not now_datetime.strftime('%Y-%m-%d_%H') == last_datetime.strftime('%Y-%m-%d_%H'):
      last_datetime = now_datetime
      load_newest_api_data()
      
      if last_datetime.hour == 6:
        run_PoPdata(now_datetime)
        run_Tmp_Wx_data(now_datetime)
        
        for i in range(3):
          bg = Image.new('RGB',((457 + 30)*2 + 60, 616 + 60 + 10), '#ffffff')
      
          pop_img = Image.open(f'pop_plots/{PoPdata_path}_{i}.png')
          bg.paste(pop_img,(0,50))
          
          v2_img = Image.open(f'v2_plots/{v2data_path}_{i}.png')
          bg.paste(v2_img,((457 + 30 + 30),0))

          bar = Image.open('color_bar_1.png')
          bg.paste(bar,(380,420))

          bar = Image.open('color_bar_2.png')
          bg.paste(bar,(944,340))
          
          bg.save(f'map_plots/{now_datetime.strftime("%Y-%m-%d_%H")}_{i}.png')
          data_time_interval = time_interval
        
        mapdata_path = now_datetime.strftime("%Y-%m-%d_%H")
        
      time.sleep(1999)
    else:
      time.sleep(601)
  
# --- flask loop ---  
app = Flask('')

def abort_msg(e):
  """500 bad request for exception

  Returns:
      500 and msg which caused problems
  """
  
  error_class = e.__class__.__name__ # 引發錯誤的 class
  detail = e.args[0] # 得到詳細的訊息
  cl, exc, tb = sys.exc_info() # 得到錯誤的完整資訊 Call Stack
  lastCallStack = traceback.extract_tb(tb)[-1] # 取得最後一行的錯誤訊息
  fileName = lastCallStack[0] # 錯誤的檔案位置名稱
  lineNum = lastCallStack[1] # 錯誤行數 
  funcName = lastCallStack[2] # function 名稱
  # generate the error message
  errMsg = "Exception raise in file: {}, line {}, in {}: [{}] {}. Please contact the member who is the person in charge of project!".format(fileName, lineNum, funcName, error_class, detail)
  # return 500 code
  abort(500, errMsg)
    
@app.route("/")
def main_page():
  return "API site is aLive!"

@app.route('/reload_today_weather')
def reload_today_weather():
  global mapdata_path, PoPdata_path, v2data_path, time_interval, data_time_interval
  try: 
    now_datetime = datetime.now() + timedelta(hours=8)
    load_newest_api_data()
    
    run_PoPdata(now_datetime)
    run_Tmp_Wx_data(now_datetime)

    for i in range(3):
      bg = Image.new('RGB',((457 + 30)*2 + 60, 616 + 60 + 10), '#ffffff')
      
      pop_img = Image.open(f'pop_plots/{PoPdata_path}_{i}.png')
      bg.paste(pop_img,(0,50))
      
      v2_img = Image.open(f'v2_plots/{v2data_path}_{i}.png')
      bg.paste(v2_img,((457 + 30 + 30),0))

      bar = Image.open('color_bar_1.png')
      bg.paste(bar,(380,420))

      bar = Image.open('color_bar_2.png')
      bg.paste(bar,(944,340))
      
      bg.save(f'map_plots/{now_datetime.strftime("%Y-%m-%d_%H")}_{i}.png')
      data_time_interval = time_interval
    
    mapdata_path = now_datetime.strftime("%Y-%m-%d_%H")
  
    return "Success", 200
  except Exception as e:
    abort_msg(e)
    
@app.route('/reload_map/<name>')
def reload_map(name):
  try:
    for i in range(3):
      bg = Image.new('RGB',((457 + 30)*2 + 60, 616 + 60 + 10), '#ffffff')
      
      pop_img = Image.open(f'pop_plots/{name}_{i}.png')
      bg.paste(pop_img,(0,50))
      
      v2_img = Image.open(f'v2_plots/{name}_{i}.png')
      bg.paste(v2_img,((457 + 30 + 30),0))

      bar = Image.open('color_bar_1.png')
      bg.paste(bar,(380,420))

      bar = Image.open('color_bar_2.png')
      bg.paste(bar,(944,340))
      
      bg.save(f'map_plots/{name}_{i}.png')

    return "Success", 200
  except Exception as e:
    abort_msg(e)

@app.route('/today_file_auto')
def today_file_auto_get():
  global PoPdata_path, v2data_path, mapdata_path, data_time_interval, data_isdone

  while not data_isdone:
    time.sleep(1)

  json_data = {'PoP_map_data': [f'pop_plots/{PoPdata_path}_0.png', f'pop_plots/{PoPdata_path}_1.png', f'pop_plots/{PoPdata_path}_2.png'], 'Tem_weather_map_data': [f'v2_plots/{v2data_path}_0.png', f'v2_plots/{v2data_path}_1.png', f'v2_plots/{v2data_path}_2.png'], 'aggregation_map_data': [f'map_plots/{mapdata_path}_0.png', f'map_plots/{mapdata_path}_1.png', f'map_plots/{mapdata_path}_2.png']}

  str_from_of_data = {}

  for i in range(len(data_time_interval)-1):
    start = datetime.strptime(data_time_interval[i], "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(data_time_interval[i+1], "%Y-%m-%d %H:%M:%S")

    str_from_of_data[data_time_interval[i]] = {"start_time": data_time_interval[i], "end_time": data_time_interval[i+1], "time_range": f"{start.strftime('%m月%d日 %H點')} - {end.strftime('%m月%d日 %H點')}"}

  #---
  
  with open(f"pop_files/{PoPdata_path}.json") as f:
    pop_data = json.load(f)

  for key, pop_time_data in pop_data.items():
    str_from_of_pop = ""
    
    for location in pop_time_data.keys():
      str_from_of_pop += location + f' - {pop_time_data[location]}%\n'

    str_from_of_data[key]['str_from_of_pop'] = str_from_of_pop

  #---

  with open(f"v2_files/{v2data_path}.json") as f:
    v2_data = json.load(f)

  for key, pop_time_data in v2_data.items():
    str_from_of_Wx = ""
    str_from_of_Tmp = ""

    del pop_time_data['time']
    
    for location in pop_time_data.keys():
      str_from_of_Tmp += location + f' - {pop_time_data[location][1]}°C\n'
      str_from_of_Wx += location + f' - {pop_time_data[location][2]}\n'

    str_from_of_data[key]['str_from_of_Tmp'] = str_from_of_Tmp
    str_from_of_data[key]['str_from_of_Wx'] = str_from_of_Wx

  json_data['str_from_of_data'] = str_from_of_data

  return json_data

@app.route('/today_file')
def today_file_get():
  global PoPdata_path, v2data_path, mapdata_path, data_time_interval, data_isdone

  while not data_isdone:
    time.sleep(1)

  json_data = {'PoP_map_data': [f'pop_plots/{PoPdata_path}_0.png', f'pop_plots/{PoPdata_path}_1.png', f'pop_plots/{PoPdata_path}_2.png'], 'Tem_weather_map_data': [f'v2_plots/{v2data_path}_0.png', f'v2_plots/{v2data_path}_1.png', f'v2_plots/{v2data_path}_2.png'], 'aggregation_map_data': [f'map_plots/{mapdata_path}_0.png', f'map_plots/{mapdata_path}_1.png', f'map_plots/{mapdata_path}_2.png']}

  list_from_of_data = {}

  for i in range(3):
    start = datetime.strptime(data_time_interval[i], "%Y-%m-%d %H:%M:%S")
    end = datetime.strptime(data_time_interval[i+1], "%Y-%m-%d %H:%M:%S")

    list_from_of_data[data_time_interval[i]] = {"start_time": data_time_interval[i], "end_time": data_time_interval[i+1], "time_range": f"{start.strftime('%m月%d日 %H點')} - {end.strftime('%m月%d日 %H點')}"}

  #---
  
  with open(f"pop_files/{PoPdata_path}.json") as f:
    pop_data = json.load(f)

  for key, pop_time_data in pop_data.items():
    pop_list = []
    location_name_list = []

    for location in pop_time_data.keys():
      pop_list.append(f'{pop_time_data[location]}%')
      location_name_list.append(location)

    list_from_of_data[key]['location_name'] = location_name_list
    list_from_of_data[key]['pop'] = pop_list

  #---

  with open(f"v2_files/{v2data_path}.json") as f:
    v2_data = json.load(f)

  for key, pop_time_data in v2_data.items():
    Wx_list = []
    Tmp_list = []

    del pop_time_data['time']
    
    for location in pop_time_data.keys():
      Tmp_list.append(f'{pop_time_data[location][1]}°C')
      Wx_list.append(f'{pop_time_data[location][2]}')

    list_from_of_data[key]['Tmp'] = Tmp_list
    list_from_of_data[key]['Wx'] = Wx_list

  json_data['list_from_of_data'] = list_from_of_data

  return json_data
  
@app.route('/pop_plots/<name>', methods=['GET'])
def pop_plots_quest(name):
  return send_from_directory('pop_plots', name, as_attachment=True)   
  
@app.route('/pop_files/<name>', methods=['GET'])
def pop_plots_filesquest(name):
  return send_from_directory('pop_files', name, as_attachment=True)
  
@app.route('/v2_plots/<name>', methods=['GET'])
def v2_plots_quest(name):
  return send_from_directory('v2_plots', name, as_attachment=True)   
  
@app.route('/v2_files/<name>', methods=['GET'])
def v2_plots_filesquest(name):
  return send_from_directory('v2_files', name, as_attachment=True)
  
@app.route('/map_plots/<name>', methods=['GET'])
def map_plots_quest(name):
  return send_from_directory('map_plots', name, as_attachment=True)  

"""
@app.route('pop_plots/<name>', methods=['GET'])
def JSON_value():
    if request.is_json:
        data = request.get_json()
        result = json.dumps(data)
    else:
        result = 'Not JSON Data'
    return result
"""

def run():
    app.run(host="0.0.0.0",port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()

# --- async loop ---

keep_alive()

async def main():
    loop = asyncio.get_event_loop()
    task = loop.create_task(clock())
    await task
    loop.stop()

# 執行主函數
asyncio.run(main())
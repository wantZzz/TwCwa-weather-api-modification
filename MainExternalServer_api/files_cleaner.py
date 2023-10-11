import os
from datetime import datetime, timedelta

file_list = ['map_plots', 'pop_files', 'v2_files', 'pop_plots', 'v2_plots']
time_boder = datetime.now() - timedelta(days=15)

for flie in file_list:
  docs = os.listdir(f'/home/runner/weatherapiv2/{flie}')
  count = len(docs)
  inline = 0
  error = 0
  deleted = 0
  pased = 0
  
  for doc in docs:
    if(doc == '2023-10-07_08_0.png'):
      pased += 1
      continue
    elif (datetime.strptime(doc[:10], "%Y-%m-%d") < time_boder):
      try:
        os.remove(f'/home/runner/weatherapiv2/{flie}/{doc}')
        deleted += 1
      except:
        error += 1
    else:
      inline += 1

  print(f'{flie}:\ncount: {count}, inline: {inline}, deleted:{deleted}, error:{error}, pased:{pased}')
from flask import Flask, request, abort, send_file, send_from_directory

import sys, traceback
import io

import pythonanywhere_html2img

app = Flask(__name__)

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

    print(errMsg)

@app.route('/')
def home():
  return 'API is aLive!'

@app.route('/pop_img', methods=['GET'])
def api_v1_fun():
  if request.is_json:
    pop_data = request.get_json()

    quest_respond, e = pythonanywhere_html2img.v1_img(pop_data)

    if quest_respond:
      with open('image_v1.png', 'rb') as f:
        return send_file(io.BytesIO(f.read()),mimetype='image/png')
    else:
       abort_msg(e)

  else:
    return abort(417, "file type error")

@app.route('/v2_img', methods=['GET'])
def api_v2_fun():
  if request.is_json:
    v2_data = request.get_json()

    quest_respond, e = pythonanywhere_html2img.v2_img(v2_data)

    if quest_respond:
      with open('image_v2.png', 'rb') as f:
        return send_file(io.BytesIO(f.read()),mimetype='image/png')
    else:
       abort_msg(e)

  else:
    return abort(417, "file type error")

@app.route('/svg_icon/day/<name>')
def svg_icon_day(name):
  with open(f'./svg_icon/day/{name}', 'rb') as f:
    return send_file(io.BytesIO(f.read()),mimetype='image/svg+xml')

@app.route('/svg_icon/night/<name>')
def svg_icon_night(name):
  with open(f'./svg_icon/night/{name}', 'rb') as f:
    return send_file(io.BytesIO(f.read()),mimetype='image/svg+xml')

@app.route('/style_v1.css')
def style_v1_css(name):
  with open('./style_v1.css', 'rb') as f:
    return send_file(io.BytesIO(f.read()),mimetype='text/css')

@app.route('/style_v2.css')
def style_v2_css(name):
  with open('./style_v2.css', 'rb') as f:
    return send_file(io.BytesIO(f.read()),mimetype='text/css')

if __name__ == '__main__':
  app.run("0.0.0.0", port=8080)
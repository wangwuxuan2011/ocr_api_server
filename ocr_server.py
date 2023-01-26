# encoding=utf-8
import argparse
import base64
import datetime
import json

import ddddocr
from flask import Flask, request, render_template

parser = argparse.ArgumentParser(description="使用ddddocr搭建的最简api服务")
parser.add_argument("-p", "--port", type=int, default=9000)
parser.add_argument("--ocr", action="store_true", help="开启ocr识别")
parser.add_argument("--old", action="store_true", help="OCR是否启动旧模型")
parser.add_argument("--det", action="store_true", help="开启目标检测")

args = parser.parse_args()

app = Flask(__name__)


class Server(object):
    def __init__(self, ocr=True, det=False, old=False):
        self.ocr_option = ocr
        self.det_option = det
        self.old_option = old
        self.ocr = None
        self.det = None
        if self.ocr_option:
            print("ocr模块开启")
            if self.old_option:
                print("使用OCR旧模型启动")
                self.ocr = ddddocr.DdddOcr(old=True)
            else:
                print("使用OCR新模型启动，如需要使用旧模型，请额外添加参数  --old开启")
                self.ocr = ddddocr.DdddOcr()
        else:
            print("ocr模块未开启，如需要使用，请使用参数  --ocr开启")
        if self.det_option:
            print("目标检测模块开启")
            self.det = ddddocr.DdddOcr(det=True)
        else:
            print("目标检测模块未开启，如需要使用，请使用参数  --det开启")

    def classification(self, img: bytes):
        if self.ocr_option:
            return self.ocr.classification(img)
        else:
            raise Exception("ocr模块未开启")

    def detection(self, img: bytes):
        if self.det_option:
            return self.det.detection(img)
        else:
            raise Exception("目标检测模块模块未开启")

    def slide(self, target_img: bytes, bg_img: bytes, algo_type: str):
        dddd = self.ocr or self.det or ddddocr.DdddOcr(ocr=False)
        if algo_type == 'match':
            return dddd.slide_match(target_img, bg_img)
        elif algo_type == 'compare':
            return dddd.slide_comparison(target_img, bg_img)
        else:
            raise Exception(f"不支持的滑块算法类型: {algo_type}")


server = Server(ocr=args.ocr, det=args.det, old=args.old)


def get_img(request, img_type='base64', key='image'):
    if img_type == 'base64':
        try:
            img = base64.b64decode(get_kv(request, key=key).encode())
        except Exception:
            raise Exception("解码失败")
    else:
        img = get_kv(request, type="file").read()
    return img


# 获取request中的json键值对，支持POST和GET,支持不同Content-Type
def get_kv(request, type="text", key="image", default=None):
    if type == "file":
        return request.files.get(key, default)
    elif type == "text":
        if request.method == "POST":
            if request.content_type == "application/json":
                try:
                    return request.get_json().get(key, default)
                except Exception:
                    return default
            elif request.content_type == "text/plain":
                if key == "image":
                    return request.get_data().decode()  # 纯文本直接输出所有文本
                return default
            else:
                return request.form.get(key, default)
        else:
            return request.args.get(key, default)
    return default


def set_ret(result, return_type='json'):
    if return_type == 'json':
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(result, Exception):
            return json.dumps({"status": 500, "result": None, "msg": str(result), "time": time}), 200, {
                'Content-Type': 'application/json'}
        else:
            return json.dumps({"status": 200, "result": result, "msg": "success", "time": time}), 200, {
                'Content-Type': 'application/json'}
    else:
        if isinstance(result, Exception):
            return None, 500, {'Content-Type': 'text/plain'}
        else:
            return str(result).strip(), 500, {'Content-Type': 'text/plain'}


@app.route('/captcha-ocr/<option>/', methods=['GET', 'POST'])
@app.route('/captcha-ocr/<option>/<file_type>/', methods=['GET', 'POST'])
def ocr(option, file_type='base64'):
    if get_kv(request, key='image') is None:
        return render_template('upload_empty.html')
        # return set_ret(Exception("未上传图片"), get_kv(request, key="return_type", default='json'))
    try:
        img = get_img(request, file_type)
        if option == 'ocr':
            result = server.classification(img)
        elif option == 'det':
            result = server.detection(img)
        else:
            raise f"<opt={option}> is invalid"
        return set_ret(result, get_kv(request, key="return_type", default='json'))
    except Exception as e:
        return set_ret(e, get_kv(request, key="return_type", default='json'))


# 还没看明白，先不写
# @app.route('/captcha-ocr/slide/<algo_type>/<img_type>/', methods=['POST'])
# @app.route('/captcha-ocr/slide/<algo_type>/<img_type>/<return_type>/', methods=['POST'])
# def slide(algo_type='compare', img_type='file'):
#     try:
#         target_img = get_img(request, img_type, 'target_img')
#         bg_img = get_img(request, img_type, 'bg_img')
#         result = server.slide(target_img, bg_img, algo_type)
#         return set_ret(result, get_kv(request, key="return_type", default='json'))
#     except Exception as e:
#         return set_ret(e, get_kv(request, key="return_type", default='json'))


@app.route('/captcha-ocr/ping/', methods=['GET'])
def ping():
    return "pong"


@app.route('/captcha-ocr/', methods=['GET'])
def index():
    return render_template('README.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=args.port)

# -*- coding:utf-8 -*-

import json
import math
import random
import re
import time
from binascii import b2a_hex, a2b_hex

import cv2
import numpy as np
import requests
from Crypto.Cipher import AES


class CrackVerification(object):

    def __init__(self):

        self.__bg_img = 'bg_img.jpg'
        self.__puzzle_img = 'puzzle_img.jpg'

        self.__serial_id = None
        self.__code = None
        self.__sign = None
        self.__namespace = None
        self.__url_parm = None
        self.__referer_url = None

        self.__session_id = None
        self.__token = None
        self.__response_id = None
        self.__puzzle_img_url = None
        self.__bg_img_url = None

    def __request_from_server(self, url, data=None, timeout=30, method=0):

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3',
            'accept-encoding': 'gzip, deflate, br',
            'cookie': '58home=gz; f=n; id58=e87rZl4OEAGsjqmoBoEIAg==; '
                      'commontopbar_new_city_info=3%7C%E5%B9%BF%E5%B7%9E%7Cgz; city=gz; '
                      'commontopbar_ipcity=gz%7C%E5%B9%BF%E5%B7%9E%7C0; '
                      '58tj_uuid=f1ea0783-9973-4fd1-8e59-9fc0ceaa0e94; new_session=1; new_uv=1; utm_source=; spm=; '
                      'init_refer=; als=0; xxzl_cid=1751ee096fa144e38be6491509a7980b; '
                      'xzuid=16febb1a-018b-4959-ba5e-426afc75a3c1; wmda_uuid=81c7378e93d18d368b0b54f811479606; '
                      'wmda_new_uuid=1; wmda_session_id_11187958619315=1577979915690-d730d94a-7fea-5205; '
                      'wmda_visited_projects=%3B11187958619315',
            'referer': self.__referer_url,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/78.0.3904.97 Safari/537.36'
        }

        if method == 0:
            r = requests.get(url, headers=headers,
                             params=data, timeout=timeout)
        elif method == 1:
            r = requests.post(url, headers=headers, data=data, timeout=timeout)
        else:
            r = None
        return r

    def __aes_encrypt(self, key, text):
        key = bytes(key, encoding="utf8")
        text = bytes(text, encoding="utf8")

        length = 16 - (len(text) % 16)
        text += bytes([length]) * length

        crypto = AES.new(key, AES.MODE_CBC, key)
        data = b2a_hex(crypto.encrypt(text))

        return str(data, encoding='utf8')

    def __aes_decrypt(self, key, data):
        key = bytes(key, encoding="utf8")

        crypto = AES.new(key, AES.MODE_CBC, key)
        text = crypto.decrypt(a2b_hex(data))
        print(text)
        return str(text, encoding='utf8')

    # def __get_track(self, y):
    #
    #     i = 8
    #     avg = (y / 30) + 1
    #     x_list = [i]
    #     while True:
    #         i += avg
    #         x_list.append(i)
    #         if i >= y:
    #             break
    #     x_list.append(y + 6)
    #     x_list.append(y + 7)
    #     x_list.append(y + 8)
    #     x_list.append(y + 8)
    #
    #     time_list = [
    #         1, 304, 329, 346, 361, 378, 487, 496, 512, 529, 547, 562, 579, 712, 729, 746, 763, 778, 886, 895, 913, 929,
    #         946,
    #         1039, 1471, 1479, 1497, 1513, 2071, 2195, 2250, 2283, 3215, 3520, 3803, 4135, 4515, 4896, 5263, 5322,
    #         5499, 5597
    #     ]
    #
    #     y_list = [19] * 17 + [21] * 25
    #
    #     track = ""
    #     for i in range(len(x_list)):
    #         track += str(x_list[i]) + ',' + str(y_list[i]) + "," + str(time_list[i]) + "|"
    #     return track

    def __generate_slide_trace(self, distance):
        """
        生成滑块验证码轨迹
        :param distance: 缺口距离
        :return:
        """
        start_x = random.randint(10, 40)
        start_y = random.randint(10, 20)
        back = random.randint(2, 6)
        distance += back
        # 初速度
        v = 0
        # 位移/轨迹列表，列表内的一个元素代表0.02s的位移
        tracks_list = []
        # 当前的位移
        current = 0
        while current < distance:
            # 加速度越小，单位时间的位移越小,模拟的轨迹就越多越详细
            a = random.randint(10000, 12000)  # 加速运动
            # 初速度
            v0 = v
            t = random.randint(9, 18)
            s = v0 * t / 1000 + 0.5 * a * ((t / 1000) ** 2)
            # 当前的位置
            current += s
            # 速度已经达到v,该速度作为下次的初速度
            v = v0 + a * t / 1000
            # 添加到轨迹列表
            if current < distance:
                tracks_list.append(round(current))
        # 减速慢慢滑
        if round(current) < distance:
            for i in range(round(current) + 1, distance + 1):
                tracks_list.append(i)
        else:
            for i in range(tracks_list[-1] + 1, distance + 1):
                tracks_list.append(i)
        # 回退
        for _ in range(back):
            current -= 1
            tracks_list.append(round(current))
        tracks_list.append(round(current) - 1)
        if tracks_list[-1] != distance - back:
            tracks_list.append(distance - back)
        # 生成时间戳列表
        timestamp_list = []
        timestamp = random.randint(20, 60)
        for i in range(len(tracks_list)):
            if i >= len(tracks_list) - 6:
                t = random.randint(80, 180)
            else:
                t = random.randint(11, 18)
            timestamp += t
            timestamp_list.append(timestamp)
            i += 1
        y_list = []
        zy = 0
        for j in range(len(tracks_list)):
            y = random.choice(
                [0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0,
                 0,
                 -1, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, -1, 0, 0])
            zy += y
            y_list.append(zy)
            j += 1
        trace = [{'p': f'{start_x},{start_y}', 't': random.choice([0, 1])}]
        for index, x in enumerate(tracks_list):
            trace.append({
                'p': ','.join([str(x + start_x), str(y_list[index] + start_y)]),
                't': timestamp_list[index]
            })
        trace.append({
            'p': f'{tracks_list[-1] + start_x},{y_list[-1] + start_y}',
            't': timestamp_list[-1] + random.randint(100, 300)
        })
        return trace

    def __get_track(self, distance):
        """
        处理轨迹
        :param distance: 轨迹
        :return:
        """
        trace = self.__generate_slide_trace(distance)

        def merge(s): return ','.join([str(s['p']), str(s['t'])])
        new_trace = '|'.join([merge(i) for i in trace]) + '|'
        return new_trace

    def __get_distance(self):

        content = self.__request_from_server(url=self.__bg_img_url).content
        with open(self.__bg_img, 'wb') as f:
            f.write(content)

        content = self.__request_from_server(url=self.__puzzle_img_url).content
        with open(self.__puzzle_img, 'wb') as f:
            f.write(content)

        target = cv2.imread(self.__bg_img, 1)
        template = cv2.imread(self.__puzzle_img, 0)

        target = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)
        target = abs(255 - target)

        result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)
        x, y = np.unravel_index(result.argmax(), result.shape)

        distance = math.floor(y / 1.6 + 0.5)
        return distance

    def __get_parm_from_url(self, url):
        result = re.findall(r'serialId=(.*?)&', url)
        serial_id = result[0]
        self.__serial_id = serial_id

        result = re.findall(r'code=(.*?)&', url)
        code = result[0]
        self.__code = code

        result = re.findall(r'sign=(.*?)&', url)
        sign = result[0]
        self.__sign = sign

        result = re.findall(r'namespace=(.*?)&', url)
        namespace = result[0]
        self.__namespace = namespace

        result = re.findall(r'url=(.*?)$', url)
        url_parm = result[0]
        self.__url_parm = url_parm

        self.__referer_url = url

    def __get_session_id(self):
        # get session id
        url = 'https://callback.58.com/antibot/codev2/getsession.do?{}'.format(
            int(time.time() * 1000))
        data = {
            "serialId": self.__serial_id,
            "code": self.__code,
            "sign": self.__sign,
            "url": self.__url_parm
        }
        json_obj = self.__request_from_server(
            url=url, data=data, method=1).json()
        if json_obj['code'] == 1:
            print(json_obj)
            exit(0)
        self.__session_id = json_obj['data']['sessionId']

    def __get_token(self):
        url = 'https://cdata.58.com/fpToken'
        r = self.__request_from_server(url)
        result = re.findall(r'null\((.*?)\)', r.text)
        json_obj = json.loads(result[0])
        self.__token = json_obj['token']

    def __get_response_id_img_url(self):
        url = 'https://verifycode.58.com/captcha/getV3'
        parm = {
            "showType": "win",
            "sessionId": self.__session_id,
            "_": int(time.time() * 1000)
        }
        json_obj = self.__request_from_server(url=url, data=parm).json()
        self.__response_id = json_obj['data']['responseId']
        self.__puzzle_img_url = "https://verifycode.58.com{}".format(
            json_obj['data']['puzzleImgUrl'])
        self.__bg_img_url = "https://verifycode.58.com{}".format(
            json_obj['data']['bgImgUrl'])

    def __verify_code(self, distance, track):
        key = self.__response_id[0:16]
        text = '{{"x":"{}","track":"{}","p":"0,0","finger":"{}"}}'.format(
            distance, track, self.__token)
        data = self.__aes_encrypt(key, text)

        # verify
        url = 'https://verifycode.58.com/captcha/checkV3'
        parm = {
            "responseId": self.__response_id,
            "sessionId": self.__session_id,
            "data": data,
            "_": str(int(time.time() * 1000))
        }
        json_obj = self.__request_from_server(url=url, data=parm).json()
        print(json_obj)
        if json_obj['message'] == "校验成功":
            source_img = "https://verifycode.58.com{}".format(
                json_obj['data']['sourceimg'])
            success_token = json_obj['data']['successToken']
            return source_img, success_token
        else:
            return []

    def __check_code(self, source_img_success_token):
        url = 'https://callback.58.com/antibot/checkcode.do'
        data = {
            "namespace": self.__namespace,
            "sessionId": self.__session_id,
            "url": self.__url_parm,
            "successToken": source_img_success_token[1],
            "serialId": self.__serial_id
        }
        r = self.__request_from_server(url=url, data=data, method=1)
        print(r.text)

        r = self.__request_from_server(url=source_img_success_token[0])
        print(r.cookies)

    def verify(self, url):
        # get parm
        self.__get_parm_from_url(url)

        # get session id
        self.__get_session_id()

        # get token
        self.__get_token()

        # get image url, response id
        self.__get_response_id_img_url()

        # get distance and track
        distance = self.__get_distance()
        track = self.__get_track(distance)

        # verify code
        source_img_success_token = self.__verify_code(distance, track)

        # # check code
        if source_img_success_token:
            self.__check_code(source_img_success_token)


def main():
    # url = 'https://callback.58.com/antibot/verifycode?serialId' \
    #       '=b258b952f085ac8eee4e07837a86dc2c_61f4852a64894c9c914c290e9db30edc&code=22&sign' \
    #       '=39ef095fa5175996adad8c0eb1636f1c&namespace=chuzulistphp&url=gz.58.com%2Fchuzu%2Fpn78%2F%3FPGTID' \
    #       '%3D0d3090a7-0000-36ce-c765-5f1d3e3dd81b%26ClickID%3D2 '

    url = 'https://callback.58.com/antibot/verifycode?serialId' \
          '=62cbf64a21ab4d309e722680c623a4e4_31ec33353c0648b7a5c97b1f2fb35976&code=22&sign' \
          '=e6760461fc971994a2f3809ff536fbe9&namespace=anjuke_zufang_pc&url=.zu.anjuke.com%2Ffangyuan' \
          '%2F1206610285371393%3Fibsauction%3D1%26shangquan_id%3D1846 '

    crack_verification = CrackVerification()
    crack_verification.verify(url)


if __name__ == '__main__':
    main()

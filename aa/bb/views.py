from rest_framework.response import Response
from .models import *
from rest_framework.decorators import api_view
import math
import numpy as np
import pandas as pd
from datetime import datetime
import json
@api_view(['GET', 'POST'])
def Str(request):
    if request.method == 'GET':
        temp = request.GET['temp']
        time = request.GET['time']
        wc = request.GET['wc']
        model = request.GET['model']
        maturity = (int(temp) + 10) * int(time)
        if model == 'Plowman':
            pass
            '''
            if wc == '40':
                pred_7 = -102.8256 + (66.4097 * np.log(maturity * 7 / int(time)))
                pred_14 = -102.8256 + 66.4097 * math.log(maturity * 14 / int(time))
                pred_28 = -102.8256 + 66.4097 * math.log(maturity * 28 / int(time))
                pred_90 = -102.8256 + 66.4097 * math.log(maturity * 90 / int(time))

            elif wc == '50':
                pred_7 = -130.3213 + 63.1236 * math.log(maturity * 7 / int(time))
                pred_14 = -130.3213 + 63.1236 * math.log(maturity * 14 / int(time))
                pred_28 = -130.3213 + 63.1236 * math.log(maturity * 28 / int(time))
                pred_90 = -130.3213 + 63.1236 * math.log(maturity * 90 / int(time))

            elif wc == '60':
                pred_7 = -126.3720 + 54.0205 * math.log(maturity * 7 / int(time))
                pred_14 = -126.3720 + 54.0205 * math.log(maturity * 14 / int(time))
                pred_28 = -126.3720 + 54.0205 * math.log(maturity * 28 / int(time))
                pred_90 = -126.3720 + 54.0205 * math.log(maturity * 90 / int(time))

            elif wc == '70':

                pred_7 = -103.6550 + 45.7503 * math.log(maturity * 7 / int(time))
                pred_14 = -103.6550 + 45.7503 * math.log(maturity * 14 / int(time))
                pred_28 = -103.6550 + 45.7503 * math.log(maturity * 28 / int(time))
                pred_90 = -103.6550 + 45.7503 * math.log(maturity * 90 / int(time))

        pred = {"7days": pred_7,
                "14days": pred_14,
                "28days": pred_28,
                "90days": pred_90}
        pred1 = json.loads(json.dumps(pred))
        return Response(pred1)
    '''
    elif request.method == 'POST':
        temp_data = request.data['temp']
        wc = request.data['wc']
        model = request.data['model']
        day, temp = list(temp_data), list(temp_data.values())
        data_dic = {"date": day, "temp": temp}  # 딕셔너리 형성 (속성이 없어서 데이터 프레임으로 바로 변환 안됨)
        df = pd.DataFrame(data_dic)  # 데이터 프레임 형성

        day_avg, day = get_avg(df)  # 일 평균 온도 리스트와 며칠의 데이터가 있는지 반환

        # 적산 온도
        maturity_7 = Maturity(7, day_avg, day)
        maturity_14 = Maturity(14, day_avg, day)
        maturity_28 = Maturity(28, day_avg, day)
        maturity_90 = Maturity(90, day_avg, day)
        # 강도 추정
        pred_7 = Strength(maturity_7, model, wc)
        pred_14 = Strength(maturity_14, model, wc)
        pred_28 = Strength(maturity_28, model, wc)
        pred_90 = Strength(maturity_90, model, wc)

        # 강도 추정 결과와 날짜 매핑
        pred = {
                    '7day': pred_7, '14day': pred_14, '28day': pred_28, '90day': pred_90
                }
        pred1 = json.loads(json.dumps(pred))

        return Response(pred1)


def timedelta2int(td):  # timedelta 형식을 int로 변환
    result = round(td.microseconds / float(1000000)) + (td.seconds + td.days * 24 * 3600)
    return result


def get_avg(df):
    str2datetime = []
    # interval 계산을 위해 날짜를 datetime 형식으로 변환
    for i in range(len(df)):
        str2datetime.append(datetime.strptime(df['date'][i], "%Y-%m-%d %H:%M:%S"))
    # 날짜 데이터의 간격
    interval = timedelta2int(str2datetime[1] - str2datetime[0])
    # 하루에 몇개의 데이터가 있는가
    one_day_cnt = (24 * 60 * 60) // interval
    # 총 며칠의 데이터가 있는가
    day_cnt = len(df) // one_day_cnt
    # one_day_cnt를 만족하지 못하는 데이터들의 개수
    remainder_cnt = len(df) % one_day_cnt

    day_avg = []
    for i in range(int(day_cnt)):
        end = int((i + 1) * one_day_cnt)  # 슬라이싱을 위해 마지막 인덱스 설정
        if i == 0:  # 1일차의 일 평균 온도
            avg = np.sum(df[:end]['temp']) / one_day_cnt
        else:  # 2, 3..일차의 일 평균 온도
            start = int(i * one_day_cnt)  # 시작 인덱스
            avg = np.sum(df[start:end]['temp']) / one_day_cnt
        day_avg.append(avg)  #

    if remainder_cnt != 0:  # 마지막 일차의 데이터 수가 24개보다 적으면
        rest = np.sum(df[end:]['temp'])  # 나머지 온도를 다 더하고 그 개수로 나눔.
        day_avg.append(rest / remainder_cnt)  # 일 평균 온도 리스트에 추가
        day_cnt += 1

    return day_avg, int(day_cnt)


def Maturity(i, day_avg, day):
    day_avg = [i + 10 for i in day_avg]  # 일 평균 온도에 10을 각각 더함.

    if i == 7:
        if day < 7:
            maturity = np.sum(day_avg[:day]) * (7 / day)
        else:
            maturity = np.sum(day_avg[:7])
    elif i == 14:
        if day < 14:
            maturity = np.sum(day_avg[:day]) * (14 / day)
        else:
            maturity = np.sum(day_avg[:14])
    elif i == 28:
        if day < 28:
            maturity = np.sum(day_avg[:day]) * (28 / day)
        else:
            maturity = np.sum(day_avg[:28])
    elif i == 90:
        if day < 90:
            maturity = np.sum(day_avg[:day]) * (90 / day)
        else:
            maturity = np.sum(day_avg[:90])

    return maturity


def Strength(maturity, model, wc):
    if model == 'Plowman':
        if wc == '40':
            strength = -102.8256 + 66.4097 * math.log(maturity)
        elif wc == '50':
            strength = -130.3213 + 63.1236 * math.log(maturity)
        elif wc == '60':
            strength = -126.3720 + 54.0205 * math.log(maturity)
        elif wc == '70':
            strength = -103.655 + 45.7503 * math.log(maturity)
    elif model == 'Lew&Reichard':
        if wc == '40':
            strength = 612.25 / (1 + 73.3993 * (math.log(maturity - 16.7)) ** (-2.4838))
        elif wc == '50':
            strength = 681.25 / (1 + 154.6303 * (math.log(maturity - 16.7)) ** (-2.7258))
        elif wc == '60':
            strength = 439.25 / (1 + 225.2903 * (math.log(maturity - 16.7)) ** (-2.969))
        elif wc == '70':
            strength = 353.25 / (1 + 375.5053 * (math.log(maturity - 16.7)) ** (-2.9595))
    elif model == 'Logistic':
        if wc == '40':
            strength = 400.25 / (1 + math.exp(-0.984 * math.log(maturity) + 4.373))
        elif wc == '50':
            strength = 392.75 / (1 + math.exp(-1.0063 * math.log(maturity) + 4.8658))
        elif wc == '60':
            strength = 285.75 / (1 + math.exp(-1.061 * math.log(maturity) + 5.118))
        elif wc == '70':
            strength = 263.5 / (1 + math.exp(-0.922 * math.log(maturity) + 5.0103))
    elif model == 'Gompertz':
        if wc == '40':
            strength = 447.25 * math.exp(-18.8645 * (1 / maturity) ** 0.654)
        elif wc == '50':
            strength = 406.25 * math.exp(-20.038 * (1 / maturity) ** 0.6328)
        elif wc == '60':
            strength = 336.5 * math.exp(-26.2728 * (1 / maturity) ** 0.6445)
        elif wc == '70':
            strength = 300 * math.exp(-16.595 * (1 / maturity) ** 0.5063)

    return strength


'''
@api_view(['GET','POST'])
def Str(request):

    if request.method == 'GET':
        temp = request.GET['temp']
        time = request.GET['time']
        wc = request.GET['wc']
        model = request.GET['model']
        maturity = (int(temp) + 10) * int(time)
        if model == 'Plowman':
            if wc == '40':
                str1 = -102.8256 + (66.4097 * np.log(maturity * 7 / int(time)))
                str2 = -102.8256 + 66.4097 * math.log(maturity * 14 / int(time))
                str3 = -102.8256 + 66.4097 * math.log(maturity * 28 / int(time))
                str4 = -102.8256 + 66.4097 * math.log(maturity * 90 / int(time))
                a = {"7days": str1,
                     "14days" : str2,
                     "28days" : str3,
                     "90days" : str4}

                return Response(a)
            elif wc == '50':

                str1 = -130.3213 + 63.1236 * math.log(maturity * 7 / int(time))
                str2 = -130.3213 + 63.1236 * math.log(maturity * 14 / int(time))
                str3 = -130.3213 + 63.1236 * math.log(maturity * 28 / int(time))
                str4 = -130.3213 + 63.1236 * math.log(maturity * 90 / int(time))
                a = {"7days": str1,
                     "14days": str2,
                     "28days": str3,
                     "90days": str4}

                return Response(a)

            elif wc == '60':

                    str1 = -126.3720 + 54.0205 * math.log(maturity * 7 / int(time))
                    str2 = -126.3720 + 54.0205 * math.log(maturity * 14 / int(time))
                    str3 = -126.3720 + 54.0205 * math.log(maturity * 28 / int(time))
                    str4 = -126.3720 + 54.0205 * math.log(maturity * 90 / int(time))
                    a = {"7days": str1,
                         "14days": str2,
                         "28days": str3,
                         "90days": str4}

                    return Response(a)
            elif wc == '70':

                    str1 = -103.6550 + 45.7503 * math.log(maturity * 7 / int(time))
                    str2 = -103.6550 + 45.7503 * math.log(maturity * 14 / int(time))
                    str3 = -103.6550 + 45.7503 * math.log(maturity * 28 / int(time))
                    str4 = -103.6550 + 45.7503 * math.log(maturity * 90 / int(time))
                    a = {"7days": str1,
                         "14days": str2,
                         "28days": str3,
                         "90days": str4}

                    return Response(a)
    elif request.method == 'POST':
        a = request.data['temp']
        wc = request.data['wc']
        model = request.data['model']
        print(type(a))
        print(wc)
        print(model)
        day, temp = list(a), list(a.values())  # 데이터 프레임으로 만들기위해 데이터 추출
        da = {"date": day, "temp": temp}  # 값의 속성 지정해주고, 합침
        df = pd.DataFrame(da)  # 데이터 프레임 형성

        day_avg, day = get_avg(df)  # 일 평균 온도 리스트와 며칠의 데이터가 있는지 반환

        Maturity_7 = Maturity(7, day_avg, day)  # 적산 온도 반환
        Maturity_14 = Maturity(14, day_avg, day)
        Maturity_28 = Maturity(28, day_avg, day)
        Maturity_90 = Maturity(90, day_avg, day)
        print(Maturity_7)
        pred_28 = Strength(Maturity_28, model, wc)  # 강도 추정 반환
        pred_7 = Strength(Maturity_7, model, wc)
        pred_14 = Strength(Maturity_14, model, wc)
        pred_90 = Strength(Maturity_90, model, wc)
        print(pred_7)
        pred = {"7day": pred_7, "14day": pred_14, "28day": pred_28, "90day": pred_90}  # 강도 추정 결과와 날짜 매핑
        str = {"7days": pred_7,
               "14days": pred_14,
               "28days": pred_28,
               "90days": pred_90, }
        # a = Strength.objects.all()
        # serializer = StrSerializer(a,many=True)
        # print(serializer.data)
        print(pred)
        print(pred_7)
        a = {"sucess" : "ok"}
        return Response(pred)
        # return Response(pred)

def timedelta2int(td):  # timedelta 형식을 int로 변환
        result = round(td.microseconds / float(1000000)) + (td.seconds + td.days * 24 * 3600)
        return result

def get_avg(df):
        make = []  # 날짜를 datetime 형식으로 변환해서 저장하는 리스트
        for i in range(len(df)):  # 데이터의 개수만큼 반복
            # interval 계산을 위해 날짜를 datetime 형식으로 변환
            make.append(datetime.strptime(df['date'][i], "%Y-%m-%d %H:%M:%S"))
        interval = timedelta2int(make[1] - make[0])  # 날짜 데이터의 시간 간격
        print(interval)
        one_day_cnt = 24 * 60 * 60 / interval  # 하루에 몇개의 데이터가 있는지 확인
        day_cnt = len(df) // one_day_cnt  # 총 며칠의 데이터가 있는지 확인
        re = len(df) % one_day_cnt  # 24시간이 되지 않는 데이터들의 개수 구하기
        day_list = []  # 일 평균 온도 리스트

        for i in range(int(day_cnt)):
            end = int((i + 1) * one_day_cnt)  # 데이터 프레임에서 슬라이싱을 위해 마지막 인덱스 설정하기
            if i == 0:  # 1일차의 일 평균 온도를 구함.
                print("1 일차 총합 = ", np.sum(df[:end]['temp']), "분모 = ", one_day_cnt)
                avg = np.sum(df[:end]['temp']) / one_day_cnt
            #                 elif i == int(day_cnt)-1:
            #                         start = int(i * one_day_cnt) # 시작하는 인덱스
            #                         print(i+1, "일차 총합 = " , np.sum(df[start:end]['temp']), "분모 = ", re)
            #                         avg = np.sum(df[start:end]['temp']) / re
            else:  # 2, 3, ...일차의 일 평균 온도를 구함.
                start = int(i * one_day_cnt)  # 시작하는 인덱스
                print(i + 1, "일차 총합 = ", np.sum(df[start:end]['temp']), "분모 = ", one_day_cnt)
                avg = np.sum(df[start:end]['temp']) / one_day_cnt
            day_list.append(avg)  # 일 평균 온도를 리스트에 넣음
        if re != 0:  # 마지막 일차의 데이터 수가 24개보다 적으면
            rest = np.sum(df[end:]['temp'])  # 나머지 온도를 다 더하고 그 개수로 나눔.
            day_list.append(rest / re)  # 일 평균 온도 리스트에 추가
            day_cnt += 1
        print("하루에 몇개의 데이터가 있는가?", one_day_cnt, "총 며칠의 데이터가 있는가? ", day_cnt)
        print(day_list)
        return day_list, int(day_cnt)

def Maturity(i, day_avg, day):
        day_avg = [i + 10 for i in day_avg]  # 일 평균 온도에 10을 각각 더함.
        if i == 7:
            if day < 7:
                maturity = np.sum(day_avg[:day]) * (7 / day)
            else:
                maturity = np.sum(day_avg[:7])
        elif i == 14:
            if day < 14:
                maturity = np.sum(day_avg[:day]) * (14 / day)
            else:
                maturity = np.sum(day_avg[:14])
        elif i == 28:
            if day < 28:
                maturity = np.sum(day_avg[:day]) * (28 / day)
            else:
                maturity = np.sum(day_avg[:28])
        elif i == 90:
            if day < 90:
                maturity = np.sum(day_avg[:day]) * (90 / day)
            else:
                maturity = np.sum(day_avg[:90])
        print("적산온도= ", maturity)
        return maturity

def Strength(maturity, model, wc):

        if model == 'Plowman':
            if wc == '40':
                s = -102.8256 + 66.4097 * math.log(maturity)
            elif wc == '50':
                s = -130.3213 + 63.1236 * math.log(maturity)
            elif wc == '60':
                s = -126.3720 + 54.0205 * math.log(maturity)
            elif wc == '70':
                s = -103.655 + 45.7503 * math.log(maturity)
            return s
        elif model == 'Lew&Reichard':
            if wc == '40':
                s = 612.25 / (1 + 73.3993 * (math.log(maturity - 16.7)) ** (-2.4838))
            elif wc == '50':
                s = 681.25 / (1 + 154.6303 * (math.log(maturity - 16.7)) ** (-2.7258))
            elif wc == '60':
                s = 439.25 / (1 + 225.2903 * (math.log(maturity - 16.7)) ** (-2.969))
            elif wc == '70':
                s = 353.25 / (1 + 375.5053 * (math.log(maturity - 16.7)) ** (-2.9595))
            return s
        elif model == 'Logistic':
            if wc == '40':
                s = 400.25 / (1 + math.exp(-0.984 * math.log(maturity) + 4.373))
            elif wc == '50':
                s = 392.75 / (1 + math.exp(-1.0063 * math.log(maturity) + 4.8658))
            elif wc == '60':
                s = 285.75 / (1 + math.exp(-1.061 * math.log(maturity) + 5.118))
            elif wc == '70':
                s = 263.5 / (1 + math.exp(-0.922 * math.log(maturity) + 5.0103))
            return s
        elif model == 'Gompertz':
            if wc == '40':
                s = 447.25 * math.exp(-18.8645 * (1 / maturity) ** 0.654)
            elif wc == '50':
                s = 406.25 * math.exp(-20.038 * (1 / maturity) ** 0.6328)
            elif wc == '60':
                s = 336.5 * math.exp(-26.2728 * (1 / maturity) ** 0.6445)
            elif wc == '70':
                s = 300 * math.exp(-16.595 * (1 / maturity) ** 0.5063)
            return s
'''

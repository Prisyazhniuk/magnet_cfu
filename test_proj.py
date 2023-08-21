import sys
import glob
import serial
from zhinst.toolkit import Session
from past.builtins import raw_input



def decimal_range(start, stop, increment):
    while start < stop:
        yield start
        start += increment


def rev_decimal_range(start, stop, increment):
    while start > stop:
        yield start
        start -= increment



def magnet_set():

    set_I = 0.05
    step_I = 0.01
    _i = 0.00

    # ser.write("A007SYST:REM\n".encode())
    # ser.close()
    # ser.open()
    # ser.write("A007*CLS\n".encode())
    # ser.close()
    # ser.open()
    # ser.write("A007OUTP ON\n".encode())
    # ser.close()
    # ser.open()
    # ser.write("A007MEAS:CURR?\n".encode())
    # result = ser.read(11)
    #
    #
    # print(result)
    #
    #
    # ser.write("A007FETC?\n".encode())
    # realCurrVolt = ser.read(23)
    # ser.close()
    # print(realCurrVolt)

    if 0.0 <= abs(set_I) < 7.5:

        if set_I > 0:
            for _i in decimal_range(_i, set_I + step_I, step_I):
                a = "A007SOUR:VOLT "
                b = _i * 10
                c = "CURR "
                d = _i
                res = f"{a}{b:.3f};{c}{d:.3f}\n"
                print(res)

        elif set_I < 0:
            for _i in rev_decimal_range(_i, set_I - step_I, step_I):
                a = "A007SOUR:VOLT "
                b = _i * 10
                c = "CURR "
                d = _i
                res = f"{a}{b:.3f};{c}{d:.3f}\n"
                print(res)

    elif abs(set_I) > 7.5 and abs(step_I) > 0.05:
        print("Ток не может быть больше 7.5 А и шаг по току не может быть больше 0.05")
    elif abs(step_I) > 0.05:
        print("Шаг по полю не может быть больше 0.05 А")
    elif abs(set_I) > 7.5:
        print("Ток не может быть больше 7.5 А")


def reset_magn():
    set_I = 0.05
    step_I = 0.01
    _i = 0.00

    if set_I > 0:
        for _i in rev_decimal_range(set_I - step_I, _i - step_I, step_I):
            a = "A007SOUR:VOLT "
            b = _i * 10
            c = "CURR "
            d = _i
            res = f"{a}{b:.3f};{c}{d:.3f}\n"
            print(res)

    if set_I < 0:
        for _i in decimal_range(set_I + step_I, _i + step_I, step_I):
            a = "A007SOUR:VOLT "
            b = _i * 10
            c = "CURR "
            d = _i
            res = f"{a}{b:.3f};{c}{d:.3f}\n"
            print(res)


# def volt_amper_check():
#     ser = serial.Serial(baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout=0.3)
#     ser.port = "COM{}".format(COMPORT)
#     ser.open()
#
#     ser.write("A007FETC?\n".encode())
#     realCurrVolt = ser.read(23)
#     ser.close()
#     print(realCurrVolt)


if __name__ == '__main__':


    magnet_set()
    print("////////////////")
    reset_magn()

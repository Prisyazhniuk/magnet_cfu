import sys
import glob
from interface import MagnetCFU
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
# from zhinst.toolkit import Session

# from lock-in docs
###########################################################################################################

# import copy
# import json
# import logging
# import re
# import typing as t
# import warnings
# from pathlib import Path
#
# from zhinst.utils._version import version as utils_version_str
# from zhinst.core import __version__ as zhinst_version_str
#
# from zhinst.toolkit._min_version import _MIN_DEVICE_UTILS_VERSION, _MIN_LABONE_VERSION
# from zhinst.toolkit.driver.parsers import node_parser
# from zhinst.toolkit.nodetree import Node, NodeTree
# from zhinst.toolkit.nodetree.helper import lazy_property
# from zhinst.toolkit.exceptions import ToolkitError
#

###########################################################################################################

def decimal_range(start, stop, increment):
    while start < stop:
        yield start
        start += increment


def rev_decimal_range(start, stop, increment):
    while start > stop:
        yield start
        start -= increment


def serial_ports():
    return [port.portName() for port in QSerialPortInfo().availablePorts()]



# def init_serial():
#     ser = (baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout=0.3)
#     ser.port = "COM{}".format(COMPORT)
#
#     ser.open()
#
#     if ser.isOpen():
#         print('Open: ' + ser.portstr)
#
#     ser.write("A007*IDN?\n".encode())
#     result = ser.read(33)
#     ser.close()
#     print(result)
#

# def magnet_read():
#     ser = serial.Serial(baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout=0.3)
#     ser.port = "COM{}".format(COMPORT)
#
#     ser.open()
#     ser.write("A007MEAS:VOLT?\n".encode())
#     res_volt = ser.read(30)
#     ser.write("A007MEAS:CURR?\n".encode())
#     res_curr = ser.read(30)
#     ser.close()
#     volt, curr = res_volt, res_curr
#     print(f' Voltage = {float(volt)} V, Current = {float(curr)} A')
#
#
# def magnet_set():
#     ser = serial.Serial(baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout=0.3)
#     ser.port = "COM{}".format(COMPORT)
#
#     set_I = float(input("Enter I set: "))
#     step_I = float(input("Enter I step: "))
#     _i = 0.00
#
#     ser.open()
#
#     ser.write("A007SYST:REM\n".encode())
#     ser.close()
#     ser.open()
#     ser.write("A007*CLS\n".encode())
#     ser.close()
#     ser.open()
#     ser.write("A007OUTP ON\n".encode())
#     ser.close()
#     ser.open()
#     ser.write("A007MEAS:CURR?\n".encode())
#     result = ser.read(11)
#
#     ser.close()
#
#     print(result)
#
#     ser.open()
#
#     ser.write("A007FETC?\n".encode())
#     realCurrVolt = ser.read(23)
#     ser.close()
#     print(realCurrVolt)
#
#     if 0.0 <= abs(set_I) < 7.5:
#
#         if set_I > 0:
#             for _i in decimal_range(_i, set_I + step_I, step_I):
#                 a = "A007SOUR:VOLT "
#                 b = _i * 10
#                 c = "CURR "
#                 d = _i
#                 res = f"{a}{b:.3f};{c}{d:.3f}\n"
#                 ser.open()
#                 ser.write(res.encode())
#                 ser.close()
#
#         elif set_I < 0:
#             for _i in rev_decimal_range(_i, set_I - step_I, step_I):
#                 a = "A007SOUR:VOLT "
#                 b = _i * 10
#                 c = "CURR "
#                 d = _i
#                 res = f"{a}{b:.3f};{c}{d:.3f}\n"
#                 ser.open()
#                 ser.write(res.encode())
#                 ser.close()
#
#     elif abs(set_I) > 7.5 and abs(step_I) > 0.05:
#         print("Ток не может быть больше 7.5 А и шаг по току не может быть больше 0.05")
#     elif abs(step_I) > 0.05:
#         print("Шаг по полю не может быть больше 0.05 А")
#     elif abs(set_I) > 7.5:
#         print("Ток не может быть больше 7.5 А")
#
#     print("Do I need to reset the current?\n> ", end='')
#     for_reset = input()
#     _i = 0.0
#     if for_reset == "y":
#         if set_I > 0:
#             for _i in rev_decimal_range(set_I - step_I, _i - step_I, step_I):
#                 a = "A007SOUR:VOLT "
#                 b = _i * 10
#                 c = "CURR "
#                 d = _i
#                 res = f"{a}{b:.3f};{c}{d:.3f}\n"
#                 ser.open()
#                 ser.write(res.encode())
#                 ser.close()
#                 print("test")
#
#             ser.open()
#             ser.write("A007OUTP OFF\n".encode())
#             ser.close()
#             ser.open()
#             ser.write("A007*RST\n".encode())
#             ser.close()
#         else:
#             print("Error")
#
#         if set_I < 0:
#             for _i in decimal_range(set_I + step_I, _i + step_I, step_I):
#                 a = "A007SOUR:VOLT "
#                 b = _i * 10
#                 c = "CURR "
#                 d = _i
#                 res = f"{a}{b:.3f};{c}{d:.3f}\n"
#                 ser.open()
#                 ser.write(res.encode())
#                 ser.close()
#
#             ser.open()
#             ser.write("A007OUTP OFF\n".encode())
#             ser.close()
#             ser.open()
#             ser.write("A007*RST\n".encode())
#             ser.close()
#     else:
#         print("ERROR")
#
#
# def reset_magn():
#     ser = serial.Serial(baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout=0.3)
#     ser.port = "COM{}".format(COMPORT)
#
#
#
#     ser.open()
#     ser.write("A007OUTP OFF\n".encode())
#     ser.close()
#     ser.open()
#     ser.write("A007*RST\n".encode())
#     ser.close()
#
#
# def volt_amper_check():
#     ser = serial.Serial(baudrate=115200, bytesize=8, parity="N", stopbits=1, timeout=0.3)
#     ser.port = "COM{}".format(COMPORT)
#     ser.open()
#
#     ser.write("A007FETC?\n".encode())
#     realCurrVolt = ser.read(23)
#     ser.close()
#     print(realCurrVolt)
#

if __name__ == '__main__':

    print(serial_ports())
    # COMPORT = int(input("Please enter the port number: "))
    # init_serial()
    # magnet_read()
    # print()
    #
    # print("do u wanna set current (y/n)? \n> ", end='')
    # s = input()
    # if s == 'y':
    #     magnet_set()
    # else:
    #     print('OK.')
    #
    # print("do u wanna checking current (y/n)? \n> ", end='')
    # s = input()
    # if s == 'y':
    #     volt_amper_check()
    # else:
    #     print('OK.')
    #
    # print("do u wanna reset current (y/n)? \n> ", end='')
    # s = input()
    # if s == 'y':
    #     reset_magn()
    # else:
    #     print('OK.')

    # IP address of the host computer where the Data Servers run
    # server_host = 'localhost'
    # # A session opened to LabOne Data Server
    # session = Session(server_host)
    # # A session opened to HF2 Data Server
    # hf2_session = Session(server_host, hf2=True)
    # device = session.connect_device("DEV4999")
    #
    #
    # print(device.demods[0].rate.node_info)

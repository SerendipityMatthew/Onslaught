# -*-coding:utf-8-*-
import asyncio
import functools
import os
import subprocess

import Device.Android_Device as Android_Device
import time

import main


async def catch_device_log(device: Android_Device, package_name: str):
    if not device.isOnline():
        return
    # 再次检查一下设备是否在线
    realTimeDevice = main.get_device()[device.deviceId]
    print("-----------------" + str(realTimeDevice.isOnline()))
    if not realTimeDevice.isOnline():
        return

    # log 的路径  包名 /  日期
    date = time.strftime("%Y-%m-%d_%H", time.localtime())
    current_path = os.getcwd()

    log_path = current_path + "/" + package_name
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_file_path = log_path + "/" + date + ".log"

    print(log_file_path)
    logcat_cmd = "adb -s " + realTimeDevice.deviceId + " logcat -b all"
    log_file = open(log_file_path, "w")
    print("==========")
    result = subprocess.Popen(logcat_cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(result.stdout.readline, "b"):
        log_file.write(line.decode('utf-8', 'ignore'))
        log_file.flush()


async def multi_fun(x):
    print("waiting:{}".format(x))
    await asyncio.sleep(x)
    # loop.stop()  # 手动结束loop


async def multi_funs(x):
    print("waiting:{}".format(x))
    await multi_fun(x)


def done_callback(trans):
    print("finish the coroutine: ", trans)
    loop.stop()


async def timer(x, cb):
    futu = asyncio.ensure_future(asyncio.sleep(x))
    futu.add_done_callback(cb)
    await futu


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # 1.run_util_complete()方法运行协程
    # loop.run_until_complete(multi_fun(3))
    # loop.run_until_complete(asyncio.ensure_future(multi_fun(x=3)))

    # 2.协程执行完成后回调方法
    en_fun = asyncio.ensure_future(multi_fun(3))
    en_fun.add_done_callback(done_callback)
    loop.run_until_complete(en_fun)

    # 3.运行多个协程,coroutine gather,运行完成后回调结束
    # coroutine_list = [multi_fun(3), multi_funs(5)]
    # multi_coroutine = asyncio.gather(*coroutine_list)
    # multi_coroutine.add_done_callback(done_callback)
    # loop.run_until_complete(multi_coroutine)

    # 4.run_forever()方法运行协程，方法内部手动结束协程
    # asyncio.ensure_future(multi_fun(5))
    # loop.run_forever()

    # 5.run_forever()方法运行，回调结束
    # coroutine_list = [multi_fun(5), multi_funs(3)]
    # _gather = asyncio.gather(*coroutine_list)
    # _gather.add_done_callback(functools.partial(done_callback))
    # loop.run_forever()

    #  6.gather 和wait的用法
    # coroutine_list = [multi_fun(5), multi_funs(3)]
    # loop.run_until_complete(asyncio.wait(coroutine_list))

    # t = timer(3, lambda futu: print('Done'))
    # loop.run_until_complete(t)

    # 关闭loop,以彻底清除loop对象防止误用
    loop.close()

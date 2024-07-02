# -*- coding: utf-8 -*-
"""
Created on Sat Aug 17 17:47:35 2019

@author: LeTai-FCU
"""
#!/usr/bin/env python3
#gksudo kate /usr/local/lib/python3.5/dist-packages/rplidar.py

# RPLidar 모듈을 가져옵니다.
from rplidar import RPLidar
import time

# RPLidar 객체를 생성하고 시리얼 포트를 지정합니다.
lidar = RPLidar('/dev/ttyUSB1')
# LiDAR 정보를 가져옵니다.
info = lidar.get_info()
print(info)
# LiDAR 상태를 가져옵니다.
health = lidar.get_health()
print(health)

def GetDataScanLiDAR():
    # LiDAR 스캔 데이터를 가져오는 함수입니다.
    oldTime = None
    dataSpeed = []

    try:
        # 스캔된 데이터 목록을 반복합니다.
        for i, scan in enumerate(lidar.iter_scans()):
            now = time.time()
            if oldTime is None:
                oldTime = now
                continue
            deltaTime = now - oldTime
            dataSpeed.append(deltaTime)
            oldTime = now
            # 각 스캔 데이터에서 측정값을 가져옵니다.
            for valueScan in scan:
                strInValueScan = valueScan
                valueQuality = strInValueScan[0]
                valueAngle = strInValueScan[1]
                valueDistance = strInValueScan[2]
                print('Angle: ', valueAngle)
                print('Distance: ', valueDistance)
    except KeyboardInterrupt:
        # Ctrl + C를 눌러 중지합니다.
        print('Stop')
        # LiDAR를 정지합니다.
        lidar.stop()
        lidar.stop_motor()
        lidar.disconnect()
        deltaTime = sum(dataSpeed)/len(dataSpeed)
        print('Average: %.2f Hz, %.2f RPM' % (1/deltaTime, 60/deltaTime))

if __name__ == '__main__':
    GetDataScanLiDAR()

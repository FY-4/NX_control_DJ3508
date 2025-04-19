#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import can
import time
import struct

class DJI3508MotorController:
    def __init__(self, can_interface='can0'):
        """
        初始化CAN接口
        :param can_interface: CAN接口名称，默认为'can0'
        """
        self.bus = can.interface.Bus(
            channel=can_interface,
            bustype='socketcan'

        )
        self.motor_id = 0x200  # 默认电机ID，根据实际情况修改
        
    def send_motor_command(self, angle_control=False, torque_current=0, speed=0, angle=0):
        """
        发送电机控制命令（明确8字节格式）
        """
        # 限制参数范围
        torque_current = max(-16384, min(16384, torque_current))
        speed = max(-32768, min(32767, speed))
        angle = max(0, min(8191, angle))
    
        if angle_control:
            data = struct.pack('<hhhxx'                                                                                                                                                                                                                                                          ,  # <表示小端，h表示int16，xx表示2字节填充
                torque_current,
                speed,
                angle
            )   
        else:
            data = struct.pack('<hhhxx',
                torque_current,
                speed,
                0
            )
    
        #print(f"Sending raw data: {bytes(data).hex()}")  # 打印原始字节
    
        msg = can.Message(
            arbitration_id=self.motor_id,
            data=data,
            is_extended_id=False
        )
    
        try:
            m=0
            b=True
            while b:
                if m<=20000:
                    m+=1
                    self.bus.send(msg)
                    time.sleep(0.001)
                    print(f"Message sent: {msg} (Data: {msg.data.hex()})")
                else:
                    b=False
            #self.bus.send(msg)
            
        except can.CanError as e:
            #print(f"Send failed: {e}")
            pass

    def stop_motor(self):
        """停止电机"""
        self.send_motor_command(torque_current=0, speed=0)

    def __del__(self):
        """析构函数，关闭CAN总线"""
        self.bus.shutdown()


if __name__ == "__main__":
    # 使用示例
    motor = DJI3508MotorController('can0')
    
    try:
        # 示例1: 以1000rpm的速度旋转
        print("Setting speed to 1000 rpm")
        motor.send_motor_command(torque_current=20, speed=10)
        time.sleep(3)
        
        # 示例2: 停止电机
        #print("Stopping motor")
        #motor.stop_motor()
        #time.sleep(1)
        
        # 示例3: 角度控制（如果需要）
        #print("Angle control to 90 degrees")
        #motor.send_motor_command(angle_control=True, angle=2048)  # 2048 = 90度
        #time.sleep(1)
        
    except KeyboardInterrupt:
        print("Interrupted by user")
    finally:
        motor.stop_motor()

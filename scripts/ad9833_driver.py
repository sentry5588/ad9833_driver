#!/usr/bin/env python

# 
#   Toy code for simple control of the AD9833 DDS chip
# 
#   adapted from https://github.com/mjoldfield/ad9833/blob/master/rpi/test.py
#   
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.
#   
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.
#   
#   You should have received a copy of the GNU Lesser General Public
#   License along with this library; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
# 

import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Imu
import gpiozero

class AD9833:

    def __init__(self, data, clk, fsync):
        self.dataPin  = gpiozero.OutputDevice(pin = data)
        self.clkPin   = gpiozero.OutputDevice(pin = clk)
        self.fsyncPin = gpiozero.OutputDevice(pin = fsync)

        self.fsyncPin.on()
        self.clkPin.on()
        self.dataPin.off()

        self.clk_freq = 25.0e6

    def set_freq(self, f):
        flag_b28  = 1 << 13
        flag_freq = 1 << 14

        scale = 1 << 28
        n_reg = int(f * scale / self.clk_freq)

        n_low = n_reg         & 0x3fff
        n_hi  = (n_reg >> 14) & 0x3fff

        self.send16(flag_b28)
        self.send16(flag_freq | n_low)
        self.send16(flag_freq | n_hi)

    def send16(self, n):
        self.fsyncPin.off()

        mask = 1 << 15
        for i in range(0, 16):

            self.dataPin.value = bool(n & mask)
            self.clkPin.off()
            self.clkPin.on()

            mask = mask >> 1

        self.dataPin.off()
        self.fsyncPin.on()

motor = AD9833(10, 11, 8)

def callback(data):
#    rospy.loginfo(rospy.get_caller_id() + "I heard %.3f", data.angular_velocity.y)
    motor.set_freq(1.0)
    
def motor_actuation():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # name are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('ad9833_actuation', anonymous=True)

    rospy.Subscriber("imu", Imu, callback)
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    motor_actuation()


#!/usr/bin/env python3

import argparse
import time
import sys
import random
import os
from math import sin, pi
import numpy as np
from datetime import datetime
from pymavlink import mavutil


#-------------------------------------------------------------------------------


def sendHeartbeat(mavlink):
    mavlink.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_ONBOARD_CONTROLLER,
        mavutil.mavlink.MAV_AUTOPILOT_GENERIC,
        0,
        0,
        0)

def getRawMavlinkStream(mavlink):
    while True:
        time.sleep(0.1)
        try:
            print(mavlink.recv_match(blocking=True).to_dict())
        except:
            pass

def readPilotParameters(mavlink):
    # Request all parameters
    mavlink.mav.param_request_list_send(mavlink.target_system, mavlink.target_component)
    while True:
        time.sleep(0.01)
        try:
            message = mavlink.recv_match(type='PARAM_VALUE', blocking=True).to_dict()
            print('name: %s\tvalue: %d' % (message['param_id'], message['param_value']))
        except Exception as error:
            print(error)
            sys.exit(0)

def moveGimball(mavlink):
    def look_at(tilt, roll=0, pan=0):
        mavlink.mav.command_long_send(
            mavlink.target_system,
            mavlink.target_component,
            mavutil.mavlink.MAV_CMD_DO_MOUNT_CONTROL,
            1,
            tilt,
            roll,
            pan,
            0, 0, 0,
            mavutil.mavlink.MAV_MOUNT_MODE_MAVLINK_TARGETING)

    while True:
        print("Move gimball")
        for angle in range(-50, 50):
            look_at(angle*100)
            time.sleep(0.01)
        for angle in range(-50, 50):
            look_at(-angle*100)
            time.sleep(0.01)


#-------------------------------------------------------------------------------


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--connect',
        dest='connection',
        action="store",
        type=str,
        default="udpout:192.168.2.1:14550",
        help="Mavlink udp address and port. eg \"127.0.0.1:4777\""
    )
    parser.add_argument(
        '-o', '--option',
        dest='option',
        action='store',
        default=0,
        help="0: print ardupilot parameters. 1: move camera gimball. 2: print raw MAVlink data"
    )
    args = parser.parse_args()


    # See https://mavlink.io/en/mavgen_python/
    os.environ['MAVLINK20'] = '1' # Set MAVLink protocol to 2.
    print("Connecting to: " + args.connection)
    mavlink = mavutil.mavlink_connection(
        args.connection,
        autoreconnect = True,
        source_system = 1,
        source_component = 93)
    print("Waiting for heartbeat")
    mavlink.wait_heartbeat()
    print("Connected!")
    print("Heartbeat from system (system %u component %u)" % (mavlink.target_system, mavlink.target_system))

    if args.option == '0':
        readPilotParameters(mavlink)
    elif args.option == '1':
        moveGimball(mavlink)
    elif args.option == '2':
        getRawMavlinkStream(mavlink)
    else:
        print("Invalid option " +str(args.option))
        exit(1)

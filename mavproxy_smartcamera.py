#!/usr/bin/env python
'''SmartCamera commands'''

import time, math
import sc_config

from pymavlink import mavutil

from sc_webcam import SmartCameraWebCam
from sc_SonyQX1 import SmartCamera_SonyQX

from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib.mp_settings import MPSetting

class SmartCameraModule(mp_module.MPModule):
    def __init__(self, mpstate):
        super(SmartCameraModule, self).__init__(mpstate, "SmartCamera", "SmartCamera commands")
        self.add_command('camtrigger', self.cmd_camtrigger, "Trigger camera")
        self.register_cameras()
    
    # register cameras - creates camera objects based on camera-type configuration
    def register_cameras(self):
        
        # initialise list
        self.camera_list = []
        
        #look for up to 2 cameras
        for i in range(0,2):
            config_group = "camera%d" % i
            camera_type = sc_config.config.get_integer(config_group, 'type', 0)
            # webcam
            if camera_type == 1:
                new_camera = SmartCameraWebCam(i)
                self.camera_list = self.camera_list + [new_camera]
            
            # Sony QX1
            if camera_type == 2:
                new_camera = SmartCamera_SonyQX(i,"eth1")
                if new_camera.boValidCameraFound() is True:
                    self.camera_list = self.camera_list + [new_camera]
                    print("Found QX Camera")

        # display number of cameras found
        print ("cameras found: %d" % len(self.camera_list))
    
    def cmd_camtrigger(self, CAMERA_FEEDBACK):
        '''Trigger Camera'''
        for cam in self.camera_list:
            cam.take_picture()
            print("Trigger Cam %s" % cam)
            print ("Latitude: %f" % CAMERA_FEEDBACK.lat)
            print ("Longitude: %f" % CAMERA_FEEDBACK.lng)
            print ("Altitude: %f" % CAMERA_FEEDBACK.alt_msl)

    def mavlink_packet(self, m):
        '''handle a mavlink packet'''
        mtype = m.get_type()
        if mtype == "CAMERA_STATUS":
            print ("Got Message camera_status")
        if mtype == "CAMERA_FEEDBACK":
            print ("Got Message camera_feedback triggering Cameras")
            self.cmd_camtrigger(m)


def init(mpstate):
    '''initialise module'''
    return SmartCameraModule(mpstate)

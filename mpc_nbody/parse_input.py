#!/usr/bin/env python3

import numpy as np


# this gives the cartesian elements and covariance


def getCovList(Els):
    ElCov = []
    covErr=""
    for El in Els:
        if El[:4]==' COV':
            ElCov.append(El)
    if len(ElCov)==7:
        junk,c11,c12,c13 = ElCov[0].split()
        junk,c14,c15,c16 = ElCov[1].split()
        junk,c22,c23,c24 = ElCov[2].split()
        junk,c25,c26,c33 = ElCov[3].split()
        junk,c34,c35,c36 = ElCov[4].split()
        junk,c44,c45,c46 = ElCov[5].split()
        junk,c55,c56,c66 = ElCov[6].split()
    if len(ElCov)!=7:
        c11,c12,c13,c14,c15,c16,c22,c23,c24,c25,c26,c33,c34,c35,c36,c44,c45,c46,c55,c56,c66="","","","","","","","","","","","","","","","","","","","",""
        covErr=' Empty covariance Matrix for '
    return covErr,c11,c12,c13,c14,c15,c16,c22,c23,c24,c25,c26,c33,c34,c35,c36,c44,c45,c46,c55,c56,c66


felfile = "../dev_data/30101.eq0_postfit"


obj={}
el = open(felfile).readlines()
cart = el.count("! Cartesian position and velocity vectors\r\n")
ept = ''

if cart>0:
    # get Cartesian Elements
    carLoc = len(el)-1 - list(reversed(el)).index('! Cartesian position and velocity vectors\n')
    carEls = el[carLoc:carLoc+25]
    car,car_x,car_y,car_z,car_dx,car_dy,car_dz = carEls[1].split()
    obj.update({'x_helio'+ept:float(car_x),'y_helio'+ept:float(car_y),'z_helio'+ept:float(car_z),
                'dx_helio'+ept:float(car_dx),'dy_helio'+ept:float(car_dy),'dz_helio'+ept:float(car_dz)})

    # Cartesian Covariance
    cart_err,sig_x,x_y,x_z,x_dx,x_dy,x_dz,sig_y,y_z,y_dx,y_dy,y_dz,sig_z,z_dx,z_dy,z_dz,sig_dx,dx_dy,dx_dz,sig_dy,dy_dz,sig_dz = getCovList(carEls)
    if cart_err=="":
        obj.update({'sigma_x_helio'+ept:sig_x,'sigma_y_helio'+ept:sig_y,'sigma_z_helio'+ept:sig_z,'sigma_dx_helio'+ept:sig_dx,
                    'sigma_dy_helio'+ept:sig_dy,'sigma_dz_helio'+ept:sig_dz})
        obj.update({'x_y_helio'+ept:x_y,'x_z_helio'+ept:x_z,'x_dx_helio'+ept:x_dx,'x_dy_helio'+ept:x_dy,'x_dz_helio'+ept:x_dz,
                    'y_z_helio'+ept:y_z,'y_dx_helio'+ept:y_dx,'y_dy_helio'+ept:y_dy,'y_dz_helio'+ept:y_dz,'z_dx_helio'+ept:z_dx,
                    'z_dy_helio'+ept:z_dy,'z_dz_helio'+ept:z_dz,'dx_dy_helio'+ept:dx_dy,'dx_dz_helio'+ept:dx_dz,'dy_dz_helio'+ept:dy_dz})


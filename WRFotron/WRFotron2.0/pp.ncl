load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRFUserARW.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRF_contributed.ncl"

if (.not. isvar("wrffilename")) then
    print("parameter wrffilename missing")
    exit
end if

if (.not. isvar("outputfilename")) then
    print("parameter outputfilename missing")
    exit
end if

filein = addfile(wrffilename, "r")
fileout = addfile(outputfilename, "c")

time = 0

Times = filein->Times
fileout->timestamp = filein->XTIME
fileout->timestamp = (/ tofloat(wrf_times_c(Times, 1)) /)
fileout->timestamp@units = "hours since 1901-01-01 00:00:00"
fileout->timestamp@description = "hours since 1901-01-01 00:00:00"

fileout->Times   = filein->Times
fileout->pres    = wrf_user_getvar(filein,"p",time)          ; full model pressure (Pa)
fileout->p_sl    = wrf_user_getvar(filein,"slp",time)        ; Sea level pressure (hPa)
fileout->rh_2m   = wrf_user_getvar(filein,"rh2",time)        ; relative humidity at 2m (%)
fileout->rh      = wrf_user_getvar(filein,"rh",time)         ; relative humidity (%)
fileout->terrain = wrf_user_getvar(filein,"ter",time)        ; terrain height (m)
fileout->td_2m   = wrf_user_getvar(filein,"td2",time)
fileout->td_2m   = (/ fileout->td_2m /) +273.15              ; dew point temperature at 2m (K)
fileout->td      = wrf_user_getvar(filein,"td",time)
fileout->td      = (/ fileout->td /) +273.15                 ; dew point temperature (K)
fileout->tk      = wrf_user_getvar(filein,"tk",time)         ; temperature (K)
fileout->th      = wrf_user_getvar(filein,"th",time)         ; potential temperature (K)
fileout->z       = wrf_user_getvar(filein,"z",time)          ; full model height (m)

; rotate winds to earth coordinates
fileout->u_ll_10m = filein->T2
fileout->v_ll_10m = filein->T2
fileout->u_ll     = filein->T
fileout->v_ll     = filein->T

uvmet           = wrf_user_getvar(filein,"uvmet",time)       ; U and V components of wind rotated to earth coordinates (m/s)
uvmet10         = wrf_user_getvar(filein,"uvmet10",time)     ; 10m U and V components of wind rotated to earth coordinates (m/s)

fileout->u_ll_10m   = (/ uvmet10(0,:,:) /)
fileout->v_ll_10m   = (/ uvmet10(1,:,:) /)

fileout->u_ll       = (/ uvmet(0,:,:,:) /)
fileout->v_ll       = (/ uvmet(1,:,:,:) /)

fileout->w_ll       = wrf_user_getvar(filein,"wa",time)       ; W component of wind on mass points (m/s)

; layer thickness
terrain             = fileout->terrain

ph                  = filein->PH
phb                 = filein->PHB
altitude            = (ph + phb)/9.81

dimsies = dimsizes(altitude)
i = 0
do while (i .lt. dimsies(1))
  altitude(0,i,:,:) = altitude(0,i,:,:) - terrain
  i = i + 1
end do

fileout->dz      = fileout->u_ll
i = 0
do while (i .lt. (dimsies(1)-1))
  fileout->dz(0,i,:,:) = altitude(0,i+1,:,:) - altitude(0,i,:,:)
  i = i + 1
end do
fileout->dz@units = "m"

alt    = filein->ALT
dz     = fileout->dz

; cloud water/ice path
; QCLOUD in kg kg-1, ALT in m3 kg-1, dz in m, *1e3 --> CLWP in g m-2
qcloud = filein->QCLOUD
qice   = filein->QICE

; variables need a blueprint to copy atts, use landmask
clwp = dim_sum_n(qcloud / alt / dz * 1e3, 1);
copy_VarMeta(filein->LANDMASK, clwp);
clwp@units = "g m-2"
clwp@description = "cloud liquid water path"
fileout->CLWP = clwp

cip  = dim_sum_n(qice / alt / dz   * 1e3, 1)
copy_VarMeta(filein->LANDMASK, cip)
cip@units = "g m-2"
cip@description = "cloud ice path"
fileout->CIP = cip

; water vapour column
; QVAPOR in kg kg-1, ALT in m3 kg-1, dz in m, rho_water = 1000 kg m-3, to cm --> H2O in cm3 cm-2
qvapor = filein->QVAPOR
h2o  = dim_sum_n(qvapor / alt / dz / 1000.0 * 1e2, 1);
copy_VarMeta(filein->LANDMASK, h2o)
h2o@units = "cm3 cm-2"
h2o@description = "water vapour column"
fileout->H2O = h2o

; wind speed and direction
u_ll_10m  = fileout->u_ll_10m
v_ll_10m  = fileout->v_ll_10m
u_ll      = fileout->u_ll
v_ll      = fileout->v_ll

wspeed_10m = sqrt( fileout->u_ll_10m*fileout->u_ll_10m + fileout->v_ll_10m*fileout->v_ll_10m )
copy_VarMeta(filein->LANDMASK, wspeed_10m)
wspeed_10m@units = "m s-1"
wspeed_10m@description = "wind speed at 10m"
fileout->wspeed_10m = wspeed_10m

wspeed     = sqrt( fileout->u_ll*fileout->u_ll         + fileout->v_ll*fileout->v_ll )
copy_VarMeta(filein->T, wspeed)
wspeed@units = "m s-1"
wspeed@description = "wind speed"
fileout->wspeed = wspeed

r2d = 45.0/atan(1.0)     ; conversion factor (radians to degrees)

wdir_10m = atan2( fileout->u_ll_10m, fileout->v_ll_10m ) * r2d + 180.0
copy_VarMeta(filein->LANDMASK, wdir_10m)
wdir_10m@units = "degrees"
wdir_10m@description = "wind direction at 10m"
fileout->wdir_10m = wdir_10m

wdir     = atan2( fileout->u_ll, fileout->v_ll )         * r2d + 180.0
copy_VarMeta(filein->T, wdir)
wdir@units = "degrees"
wdir@description = "wind direction"
fileout->wdir = wdir

; AODs (Dominik email)
;Step 1: Computation of Angstrom exponent  alpha (AOD1-AOD2):
;alpha = - ln(AOD1/AOD2)/ln(lambda1/lambda2)
; 
;Step 2:  Computation of AOD at wavelength lambda:
;AOD = AOD1* (lambda/lambda1)^(-alpha)
; input: TAUAER1, 2, 3, 4 @ 300, 400, 600, 1000 nm

; at 470 nm from 400 and 600 nm
tauaer2  = filein->TAUAER2
tauaer3  = filein->TAUAER3
tauaer4  = filein->TAUAER4

;NOTE: using dim_sum_n_Wrap as want to sum up all the values for every level in the atmospheric column dim2

fileout->AOD470 = tauaer2
alpha = - log( tauaer2 / tauaer3 ) / log( 400.0 / 600.0 )
fileout->AOD470 = (/ tauaer2 * ( 470.0 / 600.0 )^(-alpha) /)
fileout->AOD470_sfc = dim_sum_n_Wrap(fileout->AOD470, 1)

; at 550 nm from 400 and 600 nm
fileout->AOD550 = tauaer2
alpha = - log( tauaer2 / tauaer3 ) / log( 400.0 / 600.0 )
fileout->AOD550 = (/ tauaer2 * ( 550.0 / 600.0 )^(-alpha) /)
fileout->AOD550_sfc = dim_sum_n_Wrap(fileout->AOD550, 1)

; at 675 nm from 600 and 1000 nm
fileout->AOD675 = tauaer3
alpha = - log( tauaer3 / tauaer4 ) / log( 600.0 / 1000.0 )
fileout->AOD675 = (/ tauaer3 * ( 675.0 / 1000.0 )^(-alpha) /)
fileout->AOD675_sfc = dim_sum_n_Wrap(fileout->AOD675, 1)

delete(filein)
delete(fileout)

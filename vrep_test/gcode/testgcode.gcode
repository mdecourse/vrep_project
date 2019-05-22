G0 F9000 X353.279 Y229.659
G1 F3000 X354.659 Y228.279 E165.68829
G0 F9000 X354.659 Y228.845
G1 F3000 X353.844 Y229.659 E165.70273
G0 F9000 X354.410 Y229.659
G1 F3000 X354.659 Y229.410 E165.70715
G0 F9000 X353.800 Y228.800
M107
G1 F2400 E161.20715
G0 F9000 X353.800 Y228.800 Z15.000
;End GCode
M104 S0                     ;extruder heater off
M140 S0                     ;heated bed heater off (if you have it)
G91                                    ;relative positioning
G1 E-1 F300                            ;retract the filament a bit before lifting the nozzle, to release some of the pressure
G1 Z+0.5 E-5 X-20 Y-20 F9000 ;move Z up a bit and retract filament even more
G28 X0 Y0                              ;move X/Y to min endstops, so the head is out of the way
M84                         ;steppers off
G90                         ;absolute positioning
;CURA_PROFILE_STRING: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

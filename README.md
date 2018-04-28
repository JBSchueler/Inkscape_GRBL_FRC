# Inkscape_GRBL_FRC
Inkscape GRBL Feed Rate Control

_This project is based on the "Raster 2 Laser GCode generator"_
https://github.com/305engineering/Inkscape



## Installing:

Simply copy all the files in the folder "Extensions" of Inkscape

- Windows ) "C:\<...>\Inkscape\share\extensions"

- Linux ) "/usr/share/inkscape/extensions"

- Mac ) "/Applications/Inkscape.app/Contents/Resources/extensions"


for unix (& mac maybe) change the permission on the file:

`chmod 755` for all the *.py files

`chmod 644` for all the *.inx files



## Usage of "GRBL VFRC":

[Required file: png.py / grbl_vfrc.inx / grbl_vfrc.py]

1. Resize the inkscape document to match the dimension of your working area on the laser cutter/engraver (Shift+Ctrl+D)
2. Step 2) Draw or import the image
3. Step 3) To run the extension go to: Extension > GRBL Laser > GRBL Laser Variable Feed Rate Control
4. Step 4) Play!


## How To Set Laser Cut Values:
1. Import "GREY_TEST.png" into InkScape as mentioned at Usage of "GRBL VFRC" (size 5 x 30mm)
2. Set Gamma Correction  Y=1
3. Set "Feed Rate for White" to maximum Feed Rate of CNC Machine
3. Set "Feed Rate for Black" to 1/4 of White Feed Rate of CNC Machine
4. Set "Laser Power" to a value, e.g. 32.
5. Hit "Apply"

Check the black, grey and white.
- If White is a bit grey, lower the value of "Laser Power" until it is white.
- If White is white (and other too) increase "Laser Power" until only white is just a bit grey, than lower the value until it is white.

Now "Feed Rate for White" and "Laser Power" are set.

If black is way too black (burned) increase the value of "Feed Rate for Black" until black is the kind of black you want.
If black is too grey, lower the "Feed Rate for Black" until black is the kind of black you want.


Now the values are set to be able to print pictures.
Be aware these settings are different for other type of materials.
Better to write down these settings for a next time.

To increase sharpness, try Y=2 or Y=3.

_Note_
_I have created all the file except for png.py , see that file for details on the license_



'''
# ----------------------------------------------------------------------------
# Copyright (C) 2014 305engineering <305engineering@gmail.com>
# Original concept by 305engineering.
# Modified by JBSchueler (2018)
#   Stripped and removed unneeded code to only support Variable Feed Rate Control
#   Output extention changed to ".nc"
#   Matrax changed to float, GRB2Y conversion has more than 255 greyscales, so maximum
#   of greyscales is delta of feed rate. Image will be in High Quality Lasered!!!
#
# "THE MODIFIED BEER-WARE LICENSE" (Revision: my own :P):
# <305engineering@gmail.com> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff (except sell). If we meet some day, 
# and you think this stuff is worth it, you can buy me a beer in return.
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------------------------------
'''


import sys
import os
import re

sys.path.append('/usr/share/inkscape/extensions')
sys.path.append('/Applications/Inkscape.app/Contents/Resources/extensions')

import subprocess
import math

import inkex
import png
import array


class GcodeExport(inkex.Effect):

######## 	Invoked by _main()
	def __init__(self):
		"""init the effect library and get options from gui"""
		inkex.Effect.__init__(self)

		# Image export options
		self.OptionParser.add_option("-d", "--directory",action="store", type="string", dest="directory", default="/home/",help="Directory for files") ####check_dir
		self.OptionParser.add_option("-f", "--filename", action="store", type="string", dest="filename", default="-1.0", help="File name")
		self.OptionParser.add_option("","--add-numeric-suffix-to-filename", action="store", type="inkbool", dest="add_numeric_suffix_to_filename", default=True,help="Add numeric suffix to filename")
		self.OptionParser.add_option("","--bg_color",action="store",type="string",dest="bg_color",default="",help="")
		self.OptionParser.add_option("","--resolution",action="store", type="int", dest="resolution", default="5",help="") #Use the value on float (xy) / resolution and a case for the DPI of the export

		# Gamma correction on greyscale
		self.OptionParser.add_option("","--grayscale_gamma",action="store", type="int", dest="grayscale_gamma", default="4",help="Increase gamma for sharpeness")

		# Feed rate Black(minimum) and White(maximum)
		self.OptionParser.add_option("","--feedmax",action="store", type="int", dest="feedmax", default="1000",help="maximum feed rate (White)")
		self.OptionParser.add_option("","--feedmin",action="store", type="int", dest="feedmin", default="200",help="minimum feed rate (Black)")

		# Commands
		self.OptionParser.add_option("","--laseron", action="store", type="string", dest="laseron", default="M03", help="M03")
		self.OptionParser.add_option("","--laseroff", action="store", type="string", dest="laseroff", default="M05", help="M04")
		self.OptionParser.add_option("","--laserpowerwhite",action="store", type="int", dest="laserpowerwhite", default="1",help="max 255")
		self.OptionParser.add_option("","--laserpowerblack",action="store", type="int", dest="laserpowerblack", default="1",help="max 255")

		# Preview = BW image only
		self.OptionParser.add_option("","--preview_only",action="store", type="inkbool", dest="preview_only", default=False,help="")

		# inkex.errormsg ("BLA BLA BLA Message to display") #DEBUG




######## 	Call back from __init __()
########	Everything takes place here
	def effect(self):

		current_file = self.args[-1]
		bg_color = self.options.bg_color

		## Implement check_dir

		if (os.path.isdir(self.options.directory)) == True:

			## CODE IF THE DIRECTORY EXISTS
			#  inkex.errormsg ("OK") #DEBUG

			#   Add a suffix to the filename to not overwrite files
			if self.options.add_numeric_suffix_to_filename :
				dir_list = os.listdir(self.options.directory) # List of all files in the working directory
				temp_name =  self.options.filename
				max_n = 0
				for s in dir_list :
					r = re.match(r"^%s_0*(\d+)%s$"%(re.escape(temp_name),'.png' ), s)
					if r :
						max_n = max(max_n,int(r.group(1)))
				self.options.filename = temp_name + "_" + ( "0"*(4-len(str(max_n+1))) + str(max_n+1) )

			#   Create the file paths to use
			suffix = "_VFRC_"

			pos_file_png_exported = os.path.join(self.options.directory,self.options.filename+".png")
			pos_file_png_BW = os.path.join(self.options.directory,self.options.filename+suffix+"preview.png")
			pos_file_gcode = os.path.join(self.options.directory,self.options.filename+suffix+"gcode.nc")

			#   Export the image to PNG
			self.exportPage(pos_file_png_exported,current_file,bg_color)

			#   TO DO
			#   Manipulate the PNG image to generate the Gcode file
			self.PNGtoGcode(pos_file_png_exported,pos_file_png_BW,pos_file_gcode)

		else:
			inkex.errormsg("Directory does not exist! Please specify existing directory!")


########	EXPORT THE IMAGE IN PNG
######## 	Call back from effect()

	def exportPage(self,pos_file_png_exported,current_file,bg_color):
		######## CREATION OF PNG FILES ########
		# Create the image inside the folder indicated by "pos_file_png_exported"
		#-d 127 = resolution 127DPI => 5 pixels / mm 1pixel = 0.2mm
		### command="inkscape -C -e \"%s\" -b\"%s\" %s -d 127" % (pos_file_png_exported,bg_color,current_file)

		DPI = 25.4 * self.options.resolution

		command="inkscape -C -e \"%s\" -b\"%s\" %s -d %s" % (pos_file_png_exported,bg_color,current_file,DPI) # Command line command to export to PNG

		p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		return_code = p.wait()
		f = p.stdout
		err = p.stderr


########	CREATE IMAGE IN B / W AND THEN GENERATE GCODE
######## 	Call back from effect()

	def PNGtoGcode(self,pos_file_png_exported,pos_file_png_BW,pos_file_gcode):

		######## GENERATE IMAGE IN GRAY SCALE ########
		# Scan the image and make it become a matrix composed of list

		# Gamma Correction setting
		if self.options.grayscale_gamma == 1:
			Gamma = 4.0
		elif self.options.grayscale_gamma == 2:
			Gamma = 3.0
		elif self.options.grayscale_gamma == 3:
			Gamma = 2.0
		elif self.options.grayscale_gamma == 4:
			Gamma = 1.0
		elif self.options.grayscale_gamma == 5:
			Gamma = 1.0/2.0
		elif self.options.grayscale_gamma == 6:
			Gamma = 1.0/3.0
		elif self.options.grayscale_gamma == 7:
			Gamma = 1.0/4.0
		else:
			Gamma = 1.0


		reader = png.Reader(pos_file_png_exported) # PNG file generated

		w, h, pixels, metadata = reader.read_flat()

		WhiteColor=255.0		##	WHITE
		BlackColor=0.0 			##	BLACK

		matrix = [[WhiteColor for i in range(w)]for j in range(h)]  # List instead of an array

		# Write a new image in Grayscale 8bit pixel-by-pixel copy

		# Y = 0.299R + 0.587G + 0.114B
		for y in range(h): # y varies from 0 to h-1
			for x in range(w): # x varies from 0 to w-1
				pixel_position = (x + y * w)*4 if metadata['alpha'] else (x + y * w)*3
				matrix[y][x] = pixels[pixel_position]*0.299 + pixels[(pixel_position+1)]*0.587 + pixels[(pixel_position+2)]*0.114


		#### Matrix time contains the grayscale image


		######## GENERATE BLACK AND WHITE IMAGE ########
		# Scan matrix and generate matrix_BW
		matrix_BW = [[WhiteColor for i in range(w)]for j in range(h)]

		matrix_BW = matrix


		#### Now matrix_BW contains the image in White(255) and Black(0)


		#### SAVE IMAGE IN BLACK AND WHITE ####
		file_img_BW = open(pos_file_png_BW, 'wb')				# Create the file
		New_img = png.Writer(w, h, greyscale=True, bitdepth=8)	# Setting up the image file
		New_img.write(file_img_BW, matrix_BW)					# Constructor of the image file
		file_img_BW.close()										# Close the file


		#### GENERATE THE GCODE FILE ####
		if self.options.preview_only == False: # Generate Gcode only if needed

			# PNG Y-Axis is top to bottom, Laser Y-Axis is bottom to top			
			matrix_BW.reverse()

			Laser_ON = False
			F_G01 = self.options.feedmax
			Scale = self.options.resolution

			file_gcode = open(pos_file_gcode, 'w')  # I create the file

			# Initial Gcode standard configurations
			# HOMING
			file_gcode.write('G00X0Y0; home X\n')
			file_gcode.write('$H; home all axes\n')
			file_gcode.write('G21; Set units to millimeters\n')
			file_gcode.write('G90; Use absolute coordinates\n')
			file_gcode.write('G92; Coordinate Offset\n')

			# Creation of the Gcode

			# Enlarge the matrix 1 pixel to work on the whole image
			for y in range(h):
				matrix_BW[y].append(WhiteColor)
			w = w+1

			## Grey Scale FRC single direction
			file_gcode.write('G01 F' + str(F_G01) + ' S' + str(self.options.laserpowerblack) + '\n')
			file_gcode.write(self.options.laseron + '\n')
			Fdelta=float(self.options.feedmax - self.options.feedmin)
			Sdelta=float(self.options.laserpowerwhite - self.options.laserpowerblack)
			Pdiv= WhiteColor**Gamma
			for y in range(h):
				file_gcode.write('G00X0Y' + str(round(float(y)/Scale,2)) +'\n')
				file_gcode.write('G01')
				for x in range(w):
					Xt=round(float(x+1)/Scale,2)
					Pt=float(matrix_BW[y][x])**Gamma
					Ft=int(((Pt * Fdelta) / Pdiv) + self.options.feedmin)
					St=int(((Pt * Sdelta) / Pdiv) + self.options.laserpowerblack)
					# file_gcode.write('X' + str(Xt) + 'F' + str(Ft) + 'S' + str(St) + '\n')
					file_gcode.write('X' + str(Xt) + 'F' + str(Ft) + '\n')

			file_gcode.write(self.options.laseroff + '\n')
## End Grey Scale FRC single direction


			# Gcode standard final configurations
			# HOMING
			file_gcode.write('G00X0Y0; home X\n')
			file_gcode.write('$H; home all axes\n')

			file_gcode.close() # Close the file


######## 	######## 	######## 	######## 	######## 	######## 	######## 	######## 	########


def _main():
	e=GcodeExport()
	e.affect()

	exit()

if __name__=="__main__":
	_main()

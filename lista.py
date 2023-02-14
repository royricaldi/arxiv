from zipfile import ZipFile
import datetime
import tarfile
import re
from TexSoup import TexSoup


#############################################################################
#############################################################################
# CREATING THE FIRST LIST
#############################################################################
#############################################################################


# specifying the TAR file name
file_name = "CSM.tar"
  
def print_all():   # opening the zip file in READ mode
	with tarfile.TarFile(file_name, 'r') as tar:
		rist=tar.getmembers() # getting all the contents of the zip file
		print(rist)

def get_images():
	lista= []
	with tarfile.TarFile(file_name, 'r') as archive:
		for filename in archive.getnames():
			if ".png" in filename:
				lista.append(filename.replace(".png", ""))
			if ".jpg" in filename:
				lista.append(filename.replace(".jpg", ""))
			if ".eps" in filename:
				lista.append(filename.replace(".eps", ""))
			if ".jpeg" in filename:
				lista.append(filename.replace(".jpeg", ""))
			if ".pdf" in filename:
				lista.append(filename.replace(".pdf", ""))
		return lista		


print("FIRST PART OF THE PROGRAM, PARSING THE .TAR FILE ")
#print("All the elements inside the tar file:")
#print_all()
#print("_______________________________________________________________")
print("Just the list of the images present on the tar")
lista= get_images()
print(lista)
#############################################################################
#############################################################################
# CREATING THE SECOND LIST
#############################################################################
#############################################################################


def extracting(name,lista2):
	with open( str(name+".tex") ) as f:
		sopa = f.read()
	for item in sopa.split("\n"):
		if "includegraphics" in item:
			lista2.append(item)
	return(lista2)


####################################################################################
# Extracting the list from the main 
##################################################################################

name="main"
lista2=[]
lista2= extracting(name,lista2)


####################################################################################
# Extracting the list from the other tex files  
##################################################################################

with open("main.tex") as f:
	soup = TexSoup(f)

sections= soup.find_all('input')
for i in range (len(sections)):
	sec= str(sections[i])
	sec= sec.replace("\input{", "")
	sec= sec.replace("}", "")
	lista2=extracting(sec,lista2)
print("............Second list, images that were used...............")
print(lista2)

#############################################################################
#############################################################################
# COMPARISON BETWEEN THE TWO LISTS
#############################################################################
#############################################################################

lista.sort(reverse=True, key=len)

size=len(lista)

listafinal=lista



for j in (lista2):
	for i in (lista):
		if i in j:
			listafinal.remove( i )
#print(listafinal)
print("Images that were not used:", len(listafinal))
counter= (len(listafinal)*100)/size
print("Percentage of images were not used",counter)
	
	
	
	
	

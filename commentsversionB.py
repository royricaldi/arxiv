import re
from TexSoup import TexSoup

count=0
seccount=0
def numbers(name,count,seccount):
	with open(str(name+".tex")) as f:
		text = f.read()
		for item in text.split("\n"):
			seccount=seccount+1
			if len(item)>2 :
				if (item.strip()[0]) == "%":
					count=count+1 
	return(count,seccount)


name="main"
count,seccount= numbers(name,count,seccount)

with open("main.tex") as f:
	soup = TexSoup(f)

sections= soup.find_all('input')
for i in range (len(sections)):
	sec= str(sections[i])
	sec= sec.replace("\input{", "")
	sec= sec.replace("}", "")
	count,seccount= numbers(sec,count,seccount)


print("Total number of lines",seccount )
print("number of lines commented",count)
c= (count*100)/seccount
print("Percentage of commented lines", c)


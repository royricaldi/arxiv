import re
from TexSoup import TexSoup

count=0
seccount=0
text2=[] 
def numbers(name,count,seccount,text2):
	with open(str(name+".tex")) as f:
		text = f.read()
		for item in text.split("\n"):
			seccount=seccount+1
			if len(item)>2 :
				if (item.strip()[0]) == "%":
					count=count+1 
					text2.append(item)
	return(count,seccount,text2)


name="main"
count,seccount,text2= numbers(name,count,seccount,text2)

with open("main.tex") as f:
	soup = TexSoup(f)

sections= soup.find_all('input')
for i in range (len(sections)):
	sec= str(sections[i])
	sec= sec.replace("\input{", "")
	sec= sec.replace("}", "")
	count,seccount,text2= numbers(sec,count,seccount,text2)


print("Total number of lines",seccount )
print("number of lines commented",count)
c= (count*100)/seccount
print("Percentage of commented lines", c)
#print(text2) #all the lines which are comments

import matplotlib.pyplot as plt

file = open("./train.txt", "r")
y=[]
strings = file.readlines()
for line in strings:
    left = line.find('FGD')
    if left != -1:
        right = line.find(',', left)
        y.append(float(line[left+4:right]))
file.close()
x = list(range(0, 99))

plt.plot(x,y)
plt.show()
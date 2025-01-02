f = open("C:/Users/Kylie/Documents/College/C950 Data Structures and Algorithms II/csv WGUPS Distance Table.csv")
counter = 0
address_list = []
for x in f:
    
    line = x.split(",")
    address_list.append(line.pop(0))
    output = ','.join(str(y) for y in line)
    output = output.strip()
    output = "["+ output +"],"
    print(output)
address_list = "\r\n".join(str(y) for y in address_list)
print(address_list)
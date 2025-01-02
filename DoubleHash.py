


class TableNode:
    def __init__(self):
        self.key = None
        self.value = None
        self.emptySinceStart = True
        self.emptyAfterRemove = False
        ve = False




def DoubleHash(key,i,N):
    def h1(key: int):
        return key % 11

    def h2(key: int):
        return 5 - key % 5
    
    bucket = (h1(key) + i * h2(key)) % N

    return bucket



def HashInsert(hash_table,key):
    i = 0
    buckets_probed = 0

    bucket = DoubleHash(key,i,len(hash_table))
    print(str(bucket))
    while (buckets_probed < len(hash_table)):
        if hash_table[bucket].emptySinceStart is True or hash_table[bucket].emptyAfterRemove is True:
            print(str(bucket))
            hash_table[bucket].key = key
            hash_table[bucket].emptySinceStart = False
            hash_table[bucket].emptyAfterRemove = False
            return True
        i += 1
        bucket = DoubleHash(key,i,len(hash_table))
        print(str(bucket))
    return False


def HashRemove(hashTable, key):
    i = 0
    bucketsProbed = 0

#    // Hash function determines initial bucket
    N = len(hashTable)
    bucket = DoubleHash(key,i,N)
    print(str(bucket))

    while ((hashTable[bucket].emptySinceStart is not True) and (bucketsProbed < N)):
        
        if ((not hashTable[bucket].emptySinceStart and not hashTable[bucket].emptyAfterRemove) and (hashTable[bucket].key == key)):
            hashTable[bucket].key = None
            hashTable[bucket].value = None
            hashTable[bucket].emptyAfterRemove = True 
            return True
        

        # // Increment i and recompute bucket index
        # // c1 and c2 are programmer-defined constants for quadratic probing
        i = i + 1
        bucket = DoubleHash(key,i,N)
        print(str(bucket))

        # // Increment number of buckets probed
        bucketsProbed = bucketsProbed + 1
    return False # key not found


def HashSearch(hashTable, key):
    i = 0
    bucketsProbed = 0
    N = len(hashTable)
#    // Hash function determines initial bucket
    bucket = DoubleHash(key,i,N)
    print(str(bucket))
    while ((not hashTable[bucket].emptySinceStart) and (bucketsProbed < N)):
        if ((not hashTable[bucket].emptySinceStart and not hashTable[bucket].emptyAfterRemove) and (hashTable[bucket].key == key)):
            return hashTable[bucket]
      

        #   // Increment i and recompute bucket index
        #   // c1 and c2 are programmer-defined constants for quadratic probing
        i = i + 1
        bucket = DoubleHash(key,i,N)
        print(str(bucket))
        bucketsProbed = bucketsProbed + 1
    return False
    #   // Increment number of buckets probed
     




def main():
    h_size = 11
    hash_table = []
    for i in range(h_size):
        hash_table.append(TableNode())
    key = input("Enter next key: ")
    while (True and key != "x"):
        if key[0] != "!" and key[0] != "?":
            HashInsert(hash_table,int(key))
        if key[0] == "!":
            key = key.lstrip('!')
            HashRemove(hash_table,int(key))
        if key[0] == "?":
            key = key.lstrip('?')
            HashSearch(hash_table,int(key))
        count = 0
        for item in hash_table:
            print(str(count) + " " + str(item.key))
            count +=1
    
        key = input("Enter next key: ")
    
    return 0

if __name__ =="__main__":
    main()
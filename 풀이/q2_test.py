import q2_source as p2


# 각 블록은 Block ID와 이전 블록의 해시값, 그리고 블록 데이터로 구성됨
num_blocks = 10
for _ in range(num_blocks):
    temp = p2.Block()
    temp.initialize_block()
    p2.blockchain.append(temp)

# 1. Block ID
print("1.")
Block_ID = p2.blockchain[1].block_id
print(Block_ID)
print()

# 2. 이전 블록의 해시값
print("2.")
Pre_Block_Hash = p2.blockchain[1].hash_previous_block
print(Pre_Block_Hash)
print()

# 3. Block Data
print("3.")
Block_Data = p2.blockchain[1].block_data
for i in range(5):
    print(f'Block Data{i+1}: {Block_Data[i]}')
print()

# 4. Hashed result
print("4.")
Merkel_Result = p2.merkel_tree[1][13][0]
print(Merkel_Result)
print()

# 특정 Transaction 값이 위변조 되었는지 여부를 빠르게 검증
# 위조되었으면 0 출력, 위조되지 않았으면 1 출력
print("5.")
p2.forgery_or_not(1, 1)
#print(p2.blockchain[1].block_data[1 - 1])
p2.change_block(1, 1)
p2.forgery_or_not(1, 1)
#p2.blockchain[1].block_data[1 - 1]

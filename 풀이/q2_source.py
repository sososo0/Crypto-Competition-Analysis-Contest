import hashlib
import random
import base58

num_blocks = 10
bytes_hash = 20
block_id_counter = 0
index_merkel_tree = 0
blockchain = []  # one-dimensional
merkel_tree = []  # three-dimensional


class Block:

    def __init__(self):
        self.block_id = ''
        self.hash_previous_block = ''
        self.block_data = []

    @staticmethod
    def padding(trans, num):
        trans_str = str(trans)

        if len(trans_str) < num:
            trans_str_padded = '0' * (num - len(trans_str)) + trans_str
        else:
            trans_str_padded = trans_str[-1 * num:]

        return trans_str_padded

    def set_block_id(self):
        global block_id_counter

        self.block_id = self.padding(block_id_counter, 20)
        self.block_id = str(base58.b58encode(self.block_id))[2:-1]

    '''
    #block_id가 16진수라면...
    def set_block_id(self):
        global block_id_counter
        counter = '{0:x}'.format(block_id_counter) # 16진수로 변환
        self.block_id = '0' * (40 - len(str(counter))) + str(counter) #160비트를 16진수로 표현하면 40필요
        block_id_counter += 1
    '''

    @staticmethod
    def transaction():
        trans = random.randrange(1, 10 * 99)
        trans = Block.padding(trans, 108)

        return trans

    def set_block_data(self):
        for i in range(2 ** 13):
            tx_id = self.padding(i + 1, 20)
            trans = self.transaction()

            temp = str(base58.b58encode(tx_id + trans))[2:-1]

            self.block_data.append(temp)

    def set_merkel_tree(self):
        global merkel_tree
        global index_merkel_tree
        num_iter = 2 ** 13
        row = 0

        merkel_tree.append([])

        while num_iter >= 1:
            merkel_tree[index_merkel_tree].append([])
            if row == 0:
                for i in range(num_iter):
                    merkel_tree[index_merkel_tree][row].append(self.make_hash(self.block_data[i]))
            else:
                for i in range(num_iter):
                    merkel_tree[index_merkel_tree][row].append \
                        (self.make_hash(merkel_tree[index_merkel_tree][row - 1][2 * i]
                                        + merkel_tree[index_merkel_tree][row - 1][2 * i + 1]))

            num_iter //= 2
            row += 1

        index_merkel_tree += 1

    @staticmethod
    def make_hash(test):
        s = hashlib.sha3_256()
        s.update(bytes(test, 'utf-8'))
        full_hash = s.hexdigest()
        new_hash = full_hash[-20:]
        new_hash = str(base58.b58encode(new_hash))[2:-1]

        return new_hash

    def set_hash_value(self):
        global block_id_counter
        global blockchain
        global merkel_tree

        if block_id_counter == 0:
            self.hash_previous_block = self.make_hash('0' * 20)
        else:
            self.hash_previous_block \
                = self.make_hash(blockchain[block_id_counter - 1].block_id
                                 + blockchain[block_id_counter - 1].hash_previous_block
                                 + merkel_tree[block_id_counter - 1][13][0])

    def initialize_block(self):
        global block_id_counter

        self.set_block_id()
        self.set_block_data()
        self.set_merkel_tree()
        self.set_hash_value()

        block_id_counter += 1


def find_address(tx_id):
    lt2 = []

    if tx_id % 2 == 0:
        tx_id_result = tx_id + 1
        lt2.append(tx_id_result)
    else:
        tx_id_result = tx_id - 1
        lt2.append(tx_id_result)

    tx_id_next = tx_id // 2
    lt2.append(tx_id_next)

    return lt2


def select_from_tree(id_block, tx_id):
    row_merkel = 0
    list_hash = list()

    # 위변조 의심되는 값 추가
    list_hash.append(merkel_tree[id_block][row_merkel][tx_id])

    # 머클트리에서 필요한 값들 추출
    for _ in range(13):
        tx_id_result, tx_id_next = find_address(tx_id)
        list_hash.append(merkel_tree[id_block][row_merkel][tx_id_result])

        tx_id = tx_id_next
        row_merkel += 1

    return list_hash


def change_block(id_block, tx_id):
    tx_id -= 1
    temp = Block.transaction()

    while temp == blockchain[id_block].block_data[tx_id][20:]:
        temp = Block.transaction()

    blockchain[id_block].block_data[tx_id] = str(base58.b58encode(Block.padding(tx_id + 1, 20) + temp))[2:-1]


'''
forgery_or_not(id_block, tx_id):
    takes id_block, tx_id as input.
    list_hash: output of select_from_tree(id_block, tx_id)
    new_hash: combined hashed result of the altered transaction and list_hash[1:]
    original_hash: combined hashed result of list_hash[:]

    why this way? 
    The hash value in the next block in the blockchain took as one of the inputs the transactions in order.
    However, we cannot presume that the order of the transactions will be respected the same way 
    while new_hash is being made. 
    Therefore it is necessary to make a new hash value that follows the same order as new_hash,
    but only takes the original hash values in the merkel tree. 

    Because the question asked if it can be shown when a transaction in a block has been altered, 
    it seems that it would suffice if we only hash the transactions, 
    leaving out the block_id and hash_previous_block.
'''


def forgery_or_not(id_block, tx_id):
    tx_id -= 1
    list_hash = select_from_tree(id_block, tx_id)

    new_hash = Block.make_hash(blockchain[id_block].block_data[tx_id])
    for i in range(1, len(list_hash)):
        new_hash = Block.make_hash(new_hash + list_hash[i])

    original_hash = list_hash[0]
    for i in range(1, len(list_hash)):
        original_hash = Block.make_hash(original_hash + list_hash[i])

    if new_hash == original_hash:
        print("blockchain[].block_data[]: not changed".format(id_block, tx_id))
    else:
        print("blockchain[].block_data[]: changed".format(id_block, tx_id))

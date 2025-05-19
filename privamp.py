import numpy as np
from Crypto.Random import get_random_bytes
from Crypto.Hash import HMAC, SHA256

def generate_random_matrix(rows, cols):
    return np.random.randint(0, 2, (rows, cols))

def generate_hash_family(output_length, key_length, family_size):
    return [generate_random_matrix(output_length, key_length) for _ in range(family_size)]

def universal_hash_with_index(weak_key, H):
    weak_key_vector = np.array([int(bit) for bit in weak_key])
    hashed_key_vector = np.mod(H @ weak_key_vector, 2)
    return hashed_key_vector.astype(int)

def secure_hash_using_hmac(key, data):
    h = HMAC.new(key, digestmod=SHA256)
    h.update(data)
    return h.hexdigest()

class PrivAmp:
    def __init__(self):
        pass
    def univ2(self,params, final_key_length=32,family_size = 256):
        akey = params['akey']
        bkey = params['bkey']
        key_length = len(akey)
        hash_family = generate_hash_family(final_key_length, key_length, family_size)
        
        chosen_hash_index = np.random.randint(0, family_size - 1)
        print(f"Alice's chosen hash index: {chosen_hash_index}")

        hash_func = hash_family[chosen_hash_index]
        ahash_key = universal_hash_with_index(akey, hash_func)
        bhash_key = universal_hash_with_index(bkey, hash_func)
        return {'akey': ahash_key, 'bkey': bhash_key}
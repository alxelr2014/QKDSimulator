import numpy as np


def generate_random_matrix(rows, cols):
    return np.random.randint(0, 2, (rows, cols))

def generate_hash_family(output_length, key_length, family_size):
    return [generate_random_matrix(output_length, key_length) for _ in range(family_size)]

def universal_hash_with_index(weak_key, H):
    weak_key_vector = np.array([int(bit) for bit in weak_key])
    hashed_key_vector = np.mod(H @ weak_key_vector, 2)
    return hashed_key_vector.astype(int)


class PrivAmp:
    def __init__(self):
        pass
    def univ2(self,params):
        akey = params['akey']
        bkey = params['bkey']
        final_key_length=params['final_key_length']
        family_size = params['family_size']
        key_length = len(akey)
        if key_length < final_key_length:
            return {'akey': akey, 'bkey': bkey}
        hash_family = generate_hash_family(final_key_length, key_length, family_size)
        
        chosen_hash_index = np.random.randint(0, family_size - 1)

        hash_func = hash_family[chosen_hash_index]
        ahash_key = universal_hash_with_index(akey, hash_func)
        bhash_key = universal_hash_with_index(bkey, hash_func)
        return {'akey': ahash_key, 'bkey': bhash_key}
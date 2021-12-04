import random

def generate_pass(pass_len, use_numbers, use_letters, use_signs):
    chars = ''
    if use_numbers:
        chars += '1234567890' 
    if use_letters:
        chars += 'abcdefghijklnopqrstuvwxyz'
    if use_signs:
        chars += '+-/*!&$#?=@<>'
    pass_len = int(pass_len) #
    password =''
    for i in range(pass_len):
        password += random.choice(chars)
    return password

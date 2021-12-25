from email import message_from_binary_file
import random
from flask_mail import Message
from app import mail

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

def send_password_to_email(password, user_email, user_name):
    msg = Message('Reset password', sender='microblog', recipients=[user_email])
    msg.body = f"Your username: {user_name}\nYour new password: {password}"
    mail.send(msg)
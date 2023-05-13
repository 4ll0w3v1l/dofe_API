import sqlite3
import os
import secrets
from hashlib import sha256


class DBOperation:
    db_path = 'main.db'
    secure_db_path = 'secure.db'

    def __init__(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        if not os.path.isfile(self.db_path):
            payload = 'CREATE TABLE users ' \
                      '(ID INT PRIMARY KEY,' \
                      'name VARCHAR(50),' \
                      'email VARCHAR(100),' \
                      'password VARCHAR(50));'
            cur.execute(payload)
            con.commit()
        if not os.path.isfile(self.secure_db_path):
            con = sqlite3.connect(self.secure_db_path)
            cur = con.cursor()
            payload = 'CREATE TABLE tokens(' \
                      'uId int, ' \
                      'token varchar(100)' \
                      ')'
            cur.execute(payload)
            con.commit()

    def create_token(self, uid):
        token = secrets.token_hex(64)
        con = sqlite3.connect(self.secure_db_path)
        cur = con.cursor()
        cur.execute('INSERT INTO tokens(uId, token) VALUES(?, ?)', (uid, token))
        con.commit()
        return token

    def delete_token(self, uid):
        con = sqlite3.connect(self.secure_db_path)
        cur = con.cursor()
        cur.execute('DELETE FROM tokens WHERE uId == ?', (uid, ))
        con.commit()

    def user_registration(self, e, p, n=''):
        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            tmp = cur.execute('SELECT * FROM users ORDER BY ID DESC LIMIT 1').fetchall()
            print(tmp)
            first = True if len(tmp) <= 0 else False
            if not first and tmp[0][2] == e:
                return [400, 'This Email is already in use']
            else:
                cur.execute('INSERT INTO users(ID, name, email, password) VALUES(?, ?, ?, ?)', (tmp[0][0] + 1, n, e, sha256(p.encode()).hexdigest()))
                con.commit()
                uid = cur.execute('SELECT ID FROM users WHERE email == ?', (e,)).fetchall()[0][0]
                return [200, self.create_token(uid)]

        except Exception as e:
            return [400, e]
    def token_valid_acc(self, uid, token):
        con = sqlite3.connect(self.secure_db_path)
        cur = con.cursor()
        try:
            check = cur.execute('SELECT uId FROM tokens WHERE token == ?', (token,)).fetchall()
            validation = True if check[0][0] == uid else False
            return [True, validation]
        except:
            return [False, False]

    def get_acc(self, uid):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        data = cur.execute('SELECT ID, name, email FROM users WHERE ID == ?', (uid, )).fetchall()
        return data[0]

    def login(self, e, p):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        data = cur.execute('SELECT ID FROM users WHERE password == ? AND email == ?', (sha256(p.encode()).hexdigest(), e)).fetchall()
        if len(data) <= 0:
            return [400, 'Incorrect credentials']
        else:
            self.delete_token(data[0][0])
            return [1, self.create_token(data[0][0])]
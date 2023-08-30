import time
import os
import sqlite3
import random
from datetime import datetime

conn = sqlite3.connect("mydatabase.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Bank_Log(
    Time DATETIME NOT NULL,
    Sender VARCHAR(20) NOT NULL,
    Receiver VARCHAR(20) NOT NULL,
    Amount FLOAT(2) NOT NULL,
    Sender_Balance Float(2) NOT NULL,
    Receiver_Balance FLOAT(2) NOT NULL
);
''')


cursor.execute('''
CREATE TABLE IF NOT EXISTS Bank_Database(
    Account_Number INTEGER PRIMARY KEY,
    User_Name VARCHAR(20) NOT NULL,
    Age INTEGER NOT NULL,
    Type CHAR(1) NOT NULL,
    Phone INTEGER NOT NULL UNIQUE,
    Email VARCHAR(30) NOT NULL UNIQUE,
    Login_Name VARCHAR(20) NOT NULL UNIQUE,
    User_Password VARCHAR(20) NOT NULL,
    Balance FLOAT(2) NOT NULL
);
''')

def accnum_creation():
    while 1:
        r = random.randint(0000000000,9999999999)
        query = "select Account_Number from Bank_Database where Account_Number = ?"
        c = list(cursor.execute(query,(r,)))
        if not c:
            break
    return r
            


def AccountCreate():
    try:
        acc = accnum_creation()
        name = input("Name: ")
        age = int(input("Age: "))
        type = input("Type(s/c): ")
        email = input("Email: ")
        phone = input("Phone: ")
        username = input("Username: ")
        password = input("password: ")
        cpassword = input("confirm password: ")
        bal = 0.00

        if password!=cpassword:
            print("password doesn't match with confirm password")
            time.sleep(3)
            clear()
            AccountCreate()

        if len(phone)!=10:
            raise

        cursor.execute('''
insert into Bank_Database(Account_Number,User_Name,Age,Type,Phone,
                       Email,Login_Name,User_Password,Balance) values ({},'{}',{},'{}',{},'{}','{}','{}',{})                      
'''.format(acc,name,age,type,int(phone),email,username,cpassword,bal))
        conn.commit()
        print("Account creation Successfull")
        time.sleep(3)
    except Exception as e:
        print("Invalid credentials Try again...")
        time.sleep(5)
        clear()
        os.system("python p_a_t.py")
    else:
        clear()
        print("login page\n")
        login()


def TakeInput2():
    print("[0] NO")
    print("[1] YES")
    return input(">>>")

def clear():
    os.system("cls")

def menu(acc):
    print("[1] Transfer Money")
    print("[2] Deposit Money")
    print("[3] Print Statement")
    print("[0] Exit")

    inp = input(">>>")
    if inp == '1':
        clear()
        transfer(acc)
    elif inp=='2':
        clear()
        deposit(acc)
    elif inp=='3':
        clear()
        statement(acc)
    elif inp=='0':
        print("thank you for banking with us....\nHave a nice day!!!")
        time.sleep(3)
        exit()

def login():
    try:
        username = input("Username: ")
        password = input("Password: ")

        query = "select Login_Name from Bank_Database where Login_Name = ?"
        cursor.execute(query,(username,))
        usr =cursor.fetchone()
        if usr:
            query1 = "select User_Password from Bank_Database where Login_Name = ?"
            cursor.execute(query1,(username,))
            ps = cursor.fetchone()
            if ps[0]==password:
                print("\nLogin Successful !!!")
                query2 = "select Account_Number from Bank_Database where Login_Name = ?"
                cursor.execute(query2,(username,))
                acc = (cursor.fetchone())[0]
                time.sleep(2)
                
            else:
                raise
        else:
            raise
    except Exception as e:
        print("Inavalid Credentials...")
        time.sleep(5)
        clear()
        login()
    else:
        menu(acc)

def deposit(acc):
    amount = float(input("Amount: "))
    cnf_amount = float(input("Confirm Amount: "))

    if cnf_amount!=amount:
        print("account doesn't match")
        clear()
        time.sleep(2)
        deposit()
    
    cursor.execute("select Balance from Bank_Database where Account_Number = ?",(acc,))
    bal = cursor.fetchone()
    new_bal = bal[0]+amount
    
    cursor.execute("update Bank_Database set Balance = {} where Account_Number = {}".format(new_bal,acc))

    now = datetime.now()
    qry = '''
insert into Bank_Log(Time,Sender,Receiver,Amount,Sender_Balance,Receiver_Balance)
values(?,?,?,?,?,?)'''
    cursor.execute(qry,(now.strftime("%Y-%m-%d %H:%M:%S"),acc,acc,amount,new_bal,new_bal))
    

    conn.commit()
    print("Amount deposited successfully!!")

    with open(f'{acc}.txt','a+') as fp:
        fp.write(f"{now} \t {amount} \t\t {new_bal}\n") 
    menu(acc)

def transfer(acc):
    ben_name = input("Enter benificary Name: ")
    ben_acc = int(input("Enter benificary account num: "))
    cben_acc = int(input("confirm account num: "))
    money = float(input("enter money to be transfered: "))

    if ben_acc!=cben_acc:
            print("account num & confirm account num doesn't match")
            time.sleep(2)
            clear()
            transfer()
    
    if ben_name==acc:
            print("can't transfer to own bank account")
            time.sleep(2)
            clear()
            transfer()

    print("Are the details correct, Confirm again..")
    x = TakeInput2()
    if x=='0':
        clear()
        transfer(acc)
    elif x=='1':
        query1 = '''
select User_Name,Account_Number from Bank_Database
where User_Name = ? and Account_Number = ?
'''
    if cursor.execute(query1,(ben_name,ben_acc)):
        cursor.execute("select Balance from Bank_Database where Account_Number = ?",(ben_acc,))
        bal_ben = cursor.fetchone()
        new_bal_ben = bal_ben[0]+money
        cursor.execute("select Balance from Bank_Database where Account_Number = ?",(acc,))
        bal_ben = cursor.fetchone()
        new_bal_sen = bal_ben[0]-money
        if new_bal_sen < 0.00:
            print("Amount exceeded to transfer than the actual balance")
            time.sleep(3)
            transfer(acc)
        cursor.execute("update Bank_Database set Balance = {} where Account_Number = ? ".format(new_bal_ben),(ben_acc,))
        cursor.execute("update Bank_Database set Balance = {} where Account_Number = ? ".format(new_bal_sen),(acc,))
        conn.commit()
        print("Money credited to the beneficeary")
        time.sleep(5)
        now = datetime.now()
        qry = '''
    insert into Bank_Log(Time,Sender,Receiver,Amount,Sender_Balance,Receiver_Balance)
    values(?,?,?,?,?,?)'''
        cursor.execute(qry,(now.strftime("%Y-%m-%d %H:%M:%S"),acc,ben_acc,money,new_bal_sen,new_bal_ben))
        conn.commit()

        with open(f'{ben_acc}.txt','a+') as fp:
            fp.write(f"{now} \t {money} \t\t {new_bal_ben}\n")
        
        with open(f'{acc}.txt','a+') as fp:
            fp.write(f"{now} \t -{money} \t\t {new_bal_sen}\n")
        
        
        menu(acc)
    else:
        print("Invalid credentials....Try again")
        time.sleep(5)
        transfer(acc)



def statement(acc):
    with open(f"{acc}.txt",'r+') as fp:
        line = fp.readlines()
        clear()
        print("          DateTime               Transaction             Current_balance\n")
        if len(line)==0:
            print("statement is empty")
        for i in line:
            print(i)
    try:
        print('\n\n')
        if input("press [0] to exit to menu: ")=='0':
            menu(acc)
    except Exception as e:
        print("Some error occured Try again...")
        clear()
        os.system("python p_a_t.py")



if __name__ == "__main__":
   
    print("*****************************************************************************")
    print('''

  /$$$$$$  /$$$$$$$   /$$$$$$        /$$$$$$$   /$$$$$$  /$$   /$$ /$$   /$$
 /$$__  $$| $$__  $$ /$$__  $$      | $$__  $$ /$$__  $$| $$$ | $$| $$  /$$/
| $$  \ $$| $$  \ $$| $$  \__/      | $$  \ $$| $$  \ $$| $$$$| $$| $$ /$$/ 
| $$$$$$$$| $$$$$$$ | $$            | $$$$$$$ | $$$$$$$$| $$ $$ $$| $$$$$/  
| $$__  $$| $$__  $$| $$            | $$__  $$| $$__  $$| $$  $$$$| $$  $$  
| $$  | $$| $$  \ $$| $$    $$      | $$  \ $$| $$  | $$| $$\  $$$| $$\  $$ 
| $$  | $$| $$$$$$$/|  $$$$$$/      | $$$$$$$/| $$  | $$| $$ \  $$| $$ \  $$
|__/  |__/|_______/  \______/       |_______/ |__/  |__/|__/  \__/|__/  \__/
                                                                            
                                                                            
                                                                            

''')
    print("*****************************************************************************\n")
    print("Existing Customer?")
    inp = TakeInput2()
    if inp == '0':
        clear()
        print("\nWe are delighted to have you here \nWould you like to create a account with us?\n")
        inp = TakeInput2()
        if inp=='0':
            clear()
            print("If anything else we can do for you you can you can contact at our nearest branch")
            print("the system will exit in 5 seconds")
            print("thank you for coming here, have a nice day")
            time.sleep(5)
            exit()
        elif inp=='1':
            clear()
            AccountCreate()
            
    elif inp=='1':
        clear()
        login()

    else:
        clear()
        os.system("python p_a_t.py")
from flask import Flask
from flask import Flask, render_template, Response, redirect, request, session, abort, url_for

import os
import time
import datetime
from random import randint
import cv2
import PIL.Image
from PIL import Image
import img2pdf
import imagehash
from flask import send_file
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import docx2txt
import shutil
import subprocess
import cv2
import PIL.Image
from PIL import Image
#from xgboost import XGBRegressor
import gensim
#word to pdf
import aspose.words as aw

import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  charset="utf8",
  database="campus_placement_portal"
)
app = Flask(__name__)
##session key
app.secret_key = 'abcdef'
#######
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#####

@app.route('/',methods=['POST','GET'])
def index():
    act=""
    msg=""

    #now1 = datetime.datetime.now()
    #rtime=now1.strftime("%H:%M")
    #print(rtime)

    return render_template('web/index.html',msg=msg,act=act)

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    msg=""
    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM vh_admin WHERE username = %s AND password = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('admin'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login_admin.html',msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg=""
    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM vh_candidate WHERE username = %s AND password = %s', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('userhome'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html',msg=msg)

@app.route('/login_company', methods=['GET', 'POST'])
def login_company():
    msg=""
    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute('SELECT * FROM vh_job_provider_register WHERE hr_id = %s AND password = %s AND approved_status=1', (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('add_vacancy'))
        else:
            msg = 'Incorrect username/password! or Not Approved'
    return render_template('login_company.html',msg=msg)

@app.route('/login_hod', methods=['GET', 'POST'])
def login_hod():
    msg=""
    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM vh_hod WHERE staff_id = %s AND password = %s", (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('hod_home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login_hod.html',msg=msg)

@app.route('/login_pc', methods=['GET', 'POST'])
def login_pc():
    msg=""
    
    if request.method=='POST':
        uname=request.form['uname']
        pwd=request.form['pass']
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM vh_placement WHERE staff_id = %s AND password = %s", (uname, pwd))
        account = cursor.fetchone()
        if account:
            session['username'] = uname
            return redirect(url_for('pc_home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login_pc.html',msg=msg)


@app.route('/register',methods=['POST','GET'])
def register():
    msg=""
    act=""
    if request.method=='POST':
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        
        uname=request.form['uname']
        pass1=request.form['pass']
      
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        mycursor.execute("SELECT count(*) FROM vh_candidate where username=%s",(uname, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM vh_candidate")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            sql = "INSERT INTO vh_candidate(id,name,mobile, email, username,password,register_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (maxid,name,mobile,email,uname,pass1,rdate)
            print(sql)
            mycursor.execute(sql, val)
            mydb.commit()            
            print(mycursor.rowcount, "record inserted.")
            msg='success'
            
            #if mycursor.rowcount==1:
            #    result="Registered Success"
            
        else:
            msg="fail"
    return render_template('register.html',msg=msg)

@app.route('/add_dept',methods=['POST','GET'])
def add_dept():
    msg=""
    act=request.args.get("act")
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_dept")
    drow = mycursor.fetchall()

        
    if request.method=='POST':
        dept=request.form['dept']
       
      
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        mycursor.execute("SELECT count(*) FROM vh_dept where dept=%s",(dept, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM vh_dept")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            sql = "INSERT INTO vh_dept(id,dept) VALUES (%s, %s)"
            val = (maxid,dept)
            print(sql)
            mycursor.execute(sql, val)
            mydb.commit()            
            print(mycursor.rowcount, "record inserted.")
            msg='success'
            
            #if mycursor.rowcount==1:
            #    result="Registered Success"
            
        else:
            msg="fail"

    if act=="del":
        did=request.args.get("did")
        mycursor.execute("delete from vh_dept where id=%s",(did,))
        mydb.commit()
        return redirect(url_for('add_dept'))
            

            
    return render_template('add_dept.html',msg=msg,drow=drow)

@app.route('/add_student',methods=['POST','GET'])
def add_student():
    msg=""
    act=request.args.get("act")
    email=""
    mess=""
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_dept")
    drow = mycursor.fetchall()

    mycursor.execute("SELECT * FROM vh_candidate")
    data = mycursor.fetchall()
        
    if request.method=='POST':
        name=request.form['name']
        gender=request.form['gender']
        dob=request.form['dob']
        mobile=request.form['mobile']
        email=request.form['email']
        address=request.form['address']
        city=request.form['city']
        dept=request.form['dept']
        year=request.form['year']
        
        regno=request.form['regno']
        na=name[0:3]
        pass1=na+"@123"
      
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        

        mycursor.execute("SELECT count(*) FROM vh_candidate where username=%s",(regno, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM vh_candidate")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            sql = "INSERT INTO vh_candidate(id,name,gender,dob,mobile, email,address,city,dept,year,username,password,register_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            val = (maxid,name,gender,dob,mobile,email,address,city,dept,year,regno,pass1,rdate)
            print(sql)
            mycursor.execute(sql, val)
            mydb.commit()            
            print(mycursor.rowcount, "record inserted.")

            mess="Dear "+name+", Register No.: "+regno+", Password: "+pass1
            msg='success'
            
            #if mycursor.rowcount==1:
            #    result="Registered Success"
            
        else:
            msg="fail"

    if act=="del":
        did=request.args.get("did")
        mycursor.execute("delete from vh_candidate where id=%s",(did,))
        mydb.commit()
        return redirect(url_for('add_student'))

    
    return render_template('add_student.html',msg=msg,email=email,mess=mess,drow=drow,data=data)

@app.route('/change',methods=['POST','GET'])
def change():
    msg=""
    act=request.args.get("act")
    email=""
    mess=""
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_dept")
    drow = mycursor.fetchall()

    mycursor.execute("SELECT * FROM vh_candidate")
    data = mycursor.fetchall()
        
    if request.method=='POST':
        dept=request.form['dept']
        semester=request.form['semester']
        mycursor.execute("update vh_candidate set semester=%s where dept=%s",(semester,dept))
        mydb.commit()
        msg="ok"
        
    return render_template('change.html',msg=msg,drow=drow,data=data)

@app.route('/add_hod',methods=['POST','GET'])
def add_hod():
    msg=""
    email=""
    mess=""
    act=request.args.get("act")
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_dept")
    drow = mycursor.fetchall()

    mycursor.execute("SELECT * FROM vh_hod")
    data = mycursor.fetchall()

    
    if request.method=='POST':
        
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        dept=request.form['dept']
        
        uname=request.form['staff_id']
        na=name[0:3]
        pass1=na+"@123"
      
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        mycursor.execute("SELECT count(*) FROM vh_hod where staff_id=%s",(uname, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM vh_hod")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            sql = "INSERT INTO vh_hod(id,name,mobile, email, staff_id,password,dept,register_date) VALUES (%s, %s, %s, %s, %s, %s,%s, %s)"
            val = (maxid,name,mobile,email,uname,pass1,dept,rdate)
            print(sql)
            mycursor.execute(sql, val)
            mydb.commit()            
            print(mycursor.rowcount, "record inserted.")
            mess="Dear "+name+", Staff ID: "+uname+", Password: "+pass1
            msg='success'
            
            #if mycursor.rowcount==1:
            #    result="Registered Success"
            
        else:
            msg="fail"

    if act=="del":
        did=request.args.get("did")
        mycursor.execute("delete from vh_hod where id=%s",(did,))
        mydb.commit()
        return redirect(url_for('add_hod'))


    
    return render_template('add_hod.html',msg=msg,email=email,mess=mess,data=data,drow=drow)

@app.route('/add_placement',methods=['POST','GET'])
def add_placement():
    msg=""
    email=""
    mess=""
    act=request.args.get("act")
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_dept")
    drow = mycursor.fetchall()
    
    mycursor.execute("SELECT * FROM vh_placement")
    data = mycursor.fetchall()

    
    if request.method=='POST':
        
        name=request.form['name']
        mobile=request.form['mobile']
        email=request.form['email']
        
        uname=request.form['staff_id']
        na=name[0:3]
        pass1=na+"@123"
      
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        

        mycursor.execute("SELECT count(*) FROM vh_placement where staff_id=%s",(uname, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM vh_placement")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            sql = "INSERT INTO vh_placement(id,name,mobile, email, staff_id,password,register_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = (maxid,name,mobile,email,uname,pass1,rdate)
            print(sql)
            mycursor.execute(sql, val)
            mydb.commit()            
            
        else:
            msg="fail"

    if act=="del":
        did=request.args.get("did")
        mycursor.execute("delete from vh_placement where id=%s",(did,))
        mydb.commit()
        return redirect(url_for('add_placement'))

    
    return render_template('add_placement.html',msg=msg,email=email,mess=mess,data=data,drow=drow)

@app.route('/add_mark',methods=['POST','GET'])
def add_mark():
    msg=""
    act=request.args.get("act")
    cid=request.args.get("cid")
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_candidate where id=%s",(cid, ))
    cdata = mycursor.fetchone()
    regno=cdata[6]

    mycursor.execute("SELECT * FROM vh_mark where regno=%s",(regno,))
    data = mycursor.fetchall()
    
    if request.method=='POST':
        
        semester=request.form['semester']
        mark=request.form['mark']
        arrear=request.form['arrear']
        cleared=request.form['cleared']
        
        
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()
        mycursor = mydb.cursor()

        mycursor.execute("SELECT max(id)+1 FROM vh_mark")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
        sql = "INSERT INTO vh_mark(id,regno,semester,mark,arrear,cleared,register_date) VALUES (%s, %s, %s, %s, %s, %s,%s)"
        val = (maxid,regno,semester,mark,arrear,cleared,rdate)
        print(sql)
        mycursor.execute(sql, val)
        mydb.commit()
        return redirect(url_for('add_mark',cid=cid))
    
    if act=="del":
        did=request.args.get("did")
        mycursor.execute("delete from vh_mark where id=%s",(did,))
        mydb.commit()
        return redirect(url_for('add_mark',cid=cid))
    
      
    return render_template('add_mark.html',msg=msg,data=data,cid=cid)

@app.route('/add_att',methods=['POST','GET'])
def add_att():
    msg=""
    act=request.args.get("act")
    cid=request.args.get("cid")

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_candidate where id=%s",(cid, ))
    cdata = mycursor.fetchone()
    regno=cdata[6]

    mycursor.execute("SELECT * FROM vh_att where regno=%s",(regno,))
    data = mycursor.fetchall()
    
    if request.method=='POST':
        
        semester=request.form['semester']
        
        total_days=request.form['total_days']
        present=request.form['present']
        absent=request.form['absent']
        
        
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        
        m1=(int(present)/int(total_days))*100
        mark=round(m1,2)
       


        mycursor.execute("SELECT max(id)+1 FROM vh_att")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
        sql = "INSERT INTO vh_att(id,regno,semester,total_days,present,absent,mark,register_date) VALUES (%s,%s, %s, %s, %s, %s, %s, %s)"
        val = (maxid,regno,semester,total_days,present,absent,mark,rdate)
        print(sql)
        mycursor.execute(sql, val)
        mydb.commit()
        return redirect(url_for('add_att',cid=cid))

    if act=="del":
        did=request.args.get("did")
        mycursor.execute("delete from vh_att where id=%s",(did,))
        mydb.commit()
        return redirect(url_for('add_att',cid=cid))
            
        
    return render_template('add_att.html',msg=msg,data=data,cid=cid)

@app.route('/add_company',methods=['POST','GET'])
def add_company():
    msg=""
    act=request.args.get("act")
    uname=""
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_job_provider")
    data = mycursor.fetchone()

    
    if request.method=='POST':
        company=request.form['company']
        name=request.form['name']
        services=request.form['services']
        
        mobile=request.form['mobile']
        email=request.form['email']
        location=request.form['location']
        
      
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        mycursor.execute("SELECT count(*) FROM vh_job_provider_register where hr_id=%s",(uname, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM vh_job_provider_register")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1

            
            v1=str(maxid)
            val=v1.zfill(4)
            uname="C"+val

            #rn=randint(100,999)
            #p1=mobile[7:10]
            na=name[0:3]
            
            pass1=na+"@123"

            link="http://localhost:5000/login_company"
            
            sql = "INSERT INTO vh_job_provider_register(id,hr_name,company_name,services,location,mobile, email, hr_id,password,approved_status,register_date,placement) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s)"
            val = (maxid,name,company,services,location,mobile,email,uname,pass1,'1',rdate,uname)
            print(sql)
            mycursor.execute(sql, val)
            mydb.commit()            
    

            mess="Dear "+name+", Company:"+company+", User ID:"+unmae+", Paaswprd: "+pass1+", Link: "+link
            msg='success'

            #xgboost
            #if mycursor.rowcount==1:
            #    result="Registered Success"
            
        else:
            msg="fail"
    return render_template('add_company.html',msg=msg,email=email,mess=mess)

@app.route('/admin',methods=['POST','GET'])
def admin():
    msg=""
    email=""
    mess=""
    act=request.args.get("act")
    uname=""
    data=[]
   
    s1=""
    s2=""

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_job_provider_register")
    data = mycursor.fetchall()

    if act=="yes":
        cid=request.args.get("cid")
        mycursor.execute("SELECT * FROM vh_job_provider_register where id=%s",(cid,))
        ds = mycursor.fetchone()
        email=ds[6]
        name=ds[1]
        company=ds[2]
        mess="Dear "+name+", Company:"+company+" has Approved for accessing Virtual HR Web App"
        
        mycursor.execute("update vh_job_provider_register set approved_status=1 where id=%s",(cid,))
        mydb.commit()
        msg="ok"

    return render_template('admin.html',msg=msg,act=act,data=data,email=email,mess=mess)

@app.route('/candidate_vacancy',methods=['POST','GET'])
def candidate_vacancy():
    msg=""
    email=""
    mess=""
    act=request.args.get("act")
    uname=""
    data=[]
   
    s1=""
    s2=""

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_candidate where username=%s",(uname, ))
    data = mycursor.fetchone()
    
    mycursor.execute("SELECT * FROM vh_vacancy order by id desc")
    data1 = mycursor.fetchall()



    return render_template('candidate_vacancy.html',msg=msg,act=act,data=data,data1=data1)

@app.route('/admin_vacancy',methods=['POST','GET'])
def admin_vacancy():
    msg=""
    email=""
    mess=""
    act=request.args.get("act")
    uname=""
    data=[]
   
    s1=""
    s2=""

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_vacancy order by id desc")
    data = mycursor.fetchall()



    return render_template('admin_vacancy.html',msg=msg,act=act,data=data)

@app.route('/add_resume',methods=['POST','GET'])
def add_resume():
    msg=""
    act=request.args.get("act")
    uname=""
    data1=[]
    data2=[]
    s1=""
    s2=""

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_candidate where username=%s",(uname, ))
    data = mycursor.fetchone()


    mycursor.execute("SELECT count(*) FROM vh_certificate where uname=%s",(uname, ))
    c1 = mycursor.fetchone()[0]
    if c1>0:
        s1="1"
        mycursor.execute("SELECT * FROM vh_certificate where uname=%s",(uname, ))
        data1 = mycursor.fetchall()

    mycursor.execute("SELECT count(*) FROM vh_experience where username=%s",(uname, ))
    c2 = mycursor.fetchone()[0]
    if c2>0:
        s2="1"
        mycursor.execute("SELECT * FROM vh_experience where username=%s",(uname, ))
        data2 = mycursor.fetchall()

    
    if request.method=='POST':
        name=request.form['name']
        gender=request.form['gender']
        dob=request.form['dob']
        mobile=request.form['mobile']
        email=request.form['email']
        address=request.form['address']
        city=request.form['city']
        postal_code=request.form['postal_code']
        father_name=request.form['father_name']
        father_occupation=request.form['father_occupation']
        father_jobtype=request.form['father_jobtype']
        father_job_location=request.form['father_job_location']
        father_annual_income=request.form['father_annual_income']
        mother_name=request.form['mother_name']
        mother_occupation=request.form['mother_occupation']
        mother_jobtype=request.form['mother_jobtype']
        mother_job_location=request.form['mother_job_location']
        mother_annual_income=request.form['mother_annual_income']
        
        
        mycursor.execute("update vh_candidate set name=%s,gender=%s,dob=%s,mobile=%s,email=%s,address=%s,city=%s,postal_code=%s where username=%s", (name,gender,dob,mobile,email,address,city,postal_code,uname))
        mydb.commit()
        mycursor.execute("update vh_candidate set father_name=%s,father_occupation=%s,father_jobtype=%s,father_job_location=%s,father_annual_income=%s where username=%s", (father_name,father_occupation,father_jobtype,father_job_location,father_annual_income,uname))
        mydb.commit()
        mycursor.execute("update vh_candidate set mother_name=%s,mother_occupation=%s,mother_jobtype=%s,mother_job_location=%s,mother_annual_income=%s where username=%s", (mother_name,mother_occupation,mother_jobtype,mother_job_location,mother_annual_income,uname))
        mydb.commit()

        msg="success"

    if act=="del":
        did=request.args.get("did")
        mycursor.execute("delete from vh_qualification where id=%s",(did,))
        mydb.commit()
        msg="ok"
    if act=="del2":
        did=request.args.get("did")
        mycursor.execute("delete from vh_experience where id=%s",(did,))
        mydb.commit()
        msg="ok2"

        
    return render_template('add_resume.html',data=data,msg=msg,data1=data1,data2=data2,s1=s1,s2=s2)

@app.route('/userhome',methods=['POST','GET'])
def userhome():
    msg=""
    uname=""
    st=""
    data1=[]

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_candidate where username=%s",(uname, ))
    data = mycursor.fetchone()

    ff=open("emotion.txt","w")
    ff.write("")
    ff.close()

    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    #print(rtime)
    
    rtime1=rtime.split(':')
    rh=int(rtime1[0])
    rm=int(rtime1[1])

    mycursor.execute("SELECT count(*) FROM vh_profile_matched where username=%s && interview_status=1",(uname, ))
    cn = mycursor.fetchone()[0]
    if cn>0:
        
        mycursor.execute("SELECT * FROM vh_profile_matched where username=%s && interview_status=1",(uname, ))
        data2 = mycursor.fetchone()
        iv_date=data2[4]
        iv_time=data2[5]

        if rdate==iv_date:
            ivt=iv_time.split(":")
            ih=int(ivt[0])
            if ih<=rh:
                st="1"
                mycursor.execute("SELECT * FROM vh_profile_matched where username=%s && interview_status=1",(uname, ))
                data1 = mycursor.fetchall()
        
        

    return render_template('userhome.html',data=data,data1=data1,msg=msg,st=st)

@app.route('/add_school',methods=['POST','GET'])
def add_school():
    uname=""

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_candidate where username=%s",(uname, ))
    data = mycursor.fetchone()
    

    if request.method=='POST':
        sslc_school=request.form['sslc_school']
        sslc_mark=request.form['sslc_mark']
        hsc_school=request.form['hsc_school']
        hsc_mark=request.form['hsc_mark']
        
        mycursor.execute("update vh_candidate set sslc_school=%s,sslc_mark=%s,hsc_school=%s,hsc_mark=%s where username=%s", (sslc_school,sslc_mark,hsc_school,hsc_mark,uname))
        mydb.commit()

        msg="success2"
    
    return render_template('add_resume.html',data=data)

@app.route('/add_qualification',methods=['POST','GET'])
def add_qualification():
    uname=""

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_candidate where username=%s",(uname, ))
    data = mycursor.fetchone()

    mycursor.execute("SELECT * FROM vh_certificate where uname=%s",(uname, ))
    data1 = mycursor.fetchall()

    if request.method=='POST':
        detail=request.form['detail']
        file = request.files['file']

        mycursor.execute("SELECT max(id)+1 FROM vh_certificate")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
                
        fn1="S"+str(maxid)+file.filename
        file.save(os.path.join("static/certificate", fn1))
        sql = "INSERT INTO vh_certificate(id, uname, detail, filename) VALUES (%s, %s, %s, %s)"
        val = (maxid,uname,detail,fn1)
        
        mycursor.execute(sql, val)
        mydb.commit()
        msg="success3"
        
        '''if request.method=='POST':
        level=request.form['level']
        qualification=request.form['qualification']
        passout_year=request.form['passout_year']
        percentage=request.form['percentage']
        college=request.form['college']
        arrears=request.form['arrears']
        cleared=request.form['cleared']
        
        mycursor.execute("SELECT max(id)+1 FROM vh_qualification")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
        sql = "INSERT INTO vh_qualification(id,username,level,qualification,passout_year,percentage,college,arrears,cleared) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (maxid, uname,level,qualification,passout_year,percentage,college,arrears,cleared)
        print(sql)
        mycursor.execute(sql, val)
        mydb.commit() '''

        
    
    return render_template('add_resume.html',data=data,data1=data1)



@app.route('/upload_resume',methods=['POST','GET'])
def upload_resume():
    msg=""
    uname=""
    filename=""
    
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_candidate where username=%s",(uname, ))
    data = mycursor.fetchone()
    rid=data[0]

    if request.method=='POST':
        file = request.files['file']
        file_type = file.content_type
        
        if file.filename == '':
            #flash('No selected file')
            return redirect(request.url)
        if file:
            fname = "R"+str(rid)+file.filename
            filename = secure_filename(fname)
            file.save(os.path.join("static/upload", filename))

            #docx to pdf
            resume_doc=filename
            rd=resume_doc.split(".")
            resume_pdf=rd[0]+".pdf"
            # Load word document
            doc = aw.Document("static/upload/"+resume_doc)

            # Save as PDF
            doc.save("static/upload/"+resume_pdf)
        
        
        mycursor.execute("update vh_candidate set resume=%s where username=%s", (filename,uname))
        mydb.commit()
        msg="success5"
    
    return render_template('add_resume.html',data=data,msg=msg)

@app.route('/upload_photo',methods=['POST','GET'])
def upload_photo():
    uname=""

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_candidate where username=%s",(uname, ))
    data = mycursor.fetchone()
    rid=data[0]

    if request.method=='POST':
        file = request.files['file2']
        fn1="P"+str(rid)+file.filename
        
        print(fn1)
        mycursor.execute("update vh_candidate set photo=%s where username=%s", (fn1,uname))
        mydb.commit()

        file.save(os.path.join("static/upload", fn1))
        
        msg="success6"
    
    return render_template('add_resume.html',data=data)

@app.route('/add_vacancy',methods=['POST','GET'])
def add_vacancy():
    msg=""
    uname=""
    act=request.args.get("act");
    vid=request.args.get("vid")
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()

    #ff=open("static/upload/R1resume_001.docx","r")
    #fdata=ff.read()
    #ff.close()
    #print(fdata.decode(''))

    mycursor.execute("SELECT * FROM vh_job_provider_register where hr_id=%s",(uname,))
    data1 = mycursor.fetchone()
    company=data1[2]

    if request.method=='POST':
        job_title=request.form['job_title']
        gender=request.form['gender']
        mark_10th=request.form['mark_10th']
        mark_12th=request.form['mark_12th']
        level=request.form['level']
        qualification=request.form['qualification']
        mark_degree=request.form['mark_degree']
        arrears=request.form['arrears']
        
        sports=request.form['sports']
        extra_curricular=request.form['extra_curricular']
        skills=request.form['skills']

        
        
        mycursor.execute("SELECT max(id)+1 FROM vh_vacancy")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
        vid=str(maxid)
        sql = "INSERT INTO vh_vacancy(id,job_title,gender,mark_10th,mark_12th,level,qualification,mark_degree,arrears,sports,extra_curricular,skills,hr_id,company) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (maxid,job_title,gender,mark_10th,mark_12th,level,qualification,mark_degree,arrears,sports,extra_curricular,skills,uname,company)
        
        mycursor.execute(sql, val)
        mydb.commit() 

        msg="success"

    
    mycursor.execute("SELECT * FROM vh_vacancy where hr_id=%s order by id desc",(uname,))
    data = mycursor.fetchall()

    if act=="del":
        did=request.args.get("did")
        mycursor.execute("delete from vh_vacancy where id=%s",(did,))
        mydb.commit()
        return redirect(url_for('add_vacancy'))
    
    return render_template('add_vacancy.html',msg=msg,act=act,data=data,vid=vid,data1=data1)

@app.route('/add_join',methods=['POST','GET'])
def add_join():
    msg=""
    uname=""
    mess=""
    email=""
    pid=request.args.get("pid")
    
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()



    mycursor.execute("SELECT * FROM vh_job_provider_register where hr_id=%s",(uname,))
    data1 = mycursor.fetchone()
    company=data1[2]

    mycursor.execute("SELECT * FROM vh_profile_matched where id=%s",(pid,))
    data2 = mycursor.fetchone()
    vid=data2[1]
    candidate=data2[2]

    mycursor.execute("SELECT * FROM vh_candidate where username=%s",(candidate,))
    data3 = mycursor.fetchone()
    email=data3[5]
    name=data3[1]
    cid=data3[0]
    

    if request.method=='POST':
        job_position=request.form['job_position']
        training=request.form['training']
        train_days=request.form['train_days']
        join_date=request.form['join_date']
        jj="Join on "+join_date
        salary=request.form['salary']

        jd=join_date.split('-')
        join_date1=jd[2]+"-"+jd[1]+"-"+jd[0]

        ###
        fn="C"+str(cid)+".jpg"
        fn1="C"+str(cid)+".pdf"
        image = cv2.imread('static/img/off2.jpg',cv2.IMREAD_UNCHANGED)

        
        
        position = (163,442)
        cv2.putText(image, name, position, cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1) 
        cv2.imwrite("static/offer/"+fn, image)

        position = (667,595)
        cv2.putText(image, salary, position, cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1) 
        cv2.imwrite("static/offer/"+fn, image)

        position = (658,257)
        cv2.putText(image, jj, position, cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1) 
        cv2.imwrite("static/offer/"+fn, image)

        position = (779,157)
        cv2.putText(image, company, position, cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1) 
        cv2.imwrite("static/offer/"+fn, image)

        position = (478,497)
        cv2.putText(image, job_position, position, cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 0), 1) 
        cv2.imwrite("static/offer/"+fn, image)
        ###
        img_path = "static/offer/"+fn
 
        # storing pdf path
        pdf_path = "static/offer/"+fn1
         
        # opening image
        image = Image.open(img_path)
         
        # converting into chunks using img2pdf
        pdf_bytes = img2pdf.convert(image.filename)
         
        # opening or creating pdf file
        file = open(pdf_path, "wb")
         
        # writing pdf files with chunks
        file.write(pdf_bytes)
         
        # closing image file
        image.close()
         
        # closing pdf file
        file.close()
        ############

        mycursor.execute("update vh_profile_matched set interview_status=5,offer_letter=%s where id=%s",(fn1,pid))
        mydb.commit()
        
        mycursor.execute("SELECT max(id)+1 FROM vh_joined")
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
        vid=str(maxid)
        sql = "INSERT INTO vh_joined(id,vid,pid,hr_id,candidate,job_position,training,train_days,join_date,salary) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val = (maxid,vid,pid,uname,candidate,job_position,training,train_days,join_date1,salary)
        mycursor.execute(sql, val)
        mydb.commit()
        mess="Dear "+name+", You are selected in "+company+", Joining on "+join_date1

        msg="ok"


    return render_template('add_join.html',msg=msg,email=email,mess=mess)

@app.route('/check_resume',methods=['POST','GET'])
def check_resume():
    msg=""
    uname=""
    mess=""
    email=""
    st=""
    vid=request.args.get("vid")
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_candidate")
    d1 = mycursor.fetchall()

    mycursor.execute("SELECT * FROM vh_vacancy where id=%s",(vid,))
    rs1 = mycursor.fetchone()
    dd2=[]

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    ##
    sk=rs1[11]
    sk1=sk.split(",")

    ##number of profile matched
    vn=0
    ##
    
    f=0
    k=0
    for rs in d1:
        dd1=[]

        s1=""
        s2=""
        s3=""
        s4=""
        s5=""
        s6=""
        ##########
        if rs[25]=="":
            s=1
        else:
            text = docx2txt.process("static/upload/"+rs[25], "/tmp/img_dir") 
            g=0
            for sk2 in sk1:
                
                if sk2 in text:
                    #print(sk2)
                    g+=1
            print("ggg")
            print(g)
        ##########
            
        ##gender
        if rs1[2]=="Any":
            s1="1"
        elif rs1[2]==rs[2]:
            s1="1"
        else:
            s1="2"
        ##mark1
        if rs1[3]<=rs[12]:
            s2="1"
        else:
            s2="2"
        ##mark2
        if rs[14]>0:
            if rs1[4]<=rs[14]:
                s3="1"
            else:
                s3="2"
        else:
            s3="1"
        ##level
        qx=0
        qx2=0
        qx3=0
        d2=0
        mycursor.execute("SELECT count(*) FROM vh_qualification where username=%s",(rs[6],))
        d2 = mycursor.fetchone()[0]
        if d2>0:
            
            mycursor.execute("SELECT count(*) FROM vh_qualification where username=%s && (level=%s || qualification=%s)",(rs[6],rs1[5],rs1[6]))
            qx = mycursor.fetchone()[0]

            mycursor.execute("SELECT sum(percentage) FROM vh_qualification where username=%s",(rs[6],))
            qx2 = mycursor.fetchone()[0]

            mycursor.execute("SELECT sum(arrears) FROM vh_qualification where username=%s",(rs[6],))
            qx3 = mycursor.fetchone()[0]

        qx22=qx2/d2
        qx33=qx3/d2

        
        if rs1[5]=="Any":
            s4="1"
        elif qx>0:
            s4="1"
        else:
            s4="2"
        ##mark
        if qx22>=rs1[7]:
            s5="1"
        else:
            s5="2"

        #arrear
        if qx33<=rs1[8]:
            s6="1"
        else:
            s6="2"
        

        # and s6=="1" and s7=="1"
        if s1=="1" and s2=="1" and s3=="1" and s4=="1" and s5=="1" and s6=="1" and g>0:
            #print(rs[8]+" "+rs1[1])
            #dd1.append(rs[8])
            #dd1.append(rs[1])
            #dd1.append(rs1[1])
            #data4.append(dd1)
            #print(rs1[1])
            
            #dd1.append(rs1[6])
            #dd1.append(rs1[1])
            #dd1.append(rs1[5])
            #data3.append(dd1)
            

            mycursor.execute("SELECT count(*) FROM vh_profile_matched where vacancy_id=%s && username=%s",(rs1[0],rs[6]))
            ucnt = mycursor.fetchone()[0]
            if ucnt==0:

                print(rs[6])
                print(s1)
                print(s2)
                print(s3)
                print(s4)
                print(s5)
                print(s6)

                mycursor.execute("SELECT count(*) FROM vh_candidate where username=%s && status=0",(rs[6],))
                cn = mycursor.fetchone()[0]
                if cn>0:
                    vn+=1
                    mycursor.execute("SELECT max(id)+1 FROM vh_profile_matched")
                    maxid = mycursor.fetchone()[0]
                    if maxid is None:
                        maxid=1

                    '''sdate=rs1[14]
                    stime=rs1[16]

                    hh=int(stime)
                    

                    rrr=[10,20,30]
                    rn=randint(1,3)
                    rn1=rn-1

                    itime=""
                    mm2=0
                    hh2=0
                    mm=rmin+rrr[rn1]
                    if mm>60:
                        hh2=hh+1
                        mm2=mm-60
                        itime=str(hh2)+":"+str(mm2)
                    else:
                        itime=str(hh)+":"+str(mm)'''

                    
                    sql = "INSERT INTO vh_profile_matched(id,vacancy_id,username,interview_date,interview_time,minutes) VALUES (%s, %s, %s,%s,%s,%s)"
                    val = (maxid,rs1[0],rs[6],'','','0')
                    
                    mycursor.execute(sql, val)
                    mydb.commit()

    
    mycursor.execute("SELECT * FROM vh_admin where username='admin'")
    d11 = mycursor.fetchone()
    email=d11[2]

    if vn>0:
        mess="Vacancy ID: "+vid+", "+str(vn)+" profiles matched"
    else:
        mess="Vacancy ID: "+vid+", No profiles matched"

    return render_template('check_resume.html',vid=vid,mess=mess,email=email)

@app.route('/resume_match',methods=['POST','GET'])
def resume_match():
    msg=""
    uname=""
    edata=[]
    s1=""
    vid=request.args.get("vid")
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_vacancy where id=%s && hr_id=%s",(vid,uname))
    rs1 = mycursor.fetchone()
    n=rs1[18]

    
    mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status=0 && p.vacancy_id=%s",(vid,))
    mdata = mycursor.fetchall()

    if request.method=='POST':
        uu=request.form.getlist('c1[]')
        s1="1"
        for u1 in uu:
            dt=[]

            #######
            sdate=rs1[14]
            stime=rs1[16]
            mins=30

            hh=int(stime)
            

            rrr=[5,10,15]
            rn=randint(1,3)
            rn1=rn-1

            itime=""
            mm2=0
            hh2=0
            mm=rmin+rrr[rn1]
            if mm>60:
                hh2=hh+1
                mm2=mm-60
                itime=str(hh2)+":"+str(mm2)
            else:
                itime=str(hh)+":"+str(mm)
            ########
            
            mycursor.execute("update vh_profile_matched set interview_status=1,interview_date=%s,interview_time=%s,minutes=%s where vacancy_id=%s && username=%s",(sdate,itime,mins,vid,u1))
            mydb.commit()

            #apti question
            mycursor.execute("SELECT * FROM vh_apti_question order by rand()")
            qlist = mycursor.fetchall()
            i=0
            qd=[]
            for qlist1 in qlist:
                if i<n:
                    #print(qlist1[0])
                    qd.append(str(qlist1[0]))

                i+=1
            quest=','.join(qd)

            mycursor.execute("update vh_candidate set question=%s where username=%s",(quest,u1))
            mydb.commit()
            #program
            mycursor.execute("SELECT * FROM vh_program where language=%s order by rand()",(rs1[19],))
            plist = mycursor.fetchall()
            i=0
            pgm=""
            for plist1 in plist:
                if i<1:
                    pgm=str(plist1[0])
                i+=1
                    

            mycursor.execute("update vh_candidate set program=%s where username=%s",(pgm,u1))
            mydb.commit()
            ##
            mycursor.execute("SELECT * FROM vh_candidate where username=%s ",(u1,))
            d2 = mycursor.fetchone()
            email=d2[5]
            name=d2[1]

            mess="Dear "+name+", You are selected for Interview, Date:"+sdate+", Time:"+itime+", "+str(mins)+" minutes"
            dt.append(email)
            dt.append(mess)
            edata.append(dt)
        
  

    return render_template('resume_match.html',vid=vid,mdata=mdata,edata=edata,s1=s1)


@app.route('/view_candidate',methods=['POST','GET'])
def view_candidate():
    msg=""
    cid=request.args.get("cid")
    uname=""
    edata=[]
    s1=""
    fn=""
    
    if 'username' in session:
        uname = session['username']

    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_candidate where id=%s ",(cid,))
    data = mycursor.fetchone()

    if data[25]=="":
        s=1
    else:
        s1="1"
        f1=data[25].split(".")
        fn=f1[0]+".pdf"

        
    return render_template('view_candidate.html',cid=cid,data=data,fn=fn,s1=s1)

@app.route('/view_candidate1',methods=['POST','GET'])
def view_candidate1():
    msg=""
    cid=""
    uname=""
    edata=[]
    s1=""
    fn=""
    
    if 'username' in session:
        uname = session['username']
    
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_candidate where username=%s ",(uname,))
    data = mycursor.fetchone()

    if data[25]=="":
        s=1
    else:
        s1="1"
        f1=data[25].split(".")
        fn=f1[0]+".pdf"

        
    return render_template('view_candidate1.html',cid=cid,data=data,fn=fn,s1=s1)

@app.route('/interview_list',methods=['POST','GET'])
def interview_list():
    msg=""
    uname=""
    edata=[]
    s1=""
    
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute("SELECT * FROM vh_vacancy where hr_id=%s order by id desc",(uname,))
    rs1 = mycursor.fetchone()
    vid=rs1[0]
    print(vid)
    
    mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status=1 && p.vacancy_id=%s",(vid,))
    mdata = mycursor.fetchall()


    return render_template('interview_list.html',vid=vid,mdata=mdata,edata=edata,s1=s1)

@app.route('/selected_list',methods=['POST','GET'])
def selected_list():
    msg=""
    uname=""
    edata=[]
    s1=""
    
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute("SELECT * FROM vh_vacancy where hr_id=%s order by id desc",(uname,))
    rs1 = mycursor.fetchone()
    vid=rs1[0]
    print(vid)
    #1-inw select,2-inw going,3-select,4-reject,5-joined
    
    mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status=3 && p.vacancy_id=%s",(vid,))
    mdata = mycursor.fetchall()


    return render_template('selected_list.html',vid=vid,mdata=mdata,edata=edata,s1=s1)

@app.route('/admin_selected',methods=['POST','GET'])
def admin_selected():
    msg=""
    uname=""
    edata=[]
    s1=""
    
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute("SELECT * FROM vh_vacancy order by id desc")
    rs1 = mycursor.fetchone()
    vid=rs1[0]
    print(vid)
    #1-inw select,2-inw going,3-select,4-reject,5-joined
    
    mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status>=3 && p.vacancy_id=%s",(vid,))
    mdata = mycursor.fetchall()


    return render_template('admin_selected.html',vid=vid,mdata=mdata,edata=edata,s1=s1)

@app.route('/rejected_list',methods=['POST','GET'])
def rejected_list():
    msg=""
    uname=""
    edata=[]
    s1=""
    
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute("SELECT * FROM vh_vacancy where hr_id=%s order by id desc",(uname,))
    rs1 = mycursor.fetchone()
    vid=rs1[0]
    print(vid)
    #1-inw select,2-inw going,3-select,4-reject,5-joined
    
    mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status=4 && p.vacancy_id=%s",(vid,))
    mdata = mycursor.fetchall()


    return render_template('rejected_list.html',vid=vid,mdata=mdata,edata=edata,s1=s1)

@app.route('/joined_list',methods=['POST','GET'])
def joined_list():
    msg=""
    uname=""
    mdata=[]
    s1=""
    
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor(buffered=True)

    
    mycursor.execute("SELECT * FROM vh_joined p,vh_candidate c where p.candidate=c.username && p.hr_id=%s",(uname,))
    mdata = mycursor.fetchall()


    return render_template('joined_list.html',mdata=mdata,s1=s1)

@app.route('/job_details',methods=['POST','GET'])
def job_details():
    msg=""
    email=""
    mess=""
    act=request.args.get("act")
    uname=""
    data=[]
    mdata=[]
    s1=""
    s2=""

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_candidate where username=%s",(uname, ))
    data = mycursor.fetchone()
    
    mycursor.execute("SELECT * FROM vh_joined p,vh_candidate c where p.candidate=c.username && p.candidate=%s",(uname,))
    mdat = mycursor.fetchall()

    for mm in mdat:
        dt=[]

        dt.append(mm[0])
        dt.append(mm[1])
        dt.append(mm[2])
        dt.append(mm[3])
        dt.append(mm[4])
        dt.append(mm[5])
        dt.append(mm[6])
        dt.append(mm[7])
        dt.append(mm[8])
        dt.append(mm[9])
        dt.append(mm[10])
        dt.append(mm[11])
        dt.append(mm[13])
        dt.append(mm[12])
        vid=mm[1]
        mycursor.execute("SELECT * FROM vh_profile_matched where id=%s",(mm[2], ))
        dd1 = mycursor.fetchone()
        
        mycursor.execute("SELECT * FROM vh_vacancy where id=%s",(dd1[1], ))
        dd = mycursor.fetchone()
        company=dd[21]
        dt.append(company)
        mdata.append(dt)

    return render_template('job_details.html',msg=msg,act=act,data=data,mdata=mdata)

@app.route('/hod_home',methods=['POST','GET'])
def hod_home():
    msg=""
    uname=""
    vid=request.args.get("vid")
    act=""
    s1=""
    mess=""
    email=""
    data1=[]
    data=[]

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_hod where staff_id=%s",(uname, ))
    data1 = mycursor.fetchone()

    mycursor.execute("SELECT * FROM vh_dept")
    drow = mycursor.fetchall()

    if request.method=='POST':
        dept=request.form['dept']
        mycursor.execute("SELECT count(*) FROM vh_candidate where dept=%s",(dept,))
        cnt = mycursor.fetchone()[0]
        if cnt>0:
            s1="1"
            mycursor.execute("SELECT * FROM vh_candidate where dept=%s",(dept,))
            data = mycursor.fetchall()
    

    

    return render_template('hod_home.html',msg=msg,act=act,data1=data1,data=data,drow=drow,s1=s1)

@app.route('/hod_vacancy',methods=['POST','GET'])
def hod_vacancy():
    msg=""
    uname=""
    vid=request.args.get("vid")
    act=""
    st=""
    mess=""
    email=""
    data1=[]

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_hod where staff_id=%s",(uname, ))
    data1 = mycursor.fetchone()

    mycursor.execute("SELECT * FROM vh_vacancy order by id desc")
    data = mycursor.fetchall()
    

    return render_template('hod_vacancy.html',msg=msg,act=act,data1=data1,data=data)

@app.route('/pc_home',methods=['POST','GET'])
def pc_home():
    msg=""
    uname=""
    act=""
    st=""
    mess=""
    email=""
    data1=[]

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_placement where staff_id=%s",(uname, ))
    data1 = mycursor.fetchone()

    mycursor.execute("SELECT * FROM vh_job_provider_register")
    data = mycursor.fetchall()


    mycursor.execute("SELECT max(id)+1 FROM vh_job_provider_register")
    maxid = mycursor.fetchone()[0]
    if maxid is None:
        maxid=1

    
    v1=str(maxid)
    val=v1.zfill(3)
    hr_id="R"+val

    
    if request.method=='POST':
        company_name=request.form['company_name']
        hr_name=request.form['hr_name']
        services=request.form['services']
        
        mobile=request.form['mobile']
        email=request.form['email']
        location=request.form['location']
        
      
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        

        mycursor.execute("SELECT count(*) FROM vh_job_provider_register where hr_id=%s order by id desc",(hr_id, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            

            #rn=randint(100,999)
            #p1=mobile[7:10]
            na=hr_name[0:3]
            
            pass1=na+"@123"

            link="http://localhost:5000/login_company"
            
            sql = "INSERT INTO vh_job_provider_register(id,hr_name,company_name,services,location,mobile, email, hr_id,password,approved_status,register_date,placement) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s,%s,%s)"
            val = (maxid,hr_name,company_name,services,location,mobile,email,hr_id,pass1,'1',rdate,uname)
            print(sql)
            mycursor.execute(sql, val)
            mydb.commit()            
    

            mess="Dear "+hr_name+", Company:"+company_name+", Recruiter ID:"+hr_id+", Paasword: "+pass1+", Link: "+link
            msg='success'

            #xgboost
            #if mycursor.rowcount==1:
            #    result="Registered Success"
            
        else:
            msg="fail"
    

    return render_template('pc_home.html',msg=msg,act=act,data1=data1,data=data,hr_id=hr_id,mess=mess,email=email)

@app.route('/pc_vacancy',methods=['POST','GET'])
def pc_vacancy():
    msg=""
    uname=""
    vid=request.args.get("vid")
    act=""
    st=""
    mess=""
    email=""
    data1=[]

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_placement where staff_id=%s",(uname, ))
    data1 = mycursor.fetchone()

    mycursor.execute("SELECT * FROM vh_vacancy where id=%s order by id desc",(vid,))
    data = mycursor.fetchall()
    

    

    return render_template('pc_vacancy.html',msg=msg,act=act,data1=data1,data=data)



#######################
def tokenizer(text):
    for token in wordpunct_tokenize(text):
        if token not in ENGLISH_STOP_WORDS:
            tag = tagger_mem(frozenset({token}))
            yield lemmatize_mem(token, tags.get(tag[0][1],  wn.NOUN))

    # Pipeline definition
    pipeline = Pipeline([
        ('vectorizer', TfidfVectorizer(
            tokenizer=tokenizer,
            ngram_range=(1, 2),
            stop_words=ENGLISH_STOP_WORDS,
            sublinear_tf=True,
            min_df=0.00009
        )),
        ('classifier', SGDClassifier(
            alpha=1e-4, n_jobs=-1
        )),
    ])

    # Cross validate using k-fold
    y_pred = cross_val_predict(
        pipeline, dataset.get('data'),
        y=dataset.get('target'),
        cv=10, n_jobs=-1, verbose=20
    )

    # Compute precison, recall and f1 scode.
    cr = classification_report(
        dataset.get('target'), y_pred,
        target_names=dataset.get('target_names'),
        digits=3
    )

    # Confusion matrix
    cm = confusion_matrix(dataset.get('target'), y_pred)

    # Get max length of category names for printing
    label_length = len(
        sorted(dataset['target_names'], key=len, reverse=True)[0]
    )

    # Make shortened labels for plotting
    short_labels = []
    for i in dataset['target_names']:
        short_labels.append(
            ' '.join(map(lambda x: x[:3].strip(), i.split(' > ')))
        )

    # Printing Classification Report
    print('{label:>{length}}'.format(
        label='Classification Report',
        length=label_length
    ), cr, sep='\n')

    # Pretty printing confusion matrix
    print('{label:>{length}}\n'.format(
        label='Confusion Matrix',
        length=abs(label_length - 50)
    ))
    for index, val in enumerate(cm):
        print(
            '{label:>{length}} {prediction}'.format(
                length=abs(label_length - 50),
                label=short_labels[index],
                prediction=''.join(map(lambda x: '{:>5}'.format(x), val))
            )
        )
#XG Boost
def XGBoost():
    my_model = XGBRegressor()
    # Add silent=True to avoid printing out updates with each cycle
    my_model.fit(train_X, train_y, verbose=False)
    predictions = my_model.predict(test_X)

    from sklearn.metrics import mean_absolute_error
    print("Mean Absolute Error : " + str(mean_absolute_error(predictions, test_y)))
    my_model = XGBRegressor(n_estimators=1000)
    my_model.fit(train_X, train_y, early_stopping_rounds=5, 
                 eval_set=[(test_X, test_y)], verbose=False)
    my_model = XGBRegressor(n_estimators=1000, learning_rate=0.05)
    my_model.fit(train_X, train_y, early_stopping_rounds=5, 
                 eval_set=[(test_X, test_y)], verbose=False)

###########
@app.route('/pc_matched',methods=['POST','GET'])
def pc_matched():
    msg=""
    uname=""
    vid=request.args.get("vid")
    act=""
    st=""
    stt1=""
    stt2=""
    dept=""
    mdata=[]
    mess=""
    email=""
    data1=[]
    edata=[]
    

    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_dept")
    drow = mycursor.fetchall()

    
    mycursor.execute("SELECT * FROM vh_placement where staff_id=%s",(uname, ))
    data1 = mycursor.fetchone()

    mycursor.execute("SELECT * FROM vh_vacancy where id=%s",(vid,))
    data = mycursor.fetchall()

    if request.method=='POST':
        dept=request.form['dept']
        t1=request.form['t1']
        mycursor.execute("SELECT * FROM vh_candidate where dept=%s",(dept,))
        d1 = mycursor.fetchall()

        mycursor.execute("SELECT * FROM vh_vacancy where id=%s",(vid,))
        rs1 = mycursor.fetchone()
        dd2=[]

        now1 = datetime.datetime.now()
        rtime=now1.strftime("%H:%M")
        rtime1=rtime.split(':')
        rmin=int(rtime1[1])

        ##
        sk=rs1[11]
        sk1=sk.split(",")

        ##number of profile matched
        vn=0
        ##
        
        f=0
        k=0
        for rs in d1:
            dd1=[]

            s1=""
            s2=""
            s3=""
            s4=""
            s5=""
            s6=""
            ##########
            if rs[25]=="":
                s=1
            else:
                text = docx2txt.process("static/upload/"+rs[25], "/tmp/img_dir") 
                g=0
                for sk2 in sk1:
                    
                    if sk2 in text:
                        #print(sk2)
                        g+=1
                print("ggg")
                print(g)
            ##########
                
            ##gender
            if rs1[2]=="Any":
                s1="1"
            elif rs1[2]==rs[2]:
                s1="1"
            else:
                s1="2"
            ##mark1
            if rs1[3]<=rs[12]:
                s2="1"
            else:
                s2="2"
            ##mark2
            if rs[14]>0:
                if rs1[4]<=rs[14]:
                    s3="1"
                else:
                    s3="2"
            else:
                s3="1"
            ##level
            qx=0
            qx2=0
            qx3=0
            d2=0
            qx22=0
            qx33=0
            mycursor.execute("SELECT count(*) FROM vh_mark where regno=%s",(rs[6],))
            d2 = mycursor.fetchone()[0]
            if d2>0:
                
                mycursor.execute("SELECT count(*) FROM vh_mark where regno=%s",(rs[6],))
                qx = mycursor.fetchone()[0]

                mycursor.execute("SELECT sum(mark) FROM vh_mark where regno=%s",(rs[6],))
                qx2 = mycursor.fetchone()[0]

                mycursor.execute("SELECT sum(arrear) FROM vh_mark where regno=%s",(rs[6],))
                qx3 = mycursor.fetchone()[0]

            if qx2>0:
                qx22=qx2/d2

            if qx3>0:
                qx33=qx3/d2

            
            '''if rs1[5]=="Any":
                s4="1"
            elif qx>0:
                s4="1"
            else:
                s4="2"'''
            ##mark
            if qx22>=rs1[7]:
                
                s5="1"
            else:
                s5="2"

            #arrear
            if qx33<=rs1[8]:
                s6="1"
            else:
                s6="2"
            

            # and s6=="1" and s7=="1"
            # and s4=="1" and s5=="1" and s6=="1" and g>0
            if s1=="1" and s2=="1" and s3=="1" and s5=="1" and s6=="1":
                #print(rs[8]+" "+rs1[1])
                #dd1.append(rs[8])
                #dd1.append(rs[1])
                #dd1.append(rs1[1])
                #data4.append(dd1)
                #print(rs1[1])
                
                #dd1.append(rs1[6])
                #dd1.append(rs1[1])
                #dd1.append(rs1[5])
                #data3.append(dd1)
                

                mycursor.execute("SELECT count(*) FROM vh_profile_matched where vacancy_id=%s && username=%s",(rs1[0],rs[6]))
                ucnt = mycursor.fetchone()[0]
                if ucnt==0:

                    print(rs[6])
                    print(s1)
                    print(s2)
                    print(s3)
                    print(s4)
                    print(s5)
                    print(s6)

                    mycursor.execute("SELECT count(*) FROM vh_candidate where username=%s && status=0",(rs[6],))
                    cn = mycursor.fetchone()[0]
                    if cn>0:
                        vn+=1
                        mycursor.execute("SELECT max(id)+1 FROM vh_profile_matched")
                        maxid = mycursor.fetchone()[0]
                        if maxid is None:
                            maxid=1

                        '''sdate=rs1[14]
                        stime=rs1[16]

                        hh=int(stime)
                        

                        rrr=[10,20,30]
                        rn=randint(1,3)
                        rn1=rn-1

                        itime=""
                        mm2=0
                        hh2=0
                        mm=rmin+rrr[rn1]
                        if mm>60:
                            hh2=hh+1
                            mm2=mm-60
                            itime=str(hh2)+":"+str(mm2)
                        else:
                            itime=str(hh)+":"+str(mm)'''

                        
                        sql = "INSERT INTO vh_profile_matched(id,vacancy_id,username,interview_date,interview_time,minutes) VALUES (%s, %s, %s,%s,%s,%s)"
                        val = (maxid,rs1[0],rs[6],'','','0')
                        
                        mycursor.execute(sql, val)
                        mydb.commit()

        ######
        mycursor.execute("SELECT count(*) FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status=0 && p.vacancy_id=%s && c.dept=%s",(vid,dept))
        cnt = mycursor.fetchone()[0]
        if cnt>0:
            stt1="1"
            mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status=0 && p.vacancy_id=%s && c.dept=%s",(vid,dept))
            mdata = mycursor.fetchall()
        ####
        print("t1=")
        print(t1)
        if t1=="2":
            uu=request.form.getlist('c1[]')
            dept=request.form['dept']
            stt2="1"
            for u1 in uu:
                dt=[]

                
                mycursor.execute("update vh_profile_matched set interview_status=1 where vacancy_id=%s && username=%s",(vid,u1))
                mydb.commit()

                mycursor.execute("SELECT * FROM vh_candidate where username=%s ",(u1,))
                d2 = mycursor.fetchone()
                email=d2[5]
                name=d2[1]
                print(name)
                print(email)

                mess="Dear "+name+", You are Shrtlisted for Campus Interview"
                dt.append(email)
                dt.append(mess)
                edata.append(dt)
    
    

    return render_template('pc_matched.html',msg=msg,act=act,data1=data1,data=data,mdata=mdata,stt1=stt1,drow=drow,vid=vid,stt2=stt2,dept=dept)


@app.route('/pc_shortlist',methods=['POST','GET'])
def pc_shortlist():
    msg=""
    uname=""
    vid=request.args.get("vid")
    act=request.args.get("act")
    st=""
    stt1=""
    stt2=""
    dept=""
    mdata=[]
    mess=""
    email=""
    data1=[]
    edata=[]
    if 'username' in session:
        uname = session['username']
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM vh_dept")
    drow = mycursor.fetchall()

    
    
    mycursor.execute("SELECT * FROM vh_placement where staff_id=%s",(uname, ))
    data1 = mycursor.fetchone()

    mycursor.execute("SELECT * FROM vh_vacancy where id=%s",(vid,))
    data = mycursor.fetchall()


    mycursor.execute("SELECT count(*) FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status=1 && p.vacancy_id=%s",(vid,))
    cnt = mycursor.fetchone()[0]
    if cnt>0:
        stt1="1"
        mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status=1 && p.vacancy_id=%s",(vid,))
        mdata = mycursor.fetchall()

    if request.method=='POST':
        stt2="1"
        
        inw_date=request.form['inw_date']
        start_time=request.form['start_time']
        end_time=request.form['end_time']
        venue=request.form['venue']
        mycursor.execute("update vh_vacancy set inw_start_date=%s,start_time=%s,end_time=%s,program=%s where id=%s",(inw_date,start_time,end_time,venue,vid))
        mydb.commit()

        for md in mdata:
            dt=[]
            mycursor.execute("SELECT * FROM vh_candidate where username=%s ",(md[2],))
            d2 = mycursor.fetchone()
            email=d2[5]
            name=d2[1]
            print(name)
            print(email)

            mess="Campus Interview on "+inw_date+", Time: "+start_time+" to "+end_time+", Venue:"+venue
            dt.append(email)
            dt.append(mess)
            edata.append(dt)
    

    return render_template('pc_shortlist.html',msg=msg,act=act,data1=data1,data=data,mdata=mdata,stt1=stt1,drow=drow,vid=vid,stt2=stt2,dept=dept)



@app.route('/pc_attend',methods=['POST','GET'])
def pc_attend():
    msg=""
    uname=""
    edata=[]
    stt1=""
    vid=request.args.get("vid")
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_vacancy where id=%s && hr_id=%s",(vid,uname))
    rs1 = mycursor.fetchone()
    #n=rs1[18]

    
    mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status=2 && p.vacancy_id=%s",(vid,))
    mdata = mycursor.fetchall()

    if request.method=='POST':
            uu=request.form.getlist('c1[]')
            
            stt1="1"
            for u1 in uu:
                dt=[]

  

    return render_template('pc_attend.html',vid=vid,mdata=mdata,edata=edata,stt1=stt1)

@app.route('/pc_selected',methods=['POST','GET'])
def pc_selected():
    msg=""
    uname=""
    edata=[]
    stt1=""
    vid=request.args.get("vid")
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_vacancy where id=%s",(vid,))
    rs1 = mycursor.fetchone()
    n=rs1[18]

    
    mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status>=3 && p.vacancy_id=%s",(vid,))
    mdata = mycursor.fetchall()

    if request.method=='POST':
            uu=request.form.getlist('c1[]')
          
  

    return render_template('pc_selected.html',vid=vid,mdata=mdata,edata=edata,stt1=stt1)

@app.route('/hr_shortlist',methods=['POST','GET'])
def hr_shortlist():
    msg=""
    uname=""
    edata=[]
    stt1=""
    vid=request.args.get("vid")
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_vacancy where id=%s && hr_id=%s",(vid,uname))
    rs1 = mycursor.fetchone()
    n=rs1[18]

    
    mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status=1 && p.vacancy_id=%s",(vid,))
    mdata = mycursor.fetchall()

    if request.method=='POST':
            uu=request.form.getlist('c1[]')
            stt1="1"
            for u1 in uu:
                dt=[]

                
                mycursor.execute("update vh_profile_matched set interview_status=2 where vacancy_id=%s && username=%s",(vid,u1))
                mydb.commit()
  
  

    return render_template('hr_shortlist.html',vid=vid,mdata=mdata,edata=edata,stt1=stt1)

@app.route('/hr_attend',methods=['POST','GET'])
def hr_attend():
    msg=""
    uname=""
    edata=[]
    stt1=""
    vid=request.args.get("vid")
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_vacancy where id=%s && hr_id=%s",(vid,uname))
    rs1 = mycursor.fetchone()
    n=rs1[18]

    
    mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status=2 && p.vacancy_id=%s",(vid,))
    mdata = mycursor.fetchall()

    if request.method=='POST':
            uu=request.form.getlist('c1[]')
            
            stt1="1"
            for u1 in uu:
                dt=[]

                
                mycursor.execute("update vh_profile_matched set interview_status=3 where vacancy_id=%s && username=%s",(vid,u1))
                mydb.commit()
               
                mycursor.execute("SELECT * FROM vh_candidate where username=%s ",(u1,))
                d2 = mycursor.fetchone()
                email=d2[5]
                name=d2[1]
                print(name)
                print(email)

                mess="Dear "+name+", You are selected in Campus Interview"
                dt.append(email)
                dt.append(mess)
                edata.append(dt)
  

    return render_template('hr_attend.html',vid=vid,mdata=mdata,edata=edata,stt1=stt1)

@app.route('/hr_selected',methods=['POST','GET'])
def hr_selected():
    msg=""
    uname=""
    edata=[]
    stt1=""
    vid=request.args.get("vid")
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_vacancy where id=%s && hr_id=%s",(vid,uname))
    rs1 = mycursor.fetchone()
    n=rs1[18]

    
    mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status>=3 && p.vacancy_id=%s",(vid,))
    mdata = mycursor.fetchall()

    if request.method=='POST':
            uu=request.form.getlist('c1[]')
          
  

    return render_template('hr_selected.html',vid=vid,mdata=mdata,edata=edata,stt1=stt1)

##########
@app.route('/hod_shortlist',methods=['POST','GET'])
def hod_shortlist():
    msg=""
    uname=""
    edata=[]
    stt1=""
    vid=request.args.get("vid")
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_vacancy where id=%s ",(vid,))
    rs1 = mycursor.fetchone()
    n=rs1[18]

    
    mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status=1 && p.vacancy_id=%s",(vid,))
    mdata = mycursor.fetchall()

 
  

    return render_template('hod_shortlist.html',vid=vid,mdata=mdata,edata=edata,stt1=stt1)

@app.route('/hod_attend',methods=['POST','GET'])
def hod_attend():
    msg=""
    uname=""
    edata=[]
    stt1=""
    vid=request.args.get("vid")
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_vacancy where id=%s ",(vid,))
    rs1 = mycursor.fetchone()
    n=rs1[18]

    
    mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status=2 && p.vacancy_id=%s",(vid,))
    mdata = mycursor.fetchall()

    
  

    return render_template('hod_attend.html',vid=vid,mdata=mdata,edata=edata,stt1=stt1)

@app.route('/hod_selected',methods=['POST','GET'])
def hod_selected():
    msg=""
    uname=""
    edata=[]
    stt1=""
    vid=request.args.get("vid")
    if 'username' in session:
        uname = session['username']

    now1 = datetime.datetime.now()
    rtime=now1.strftime("%H:%M")
    rtime1=rtime.split(':')
    rmin=int(rtime1[1])

    
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM vh_vacancy where id=%s",(vid,))
    rs1 = mycursor.fetchone()
    n=rs1[18]

    
    mycursor.execute("SELECT * FROM vh_profile_matched p,vh_candidate c where p.username=c.username && p.interview_status>=3 && p.vacancy_id=%s",(vid,))
    mdata = mycursor.fetchall()


    return render_template('hod_selected.html',vid=vid,mdata=mdata,edata=edata,stt1=stt1)

@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    #session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=5000)

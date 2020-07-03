from flask import render_template, request, redirect, url_for, session, flash
from functools import wraps
from facebok import app,db
import gc

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'loggedin' in session:
            return f(*args, **kwargs)
        else:
            flash("you need to login ")
            return redirect(url_for(index))
    return wrap


@app.route('/', methods=['GET','POST'])
def index():
    msg=''
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        cur = db.cursor(dictionary=True,buffered=True)
        cur.execute("SELECT * FROM users WHERE user_name = %s AND user_pass = %s",(name,password))
        user = cur.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user['user_id']
            session['username'] = user['user_name']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'

    if 'loggedin' in session:
        return redirect(url_for('home'))
    else:
        return render_template('index.html', msg=msg, title='index')



@app.route('/logout')
@login_required
def logout():
    session.clear()
    gc.collect()
    return redirect(url_for('index'))



@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        dob = request.form.get('date_birth')
        cur = db.cursor(dictionary=True)
        cur.execute("INSERT INTO users(user_name, user_email, user_pass, user_phone, user_dob) VALUES (%s,%s,%s,%s,%s)",(name,email,password,phone,dob))
        db.commit()
        cur.close()
        return redirect(url_for('index'))
    return render_template('signup.html',title='register')

@app.route('/home')
@login_required
def home():
    cur = db.cursor()
    cur.execute(" SELECT posts.post_title, users.user_name FROM posts JOIN users ON users.user_id=posts.user_id ")
    posts = cur.fetchall()
    return render_template('home.html', posts= posts, title='Home')


@app.route('/post', methods=['GET','POST'])
@login_required
def create_post():
    if request.method=='POST':
        title = request.form.get('title')
        cur = db.cursor(dictionary=True,buffered=True)
        cur.execute("INSERT INTO posts(post_title,user_id) VALUES (%s,%s)",(title,session['id']))
        db.commit()
        cur.close()
        return redirect(url_for('home'))
    return render_template('post.html', title='Create Post')


'''
PROFILE PAGE

'''



@app.route('/profile')
@login_required
def profile():
    cur = db.cursor()
    cur.execute(" SELECT posts.post_id, posts.post_title, users.user_name FROM posts JOIN users ON users.user_id=posts.user_id WHERE users.user_id='%s'",(session['id'],))
    posts = cur.fetchall()
    cur.execute(" SELECT * FROM users WHERE users.user_id='%s'",(session['id'],) )
    users = cur.fetchall()
    return render_template('profile.html', posts=posts, users=users, title='Profile')




@app.route('/update/<post_id>', methods=['GET','POST'])
@login_required
def update(post_id):
    if request.method == 'POST':
        title = request.form.get('title')
        cur = db.cursor()
        cur.execute("UPDATE posts SET post_title=%s WHERE post_id=%s",(title,post_id))
        cur.execute("SELECT * FROM posts WHERE post_id=%s",(post_id,))
        current_post = cur.fetchall()
        db.commit()
        cur.close()
        return redirect(url_for('profile'))

    if request.method == 'GET':
        cur = db.cursor()
        cur.execute("SELECT * FROM posts WHERE post_id=%s",(post_id,))
        current_post = cur.fetchall()
        db.commit()
        cur.close()
        return render_template('update.html',current_post=current_post, title='Update Post')


@app.route('/delete/<post_id>', methods=['GET','POST'])
@login_required
def delete(post_id):
    if request.method == 'GET':
        cur = db.cursor()
        cur.execute("DELETE FROM posts where post_id=%s",(post_id,))
        db.commit()
        cur.close()
        return redirect(url_for('profile'))



'''
    UPDATE PROFILE 
'''

@app.route('/updatepro/<user_id>', methods=['GET','POST'])
@login_required
def update_profile(user_id):
    if request.method=='GET':
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE user_id=%s",(user_id,))
        current_user = cur.fetchall()
        db.commit()
        cur.close()
        return render_template('updatepro.html', current_user=current_user)
    
    if request.method=='POST':
        name = request.form.get('username')
        phone = request.form.get('phone')
        dob = request.form.get('date_birth')
        profile_pic = request.form.get('profile_pic')
        cur = db.cursor()
        cur.execute("UPDATE users SET user_name=%s, user_phone=%s, user_dob=%s, profile_image=%s WHERE user_id=%s",(name, phone, dob, profile_pic, user_id))
        db.commit()
        cur.close()
        return redirect(url_for('profile'))


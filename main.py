from flask import Flask,render_template,request,flash,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'MLXH243GssUWwKdTWS7FDhdwYF56wPj8'
db_name='library.db'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+db_name
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

# engine = create_engine('sqlite://', echo=False)

class Books(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(80),nullable=False)
    is_issued=db.Column(db.Boolean)

class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(80),nullable=False)
    password = db.Column(db.String(80),nullable=False)
    book1=db.Column(db.String(80))
    issue1 = db.Column(db.String(80))
    book2=db.Column(db.String(80))
    issue2 = db.Column(db.String(80))
    book3=db.Column(db.String(80))
    issue3 = db.Column(db.String(80))
    number = db.Column(db.Integer)


app.app_context().push()

@app.before_first_request
def create_tables():
    db.create_all()


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        name=request.form.get('name')
        password=request.form.get('password')
        user=User.query.filter(User.name==name).first()
        if name=='admin' and password=='711':
            return redirect('/admin')
        elif user and password == user.password:
            return redirect('/'+str(user.id))
        else: 
            flash('Incorrect Credentials')
    return render_template('index.html')

@app.route('/admin')
def admin():
    books = Books.query.all()
    studs = User.query.all()
    for stud in studs:
        print(stud.id, stud.name)
    return render_template('admin.html',books=books,studs=studs)

@app.route('/addbook', methods=['GET', 'POST'])
def addbook():
    bookname = request.form.get('book')
    books =Books.query.filter(Books.name == bookname).first()
    if not books and bookname != '':
        book = Books(name=bookname.lower(), is_issued=False)
        db.session.add(book)
        db.session.commit()
        flash(f'Book {bookname} added Successfully')
    else:
        flash('Error adding book')
        flash('Either book already exists or Incorrect Input')
    return redirect('/admin')
    
@app.route('/editbook/<id>', methods=['GET', 'POST'])
def editbook(id):
    book = Books.query.get(id)
    # print(request.form)
    name = request.form.get('name')
    book1 = Books.query.filter(Books.name==name).all()
    if not book1:
        book.name = name
        db.session.commit()
    else:
        flash('Bookname already exists')
    return redirect('/admin')

@app.route('/deletebook/<id>')
def delete_usr(id):
    book = Books.query.get(id)
    db.session.delete(book)
    db.session.commit()
    return redirect('/admin')

@app.route('/create', methods=['GET',"POST"])
def create_student():
    if request.method=='POST':
        name=request.form.get('name')
        password=request.form.get('password')
        user=User.query.filter(User.name==name).first()
        if not user and name!='admin' and name!='' and password!='':
            user = User(name=name,password=password, book1='',issue1='', book2='',issue2='', book3='',issue3='', number=0)
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        else:
            flash('Incorrect Input')
    return render_template('create.html')

@app.route('/searchbooks', methods=['GET',"POST"])
def search_books():
    name = request.form.get('name')
    book1 = Books.query.filter(Books.name==name).all()
    if name.lower() == 'all':
        return redirect('/admin')
    elif not book1:
        flash('No such book exists')
    return render_template('admin.html', books=book1)


@app.route('/issuebook', methods=['GET', 'POST'])
def issuebook():
    if request.method == 'POST':
        book_id = request.form.get('books')
        stud_id = request.form.get('studs')
        # print(book_id,stud_id)
        
        stud = User.query.filter(User.id==stud_id).first()
        book=Books.query.filter(Books.id==book_id).first()
        if book == None or stud==None:
            flash('Incorrect Input')
            return redirect('/issuebook')
        print(stud)
        if stud.number < 3:
            if stud.book1 == '':
                stud.book1=book_id
                stud.issue1 = date.today()
                stud.number+=1
                book.is_issued = True
            elif stud.book2 == '':
                stud.book2=book_id
                stud.issue2 = date.today()
                stud.number+=1
                book.is_issued = True
            elif stud.book3 == '':
                stud.book3=book_id
                stud.issue3 = date.today()
                stud.number+=1
                book.is_issued = True
            flash('Book Issued Successfully')
            
        else:
            flash('Sorry! You have already issued 3 books')
                # return redirect('/issuebook')
        db.session.commit()
    books = Books.query.filter(Books.is_issued==False)
    studs = User.query.all()
    return render_template('issue.html',books=books,studs=studs)

@app.route('/returnbook', methods=['GET', 'POST'])
def returnbook():
    id = request.form.get('stud_name')
    stud = User.query.filter(User.id==id).first()
    if stud==None:
        flash('Incorrect Input')
        return redirect('/admin')

    if stud.book1 == '' and stud.book2 == '' and stud.book3=='':
        flash('No Books issued')
        return redirect('/admin')
    book1 = stud.book1
    book2=stud.book2
    book3=stud.book3
    if book1:
        book1 = Books.query.filter(Books.id==int(book1)).first()
    if book2:
        book2 = Books.query.filter(Books.id==int(book2)).first()
    if book3:
        book3 = Books.query.filter(Books.id==int(book3)).first()
    return render_template('return.html',stud=stud,book1=book1,book2=book2,book3=book3)


@app.route('/returned', methods=['GET', 'POST'])
def returned():
    book_id = request.form.get('return')
    stud_id = request.form.get('stud_id')
    
    stud = User.query.filter(User.id==stud_id).first()
    book = Books.query.filter(Books.id==book_id).first()
    if book==None or stud==None:
        flash('Incorrect Input')
        return redirect('/admin')
    today = date.today()
    fine=0
    day=0
    if stud.book1 == book_id:
        date1 = date(int(stud.issue1[:4]),int(stud.issue1[5:7]),int(stud.issue1[8:]))
        # print(day)
        stud.book1=''
        stud.number-=1
        stud.issue1 = ''
        book.is_issued=False
    elif stud.book2 == book_id:
        date1 = date(int(stud.issue2[:4]),int(stud.issue2[5:7]),int(stud.issue2[8:]))
        stud.book2=''
        stud.number-=1
        stud.issue2 = ''
        book.is_issued=False
    elif stud.book3 == book_id:
        date1 = date(int(stud.issue3[:4]),int(stud.issue3[5:7]),int(stud.issue3[8:]))
        stud.book3=''
        stud.number-=1
        stud.issue3 = ''
        book.is_issued=False
    day = (today-date1).days
    if day > 10:
        fine=(day-10)*10
        flash(f'You have to pay ₹{fine} as fine as you are {day-10} days late')
    db.session.commit()
    return redirect('/admin')

@app.route('/editstud/<id>', methods=['GET', 'POST'])
def editstud(id):
    stud = User.query.get(id)
    # print(request.form)
    name = request.form.get('name')
    stud1 = User.query.filter(User.name==name).all()
    if not stud1:
        stud.name = name
        db.session.commit()
    else:
        flash('Student name already exists')
    return redirect('/admin')

@app.route('/deletestud/<id>')
def delete_stud(id):
    stud = User.query.get(id)
    db.session.delete(stud)
    db.session.commit()
    return redirect('/admin')

@app.route('/resetstud/<id>')
def reset_stud(id):
    stud = User.query.get(id)
    stud.name = 'reset'
    stud.password = '123'
    books = [stud.book1,stud.book2,stud.book3]
    stud.book1 = stud.book2 = stud.book3 = ''
    stud.issue1 = stud.issue2 = stud.issue3 = ''
    stud.number = 0
    for book in books:
        b = Books.query.filter(Books.id==book).first()
        if b:
            b.is_issued=False
    db.session.commit()
    return redirect('/admin')

@app.route('/deleteall')
def del_all():
    User.query.delete()
    db.session.commit()
    return redirect('/admin')

@app.route('/logout')
def logout():
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)

from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from passlib.hash import sha256_crypt
from functools import wraps

# Kullanıcı Giriş Decorator'ı
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın.","danger")
            return redirect(url_for("login"))
    return decorated_function

#admin giriş decoratoru

def admin_login_required(f):
    @wraps(f)
    def admin_decorated_function(*args, **kwargs):
        if "admin_logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın.","danger")
            return redirect(url_for("adminlogin"))
    return admin_decorated_function



# Kullanıcı Kayıt Formu
class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min = 0,max = 100)])
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min = 3,max = 100)])
    phone = StringField("İsim Soyisim",validators=[validators.Length(min = 0,max = 11)])
    email = StringField("Email Adresi",validators=[validators.Email(message = "Lütfen Geçerli Bir Email Adresi Girin...")])
    businnesid = StringField("Kurumsal Kimlik Numarası",validators=[validators.Length(min = 0,max = 11)])
    personalid = StringField("T.C Kimlik Numarası",validators=[validators.Length(min = 0,max = 11)])
    password = PasswordField("Parola:",validators=[
        validators.DataRequired(message = "Lütfen bir parola belirleyin"),
        validators.EqualTo(fieldname = "confirm",message="Parolanız Uyuşmuyor...")
    ])
    confirm = PasswordField("Parola Doğrula")
#kullanıcı login form
class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")


app = Flask(__name__)
app.secret_key= "reezo_start_up"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "reezoblog"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)





@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template ("about.html")


@app.route("/service")
def service():
    return render_template("service.html")

@app.route("/service/taraasistan")
def taraasistan():
    return render_template("taraasistan.html")

@app.route("/service/sem")
def sem():
    return render_template("sem.html")


@app.route("/support")
def support():
    return render_template("support.html")

@app.route("/comunication")
def com():
    return render_template("com.html")

@app.route("/ourteam")
def team():
    return render_template("ourteam.html")


#kullanıcı kayıt
@app.route("/register",methods = ["GET","POST"])
def register():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        
        phone = form.phone.data

        cursor = mysql.connection.cursor()

        sorgu = "Insert into reezoblog(name,email,username,password) VALUES(%s,%s,%s,%s)"

        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()

        cursor.close()
        flash("Başarıyla Kayıt Oldunuz...","success")
        return redirect(url_for("login"))
    else:
        return render_template("register.html",form = form)

#adminkayıt
@app.route("/adminregister",methods = ["GET","POST"])
def adminregister():
    form = RegisterForm(request.form)

    if request.method == "POST" and form.validate():
        personalid = form.personalid.data
        businnesid = form.businnesid.data
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        phone = form.phone.data

        cursor = mysql.connection.cursor()

        sorgu = "Insert into reezoadmins(businnesid,personalid,name,email,username,password,phone) VALUES(%s,%s,%s,%s,%s,%s,%s)"

        cursor.execute(sorgu,(businnesid,personalid,name,email,username,password,phone,))
        mysql.connection.commit()

        cursor.close()
        flash("Başarıyla Kayıt Oldunuz...","success")
        return redirect(url_for("adminlogin"))
    else:
        return render_template("adminregister.html",form = form)

#kullanıcı girişi
@app.route("/login",methods =["GET","POST"])
def login():
    form = LoginForm(request.form)
    if request.method == "POST":
       username = form.username.data
       password_entered = form.password.data

       cursor = mysql.connection.cursor()

       sorgu = "Select * From reezoblog where username = %s"

       result = cursor.execute(sorgu,(username,))

       if result > 0:
           data = cursor.fetchone()
           real_password = data["password"]
           if sha256_crypt.verify(password_entered,real_password):
               flash("Başarıyla Giriş Yaptınız...","success")

               session["logged_in"] = True
               session["username"] = username

               return redirect(url_for("eservice"))
           else:
               flash("Parolanızı Yanlış Girdiniz...","danger")
               return redirect(url_for("eservice")) 

       else:
           flash("Böyle bir kullanıcı bulunmuyor...","danger")
           return redirect(url_for("eservice"))

    
    return render_template("login.html",form = form)



#admin giriş formu
class AdminLoginForm(Form):
    businnesid= StringField("Kurumsal İD")
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")


#admin girişi
@app.route("/adminlogin",methods =["GET","POST"])

def adminlogin():
    form = AdminLoginForm(request.form)
    if request.method == "POST":
       username = form.username.data
       password_entered = form.password.data
       businnesid = form.businnesid.data
       
       cursor = mysql.connection.cursor()
       

       sorgu = "Select * From reezoadmins where businnesid = %s"
       sorgu1 = "Select * From reezoadmins where username = %s"

       result = cursor.execute(sorgu,(businnesid,))
       result1 = cursor.execute(sorgu1,(username,))

       if result and result1 > 0:
           data = cursor.fetchone()
           real_password = data["password"]
           if sha256_crypt.verify(password_entered,real_password):
               flash("Başarıyla Giriş Yaptınız...","success")

               session["admin_logged_in"] = True
               session["username"] = username

               return redirect(url_for("eservice"))
           else:
               flash("Parolanızı Yanlış Girdiniz...","danger")
               return redirect(url_for("eservice")) 

       else:
           flash("Böyle bir kullanıcı bulunmuyor...","danger")
           return redirect(url_for("eservice"))

    
    return render_template("adminlogin.html",form = form)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("eservice"))

@app.route("/eservice")
def eservice():
    return render_template("e-service.html")

@app.route("/articles")
@login_required
def articles1():
    return render_template("articles.html")

@app.route("/blog")
@login_required
def blog():
    return render_template("blog.html")

#kullanıcı yönetim paneli
@app.route("/dashboard")
@login_required  
def dashboard():
    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles where author = %s"

    result = cursor.execute(sorgu,(session["username"],))

    if result > 0:
        articles = cursor.fetchall()
        return render_template("dashboard.html",articles = articles)
    else:
        return render_template("dashboard.html")

#admin yönetim paneli
@app.route("/admindashboard")
@admin_login_required
def admindashboard():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From articles where author = %s"
    result = cursor.execute(sorgu,(session["username"],))
    if result > 0:
        articles = cursor.fetchall()
        return render_template("admindashboard.html",articles = articles)
    else:
        return render_template("admindashboard.html")
    
#kullanıcılar ana sayfa
@app.route("/admindashboard/users")
@admin_login_required
def users():
    cursor = mysql.connection.cursor()
    sorgu = "Select * From reezoblog"
    result = cursor.execute(sorgu)
    if result > 0:
        users = cursor.fetchall()
        return render_template("users.html",users = users)
    else:
        return render_template("users.html")


#detay sayfası
@app.route("/article/<string:id>")
@login_required
def article(id):
    cursor = mysql.connection.cursor()
    
    sorgu = "Select * from articles where id = %s"

    result = cursor.execute(sorgu,(id,))

    if result > 0:
        article = cursor.fetchone()
        return render_template("article.html",article = article)
    else:
        return render_template("article.html")

#makale silme
@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor = mysql.connection.cursor()

    sorgu = "Select * from articles where author = %s and id = %s"

    result = cursor.execute(sorgu,(session["username"],id))

    if result > 0:
        sorgu2 = "Delete from articles where id = %s"

        cursor.execute(sorgu2,(id,))

        mysql.connection.commit()

        return redirect(url_for("dashboard"))
    else:
        flash("Böyle bir makale yok veya bu işleme yetkiniz yok","danger")
        return redirect(url_for("index"))

#Makale Güncelleme
@app.route("/edit/<string:id>",methods = ["GET","POST"])
@login_required
def update(id):
   if request.method == "GET":
       cursor = mysql.connection.cursor()

       sorgu = "Select * from articles where id = %s and author = %s"
       result = cursor.execute(sorgu,(id,session["username"]))

       if result == 0:
           flash("Böyle bir makale yok veya bu işleme yetkiniz yok","danger")
           return redirect(url_for("index"))
       else:
           article = cursor.fetchone()
           form = ArticleForm()

           form.title.data = article["title"]
           form.content.data = article["content"]
           return render_template("update.html",form = form)

   else:
       # POST REQUEST
       form = ArticleForm(request.form)

       newTitle = form.title.data
       newContent = form.content.data

       sorgu2 = "Update articles Set title = %s,content = %s where id = %s "

       cursor = mysql.connection.cursor()

       cursor.execute(sorgu2,(newTitle,newContent,id))

       mysql.connection.commit()

       flash("Makale başarıyla güncellendi","success")

       return redirect(url_for("dashboard"))

       pass

class ArticleForm(Form):
    title = StringField("Makale Başlığı",validators=[validators.Length(min = 5,max = 100)]) 
    content = TextAreaField("Makale İçeriği",validators=[validators.Length(min = 10)])

class supportform(Form):
    name = StringField("Ad Soyad" , validators=[validators.Length(min = 0,max = 100)])
    phone = StringField("Telefon Numarası" , validators=[validators.Length(min = 0,max = 100)])
    email = StringField("E-Posta Adresi",validators=[validators.Email(message = "Lütfen Geçerli Bir Email Adresi Girin...")]) 
    content = TextAreaField("Makale İçeriği",validators=[validators.Length(min = 10)])

#supportform veri alma
@app.route("/support",methods = ["GET","POST"])
@login_required
def addsupportform():
    form = supportform(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data
        phone = form.phone.data
        email = form.email.data
        content = form.content.data

        cursor = mysql.connection.cursor()

        sorgu = "Insert into reezosupports(name,phone,email,content) VALUES(%s,%s,%s,%s)"

        cursor.execute(sorgu,(name,phone,email,content))

        mysql.connection.commit()

        cursor.close()

        flash("Mesajınız Başarı İle Gönderildi","success")

        return redirect(url_for("support"))

    return render_template("index.html",form = form)


#makale yazma
@app.route("/addarticle",methods = ["GET","POST"])
@login_required
def addarticle():
    form = ArticleForm(request.form)
    if request.method == "POST" and form.validate():
        title = form.title.data
        content = form.content.data

        cursor = mysql.connection.cursor()

        sorgu = "Insert into articles(title,author,content) VALUES(%s,%s,%s)"

        cursor.execute(sorgu,(title,session["username"],content))

        mysql.connection.commit()

        cursor.close()

        flash("Makale Başarıyla Eklendi","success")

        return redirect(url_for("dashboard"))

    return render_template("addarticle.html",form = form)


#makaleler ana sayfa
@app.route("/articles")
@login_required
def articles():
    cursor = mysql.connection.cursor()

    sorgu = "Select * From articles"

    result = cursor.execute(sorgu)

    if result > 0:
        articles = cursor.fetchall()
        return render_template("articles.html",articles = articles)
    else:
        return render_template("articles.html")




#e arşiv ana sayfası
@app.route("/archive")
@login_required
def archive():
    return render_template("archive.html")


# Arama URL
@app.route("/search",methods = ["GET","POST"])
@login_required
def search():
   if request.method == "GET":
       return redirect(url_for("index"))
   else:
       keyword = request.form.get("keyword")

       cursor = mysql.connection.cursor()

       sorgu = "Select * from articles where title like '%" + keyword +"%'"

       result = cursor.execute(sorgu)

       if result == 0:
           flash("Aranan kelimeye uygun makale bulunamadı...","warning")
           return redirect(url_for("articles"))
       else:
           articles = cursor.fetchall()

           return render_template("articles.html",articles = articles)



if __name__ == '__main__':
    app.run(debug = True)


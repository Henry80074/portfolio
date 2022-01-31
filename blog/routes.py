from flask import flash, render_template, url_for, request, redirect
from flask_admin.contrib.sqla import ModelView
from flask_mail import Message
from blog.models import User, Post, Comment, Rating
from blog import app, mail, limiter, flask_admin
from blog import db
from blog.forms import RegistrationForm, LoginForm, ContactForm, CommentForm, SortForm
from flask_login import login_user, logout_user, current_user
from statistics import mean
import json

flask_admin.add_view(ModelView(Post, db.session))

ROWS_PER_PAGE = 3


@app.route('/')
@app.route("/home",  methods=["GET", "POST"])
def home():
    sort_form = SortForm()
    sort_form.options.choices = [("date_desc","order by newest",), ('date_asc', "order by oldest",)]
    page = request.args.get('page', 1, type=int)
    order = request.args.get('order', '')
    # maintains order of posts on page refresh/ moving between paginated pages
    posts = Post.query.order_by(Post.date.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
    if order == 'date_asc':
        posts = Post.query.order_by(Post.date.asc()).paginate(page=page, per_page=ROWS_PER_PAGE)
    if order == 'date_desc' or None:
        posts = Post.query.order_by(Post.date.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
    # updates order of posts on submit
    if request.method == 'POST':
        val = sort_form.options.data
        if val == "date_desc":
            posts = Post.query.order_by(Post.date.desc()).paginate(page=page, per_page=ROWS_PER_PAGE)
        if val == "date_asc":
            posts = Post.query.order_by(Post.date.asc()).paginate(page=page, per_page=ROWS_PER_PAGE,)
        return render_template('home.html', posts=posts, form=sort_form, order=val, page_num=page)
    return render_template('home.html', posts=posts, form=sort_form, order=order,  page_num=page)


@app.route("/about")
def about():
    return render_template('about.html', title='About Me')


@app.route("/post/<int:post_id>")
def post(post_id):
    user_model = User
    comment_form = CommentForm()
    post = Post.query.get_or_404(post_id)
    user = current_user
    all_ratings = Rating.query.filter_by(post_id=post_id).all()
    rating_list = {}
    for i in all_ratings:
        try:
            rating_list[i.user_id] += i.rating
        except KeyError:
            rating_list[i.user_id] = i.rating
    critic_avg = None
    if rating_list:
        critic_avg = round(mean(rating_list.values())) # rounds rating to integer for easy display as stars,
    return render_template('post.html', critic_avg=critic_avg, user_model=user_model, post=post, comment_form=comment_form, user=user, all_ratings=json.dumps(rating_list))#change to rating_dict


@app.route("/post/<int:post_id>/comment", methods=["GET", "POST"])
@limiter.limit("10/hour")
def comment_post(post_id):
    form = CommentForm()
    if current_user.is_authenticated:
        author_id = current_user.id
        comment_body = request.form['body']
        if request.method == 'POST':
            if form.validate_on_submit():
                comment = Comment(body=comment_body, post_id=post_id, author=author_id)
                db.session.add(comment)
                db.session.commit()
                return redirect(url_for("post", post_id=post_id))
    else:
        return redirect(url_for("post", post_id=post_id))


@app.route("/post/<int:post_id>/rate", methods=["GET", "POST"])
@limiter.limit("60/hour")
def rate_post(post_id):
    if request.method == 'POST':
        val = request.form['val']
        user_id = current_user.id
        # check to see if user has already rated the post, enter rating into database if not true
        if Rating.query.filter_by(user_id=user_id, post_id=post_id).first() is None:
            new_rating = Rating(rating=val, post_id=post_id, user_id=user_id)
            db.session.add(new_rating)
            db.session.commit()
            return redirect(url_for("post", post_id=post_id))
        else:  # update the old rating with the new rating
            old_rating = Rating.query.filter_by(user_id=user_id,
                                            post_id=post_id).first()  # check- is this a robust way of making the query?
            old_rating.rating = val
            db.session.commit()
            print("updated")
            return redirect(url_for("post", post_id=post_id))


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    return render_template('contact.html', form=form)


@app.route('/contact/send', methods=['GET', 'POST'])
@limiter.limit("3/day")
def contact_send():
    form = ContactForm()
    if request.method == 'POST':
        if not form.validate():
            return render_template('contact.html', form=form)
        else:
            msg = Message(form.subject.data, sender=form.email.data, recipients=["flaskassignmenttest1@gmail.com"])
            msg.body = """
            From: %s <%s>
            %s
            """ % (form.name.data, form.email.data, form.message.data)
            mail.send(msg)
            return render_template('message.html', title='messagesent', message="Thanks for your email.", link="/home", page_name="Home")
    elif request.method == 'GET':
        return render_template('contact.html', form=form)


@app.route("/register",methods=['GET','POST'])
@limiter.limit("5/hour")
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User(firstname=form.firstname.data, password=form.password.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!')
            new_user = User.query.filter_by(firstname=form.firstname.data, email=form.email.data).first()
            login_user(new_user)
            return redirect(url_for('home'))
        else:
            flash('Sorry, there is a problem with your registration.')
            return render_template('register.html', form=form)
    return render_template('register.html',title='Register',form=form)


@app.route("/login",methods=['GET','POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None and user.verify_password(form.password.data):
                login_user(user)
                return redirect(url_for('home'))
            else:
                return redirect(url_for("loginfailed"))
    return render_template('login.html',title='Login',form=form)


@app.route("/logout")
def logout():
    logout_user()
    return render_template('message.html',title='LoggedOut', message="You have been logged out.", link="/home", page_name="Home")


@app.route("/loginfailed")
def loginfailed():
    return render_template('message.html', title='loginFailed', message="Incorrect email or password supplied.", link="/login", page_name="Login", HTMLclass="login_error")

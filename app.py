import json
import os
import uuid
from flask import Flask, flash, redirect, render_template, request, send_from_directory, session, url_for
from werkzeug.utils import secure_filename
from backend.auth import current_user, login_required, login_user, logout_user, register_user
from backend.config import MAX_UPLOAD_MB, SECRET_KEY, UPLOAD_DIR
from backend.db import get_recommendation, get_user_recommendations, init_db, save_recommendation
from backend.gemini_service import generate_recommendation
from backend.recommendation_service import enrich_result
from backend.utils import ALLOWED_CATEGORIES, clean_text, parse_budget

app=Flask(__name__,template_folder='frontend/templates',static_folder='frontend/static')
app.config['SECRET_KEY']=SECRET_KEY
app.config['MAX_CONTENT_LENGTH']=MAX_UPLOAD_MB*1024*1024
os.makedirs(UPLOAD_DIR,exist_ok=True)
init_db()

@app.context_processor
def inject_user(): return {'current_user':current_user()}

@app.route('/')
def index(): return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        name=clean_text(request.form.get('name'),80); email=clean_text(request.form.get('email'),120).lower(); password=request.form.get('password','')
        if len(name)<2: flash('Enter your name.','danger'); return render_template('register.html')
        if '@' not in email: flash('Enter a valid email address.','danger'); return render_template('register.html')
        if len(password)<6: flash('Password must contain at least 6 characters.','danger'); return render_template('register.html')
        try: user_id,message=register_user(name,email,password)
        except Exception as exc: app.logger.exception('Registration error'); flash('Registration failed: {}'.format(exc),'danger'); return render_template('register.html')
        if not user_id: flash(message,'warning'); return render_template('register.html')
        flash('Registration successful. Please login.','success'); return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=clean_text(request.form.get('email'),120).lower(); password=request.form.get('password','')
        if login_user(email,password): flash('Welcome back!','success'); return redirect(url_for('dashboard'))
        flash('Invalid email or password.','danger')
    return render_template('login.html')

@app.route('/logout')
def logout(): logout_user(); flash('You have been logged out.','success'); return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard(): return render_template('dashboard.html',recommendations=get_user_recommendations(session['user_id']))

@app.route('/planner/<category>',methods=['GET','POST'])
@login_required
def planner(category):
    if category not in ALLOWED_CATEGORIES: flash('Unknown planner.','danger'); return redirect(url_for('dashboard'))
    if request.method=='GET': return render_template('planner.html',category=category,category_name=ALLOWED_CATEGORIES[category])
    try:
        budget=parse_budget(request.form.get('budget'))
        data={'budget':budget,'currency':'INR','category':category}
        if category=='home':
            data.update({'room':clean_text(request.form.get('room'),100),'style':clean_text(request.form.get('style'),100),'color':clean_text(request.form.get('color'),100),'priority':clean_text(request.form.get('priority'),200),'city':clean_text(request.form.get('city'),100)})
        elif category=='party':
            guests=int(request.form.get('guests','1'))
            if guests<1 or guests>10000: raise ValueError('Guests must be between 1 and 10000.')
            data.update({'event_type':clean_text(request.form.get('event_type'),100),'guests':guests,'theme':clean_text(request.form.get('theme'),100),'date':clean_text(request.form.get('date'),50),'food_preference':clean_text(request.form.get('food_preference'),200),'city':clean_text(request.form.get('city'),100)})
        else:
            data.update({'occasion':clean_text(request.form.get('occasion'),100),'jewelry_type':clean_text(request.form.get('jewelry_type'),100),'metal':clean_text(request.form.get('metal'),100),'style':clean_text(request.form.get('style'),100),'outfit':clean_text(request.form.get('outfit'),200),'city':clean_text(request.form.get('city'),100)})
        image_path=None; image_filename=None; uploaded=request.files.get('image')
        if uploaded and uploaded.filename:
            ext=os.path.splitext(uploaded.filename)[1].lower()
            if ext not in {'.jpg','.jpeg','.png','.webp'}: raise ValueError('Only JPG, JPEG, PNG and WEBP images are allowed.')
            image_filename=secure_filename('{}{}'.format(uuid.uuid4().hex,ext)); image_path=os.path.join(UPLOAD_DIR,image_filename); uploaded.save(image_path)
        try: result=generate_recommendation(category,data,image_path=image_path)
        except Exception:
            app.logger.exception('Gemini generation failed'); flash('AI service could not be reached. A demo recommendation was generated instead.','warning')
            from backend.gemini_service import _demo_response
            result=_demo_response(category,data)
        result=enrich_result(result)
        recommendation_id=save_recommendation(session['user_id'],category,budget,data,result,image_filename)
        return redirect(url_for('result',recommendation_id=recommendation_id))
    except ValueError as exc:
        flash(str(exc),'danger'); return render_template('planner.html',category=category,category_name=ALLOWED_CATEGORIES[category])
    except Exception as exc:
        app.logger.exception('Planner error'); flash('Something went wrong: {}'.format(exc),'danger'); return redirect(url_for('dashboard'))

@app.route('/result/<int:recommendation_id>')
@login_required
def result(recommendation_id):
    row=get_recommendation(session['user_id'],recommendation_id)
    if not row: flash('Recommendation not found.','danger'); return redirect(url_for('dashboard'))
    return render_template('result.html',row=row,result=json.loads(row['result_json']),input_data=json.loads(row['input_json']))

@app.route('/history')
@login_required
def history(): return render_template('history.html',recommendations=get_user_recommendations(session['user_id']))

@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename): return send_from_directory(UPLOAD_DIR,filename)

@app.errorhandler(413)
def too_large(error): flash('Uploaded image is too large. Maximum size is {} MB.'.format(MAX_UPLOAD_MB),'danger'); return redirect(request.referrer or url_for('dashboard'))

if __name__=='__main__': app.run(host='127.0.0.1',port=5000,debug=True)

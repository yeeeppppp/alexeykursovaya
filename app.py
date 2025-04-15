from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
import os
import base64
from io import BytesIO
from PIL import Image
from models import db, Car, Admin
import random

app = Flask(__name__)
app.secret_key = 'carSalesAppSecretKey123'

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True,
}

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
    
    # Insert test admin if none exists
    if not Admin.query.filter_by(username='admin').first():
        test_admin = Admin(username='admin', password='admin123')
        db.session.add(test_admin)
        db.session.commit()

@app.route('/')
def index():
    """Display the role selection page"""
    return render_template('index.html')

@app.route('/user')
def user_view():
    """Display the user view with car listings"""
    cars = Car.query.all()
    return render_template('user.html', cars=[car.to_dict() for car in cars])

@app.route('/car/<int:car_id>')
def car_detail(car_id):
    """Display details for a specific car"""
    car = Car.query.get(car_id)
    if not car:
        flash('Автомобиль не найден', 'error')
        return redirect(url_for('user_view'))
    
    # Convert to dictionary for template use
    car_dict = car.to_dict()
    
    # Convert image data to base64 for display in HTML
    if car_dict['image']:
        encoded_image = base64.b64encode(car_dict['image']).decode('utf-8')
        car_dict['image_data'] = encoded_image
    
    return render_template('car_detail.html', car=car_dict)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Handle admin login"""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        admin = Admin.query.filter_by(username=username, password=password).first()
        if admin:
            session['admin_logged_in'] = True
            flash('Авторизация успешна!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Неверное имя пользователя или пароль'
    
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    """Handle admin logout"""
    session.pop('admin_logged_in', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Display the admin dashboard"""
    if not session.get('admin_logged_in'):
        flash('Пожалуйста, войдите, чтобы получить доступ к панели администратора', 'error')
        return redirect(url_for('admin_login'))
    
    cars = Car.query.all()
    return render_template('admin_dashboard.html', cars=[car.to_dict() for car in cars])

@app.route('/admin/add_car', methods=['GET', 'POST'])
def admin_add_car():
    """Handle adding a new car"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        specifications = request.form['specifications']
        
        # Process uploaded image
        image_data = None
        if 'image' in request.files and request.files['image'].filename:
            file = request.files['image']
            img = Image.open(file)
            img = img.resize((800, 600), Image.LANCZOS)
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='PNG')
            image_data = img_byte_arr.getvalue()
        
        # Add car to database
        new_car = Car(
            name=name,
            price=price,
            specifications=specifications,
            image=image_data
        )
        
        try:
            db.session.add(new_car)
            db.session.commit()
            flash('Автомобиль успешно добавлен!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении автомобиля: {str(e)}', 'error')
    
    return render_template('add_car.html')

@app.route('/admin/delete_car/<int:car_id>', methods=['POST'])
def admin_delete_car(car_id):
    """Handle deleting a car"""
    if not session.get('admin_logged_in'):
        return jsonify(success=False, error='Не авторизован')
    
    car = Car.query.get(car_id)
    if car:
        try:
            db.session.delete(car)
            db.session.commit()
            flash('Автомобиль успешно удален!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при удалении автомобиля: {str(e)}', 'error')
    else:
        flash('Автомобиль не найден', 'error')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/car_image/<int:car_id>')
def car_image(car_id):
    """Serve car image"""
    car = Car.query.get(car_id)
    if car and car.image:
        return send_file(
            BytesIO(car.image),
            mimetype='image/jpeg',
            as_attachment=False,
            download_name=f'car_{car_id}.jpg'
        )
    
    # Return placeholder image if no image is available
    return redirect(url_for('static', filename='img/placeholder.svg'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
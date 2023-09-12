from flask import Flask, render_template,request,url_for,redirect,jsonify,Response
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime 
import time
from flask_migrate import Migrate
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['UPLOAD_FOLDER']='asset'
db=SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # Add this line to allow connections from any origin
global card_id
card_id='23'
migrate = Migrate(app, db)
# Replace this section with your database model
class CardEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=True)
    photo_path = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=True)
    def __init__(self, card_id, full_name, email, phone, message, photo_path=None):
        self.card_id = card_id
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.message = message
        self.photo_path = photo_path 
    def __repr__(self):
        return f'<CardEntry {self.card_id}>'
def create_tables():
    with app.app_context():
        db.create_all()
create_tables()
@app.route('/register', methods=['GET', 'POST'])
def register():
    global card_id
    if request.method == 'POST':
        card_id=request.form.get('card_id')
        socketio.emit('update_card', card_id)

        # Process the rest of the form datacomm
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']

        # Handle photo upload
        photo = request.files['photo']
        photo_path = None
        if photo:
            # Save the photo to the specified directory
            filename = secure_filename(photo.filename)
            photo_path = os.path.join('asset', filename).replace('\\', '/')  # Store the relative path to the asset folder
            photo.save(os.path.join(app.static_folder, photo_path))
            print(photo_path)


        # Create a new entry in the database
        new_card_entry = CardEntry(
    card_id=card_id,
    full_name=full_name,
    email=email,
    phone=phone,
    message=message,
    photo_path=photo_path,  # Use the corrected photo path
)
        db.session.add(new_card_entry)
        db.session.commit()

        return redirect(url_for('data'))
    else:
        # Render the form with the card_id value in a hidden input field
        return render_template('register.html', card_id=card_id)

@app.route('/data')
def data():
    all_card_entries=CardEntry.query.order_by(desc(CardEntry.timestamp)).all()

    return render_template('data.html',card_entries=all_card_entries)
@app.route('/')
def home():
    return render_template('second.html')
@app.route('/edit/<int:entry_id>', methods=['GET', 'POST'])
def edit(entry_id):
    card_entry = CardEntry.query.get_or_404(entry_id)

    if request.method == 'POST':
        # Update the card entry with the form data
        card_entry.full_name = request.form['full_name']
        card_entry.email = request.form['email']
        card_entry.phone = request.form['phone']
        card_entry.message = request.form['message']

        # Handle photo upload
        photo = request.files['photo']
        if photo:
            # Save the photo to the specified directory
            filename = secure_filename(photo.filename)
            photo_path = os.path.join('asset', filename).replace('\\', '/')  # Store the relative path to the asset folder
            photo.save(os.path.join(app.static_folder, photo_path))
            print(photo_path)
            card_entry.photo_path = photo_path

        db.session.commit()
        return redirect(url_for('data'))

    return render_template('edit.html', card_entry=card_entry)


# Route to display the card entries on the read.html page

@app.route('/read', methods=['GET', 'POST'])
def read():
    global card_id 
    if card_id != '':
        card_entry = CardEntry.query.filter_by(card_id=card_id).first()
        if card_entry:
            entry_data = {
                'card_id': card_entry.card_id,
                'full_name': card_entry.full_name,
                'email': card_entry.email,
                'phone': card_entry.phone,
                'message': card_entry.message,
                 'photo_path': url_for('static', filename=card_entry.photo_path)
            }
            print(entry_data['photo_path'])
            # socketio.emit('update_read', entry_data)  # Emit entry_data instead of card_id
            return render_template('read.html', entry_data=entry_data)  # Pass entry_data
        else:
            return render_template('read.html', entry_data=None)  # No card entry found
    # else:
    #     return render_template('read.html', entry_data=None)  # No card ID available
def fetch_card_id():
    global card_id
    return card_id

@app.route('/sse')
def sse():
    def event_stream():
        while True:
            card_id = fetch_card_id()
            if card_id:
                yield f"data: {json.dumps({'card_id': card_id})}\n\n"
            time.sleep(4)
    
    return Response(event_stream(), mimetype="text/event-stream")



@app.route('/delete/<int:entry_id>', methods=['POST'])
def delete(entry_id):
    card_entry = CardEntry.query.get_or_404(entry_id)

    # Delete the card entry from the database
    db.session.delete(card_entry)
    db.session.commit()

    return redirect(url_for('data'))

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)








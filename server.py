from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hubsecret!1'
socketio = SocketIO(app)

messages = []
online_users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    username = online_users.get(request.sid, 'Anonymous')
    online_users[request.sid] = username
    emit('update_users', {'users': list(online_users.values())}, broadcast=True)
    print(f'{username} connected')

@socketio.on('disconnect')
def handle_disconnect():
    username = online_users.pop(request.sid, 'Anonymous')
    emit('user_left', {'username': username}, broadcast=True)
    print(f'{username} disconnected')

@socketio.on('message')
def handle_message(data):
    print(f"Received message from {data['username']}: {data['message']}")
    message_id = len(messages)
    messages.append({'id': message_id, 'username': data['username'], 'message': data['message']})
    emit('message', {**data, 'id': message_id}, broadcast=True)

@socketio.on('delete_message')
def handle_delete_message(data):
    message_id = data['id']
    username = data['username']
    if 0 <= message_id < len(messages) and messages[message_id]['username'] == username:
        del messages[message_id]
        emit('delete_message', {'id': message_id}, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    emit('typing', data, broadcast=True)

@socketio.on('set_username')
def handle_set_username(data):
    username = data['username'] if data['username'].strip() else 'Anonymous'
    online_users[request.sid] = username
    emit('update_users', {'users': list(online_users.values())}, broadcast=True)

@socketio.on_error()
def error_handler(e):
    emit('error', {'error': str(e)})

if __name__ == '__main__':
    print('Server is running on http://localhost:5000')
    socketio.run(app, host='0.0.0.0', port=5000)



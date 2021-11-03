from flask import Flask, send_from_directory, request, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from .Game.GameData import GameData
from .Game.GameController import GameController

app = Flask(__name__, static_folder='../../client/build', static_url_path='/')

socket = SocketIO(app)

if __name__ == "__main__":
    socket.run(app, debug=True)#, port=5000)

game_controllers = {}

@socket.on('connect')
def on_connect():
    print('user connected')

@socket.on('disconnect')
def on_disconnect():
    for room, game_controller in game_controllers.items():
        if request.sid in game_controller.clients:
            game_controllers[room].PlayerLeaves(request.sid)
            distributeGameData(game_controllers[room].game.toJSON(), room)
    


@socket.on('join_room')
def on_join(data):
    room = data['room']
    print(f"{data['username']} joined room: {room}")
    join_room(room)
    if room in game_controllers.keys():
        game_controllers[room].NewPlayerJoined(data['username'],request.sid)
        controller = game_controllers[room]
        emit('game_data', {'msg': controller.game.toJSON()}, room=room)
    else:
        game_controllers[room] = GameController()
        game_controllers[room].NewPlayerJoined(data['username'],request.sid)
        controller = game_controllers[room]
        emit('game_data', {'msg': controller.game.toJSON()}, room=room)


###### UpPoker Code #######

game_controllers = {}

@socket.on('joined')
def joined(data):
    print("player joined")
    room = data['room']
    join_room(room)
    if room in game_controllers.keys():
        game_controllers[room].NewPlayerJoined(data['username'],request.sid)
        controller = game_controllers[room]
        emit('game_data', {'msg': controller.game.toJSON()}, room=room)
    else:
        game_controllers[room] = GameController()
        game_controllers[room].NewPlayerJoined(data['username'],request.sid)
        controller = game_controllers[room]
        emit('game_data', {'msg': controller.game.toJSON()}, room=room)


@socket.on('take_action')
def action(data):
    print(data)

    room = data['room']
    controller = game_controllers[room]
    action = data['action'].lower()
    modifier = data['modifier']
    print(f"{action} - {modifier}")

    if action == "deal":
        game_controllers[room].NewDeal("twoup")
        dealCards(room)
    elif action in ["check", "call", "bet", "fold"]:
        print("player acts")
        game_controllers[room].MakeMove(request.sid, action, modifier)
    elif action == "show":
        print("player shows")
        game_controllers[room].PlayerShows(request.sid, modifier)

    distributeGameData(controller.game.toJSON(), room)

def distributeGameData(data, room):
    emit('game_data', {'msg': data}, room=room)

def dealCards(room):
    controller = game_controllers[room]
    for client, seat_number in controller.clients.items():
        if controller.game.players[seat_number] is not None:
            emit('deal_cards', {'msg' : controller.game.players[seat_number].cards}, room=client)


@socket.on('left')
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': session.get('name') + ' has left the room.'}, room=room)

@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')
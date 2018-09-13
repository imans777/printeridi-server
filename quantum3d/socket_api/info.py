
from shortid import ShortId
from flask_socketio import Namespace, send, emit
sid = ShortId()


class SocketBase(Namespace):
    id = sid.generate()

    def on_connect(self):
        print('connected!', self.id)
        emit('message', {'connect:': 'hey'})

    def on_disconnect(self):
        print('disconnected!', self.id)

    def on_message(self, data):
        print('on message!')
        send({'inner': 'good!'})

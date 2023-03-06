#__all__ = ["SocketMessagingWindow"]
import omni.ui as ui
import logging, os
from .style import *
from .messenger import *
from signalrcore.hub_connection_builder import HubConnectionBuilder

class SocketMessagingWindow(ui.Window):
    """SocketMessagingWindow"""

    title = "SocketMessagingWindow"
    _label_connection_status=None
    _label_connection_status_message=""
    dataDict = {
        'robot1': None,
        'robot2': None,
        'robot3': None,
        'robot4': None,
    }
    label_robot4 = None
    _hub_connection = None

    def __init__(self, **kwargs):
        super().__init__(SocketMessagingWindow.title, **kwargs)

        with self.frame:
            with ui.VStack(height=0,style=style):
                self._ui_connection_status_frame =  ui.Frame(name="connection_status_frame")
                self.redraw_ui()
                self.dataDict['robot1'] = ui.Label('')
                self.dataDict['robot2'] = ui.Label('')
                self.dataDict['robot3'] = ui.Label('')
                self.dataDict['robot4'] = ui.Label('')
                ui.Spacer()


    def _connection_status(self):
        with self._ui_connection_status_frame:
            with ui.VStack(style=style):
                self._ui_connection_btn = ui.Button(
                    "Disconnect" if self._hub_connection != None  else "Connect",
                    name="disconnect" if self._hub_connection != None  else "connect",
                    clicked_fn=self._toggle_connection,
                    style=style
                    )
                self._label_connection_status=ui.Label(
                    self._label_connection_status_message,
                    name="connection_error_label",
                    word_wrap=True)

    def redraw_ui(self):
        self._connection_status()


    def do_disconnect(self):
        if self._hub_connection:
            self._hub_connection.stop()
        self._hub_connection = None

    def do_connect(self):
        self.start_listening()

    def _toggle_connection(self):
        self._label_connection_status_message=""
        if self._hub_connection != None:
            self.do_disconnect()
        else:
            self.do_connect()

        self.redraw_ui()


    def handle_message(self, msg):
        #print(str(msg))
        #print(str(msg[0]['id']))
        robot_id = str(msg[0]['id'])

        self.dataDict[robot_id].text = f"ID: {robot_id}\n" \
            + f"TS: {str(msg[0]['timestamp'])}\n" \
            + f"A1: {str(msg[0]['ang1j'])}\n" \
            + f"A2: {str(msg[0]['ang2j'])}\n" \
            + f"A3: {str(msg[0]['ang3j'])}\n" \
            + f"A4: {str(msg[0]['ang4j'])}\n" \
            + f"A5: {str(msg[0]['ang5j'])}\n" \
            + f"A6: {str(msg[0]['ang6j'])}\n"

        # if self.is_twin_changed(cur_twin, twin):
        Messenger().push(event_type=Messenger.EVENT_SIGNALR_MSG, payload=msg[0])

    # def is_msg_updates_values(self, val1: dict, val2: dict):
    #     import copy
    #     """
    #     val1 = current robot values
    #     val2 = new robot values
    #     """
    #     val1 = copy.deepcopy(val1)
    #     val2 = copy.deepcopy(val2)

    #     changed = set(val2) - set(val1)

    #     return len(changed) > 0

    def start_listening(self):
        # if bool(os.environ["OV_DEBUG"]):
        #     handler = logging.StreamHandler()
        #     handler.setLevel(logging.DEBUG)
            # .configure_logging(logging.DEBUG, socket_trace=True, handler=handler) \
        try:
            hub_connection = HubConnectionBuilder() \
                .with_url(os.environ['OV_SIGNALR_ENDPOINT'], options={"verify_ssl": False}) \
                .with_automatic_reconnect({
                        "type": "interval",
                        "keep_alive_interval": 10,
                        "intervals": [1, 3, 5, 6, 7, 87, 3]
                    }).build()

            hub_connection.on_open(lambda: logging.info("connection opened and handshake received ready to send messages"))
            hub_connection.on_close(lambda: logging.info("connection closed"))

            hub_connection.on("ReceiveMessage", self.handle_message)
            hub_connection.start()

            self._hub_connection = hub_connection
        except Exception as e:
            self._label_connection_status_message=str(e)
            logging.error(str(e))
            self.do_disconnect()
        except:
            self._label_connection_status_message="Cannot connect to socket"
            logging.error("Cannot connect to socket")
            self.do_disconnect()

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
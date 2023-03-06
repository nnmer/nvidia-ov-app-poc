__all__ = ["MsftKhiAnimationWindow"]
import omni.ui as ui


class MsftKhiAnimationWindow(ui.Window):
    """MsftKhiAnimationWindow"""

    title = "MSFT KHI Animation"
    msg = None
    label_msg_adt = None
    label_msg_signalr = None

    def __init__(self, **kwargs):
        super().__init__(MsftKhiAnimationWindow.title, **kwargs)

        # here you build the content of the window
        with self.frame:
            with ui.VStack(height=0):

                ui.Spacer()
                self.msg = ui.Label('Controlls TBD')
                ui.Spacer(height=20)
                self.label_msg_adt = ui.Label('')
                ui.Spacer(height=20)
                self.label_msg_signalr = ui.Label('',word_wrap=True)


    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

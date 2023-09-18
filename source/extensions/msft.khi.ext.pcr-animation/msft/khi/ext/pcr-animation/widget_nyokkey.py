import omni.ui as ui
import os
import carb
from msft.ext.adt import ADT, AdtPullingRegistry

NyokkeyActionType = {
  "DEFAULT": '1',
  "BRING_OVER_TIPS": '2',
  "BRING_OVER_SPECIMEN": '3',
  "WASTE": 'waster'
}

NyokkeyActionDefinition = {
  NyokkeyActionType["DEFAULT"]: {
    "avatar": './assets/nyokkey1.png',
    "currentTask": 'Patrolling',
    "nextTask": None,
    "badge": 'bg-green'
  },
  NyokkeyActionType["BRING_OVER_TIPS"]: {
    "avatar": './assets/nyokkey2.png',
    "currentTask": 'Bringing over tips',
    "nextTask": 'Patrolling',
    "badge": 'bg-yellow'
  },
  NyokkeyActionType["BRING_OVER_SPECIMEN"]: {
    "avatar": './assets/nyokkey3.png',
    "currentTask": 'Bringing over a new specimen container',
    "nextTask": 'Patrolling',
    "badge": 'bg-yellow'
  },
  NyokkeyActionType["WASTE"]: {
    "avatar": './assets/nyokkey4.png',
    "currentTask": 'Bring over a waste box to the disposal area',
    "nextTask": 'Pick up specimen',
    "badge": 'bg-yellow'
  }
}

class NyokkeyWidget:

    def __init__(self) -> None:
        self._ui_frame = None
        self.label_nyokkey_status = None
        AdtPullingRegistry().register_action('register_nyokkey_status_adt_pull_action', self._register_nyokkey_status_adt_pull_action, 5)
        AdtPullingRegistry().start_action('register_nyokkey_status_adt_pull_action')

    def _register_nyokkey_status_adt_pull_action(self):
        query_expression = f"SELECT * FROM digitaltwins dt WHERE dt.$dtId = 'Nyokkey'"
        query_result = ADT().service_client().query_twins(query_expression)
        for i in query_result:
            if bool(os.environ['OV_DEBUG']):
                carb.log_info(f"[NyokkeyWidget] pulled data => {i}")
            val = str(i['RobotStatus'])
            # self.label_nyokkey_status = val +'-'+str(id(i))[-7:] if bool(os.environ["OV_DEV"]) == True else val
            self.label_nyokkey_status = val
        self.re_draw()

    def render(self):
        with ui.ZStack():
            ui.Rectangle(width=200, height=100, style={"background_color": ui.color("#0000BB")})
            with ui.VStack(height=0):
                ui.Spacer(height=4)
                ui.Label("Nyokkey", style={"font_size": 24})
                self._ui_frame = ui.Frame(name="ui_frame")

    def re_draw(self):
        with self._ui_frame:
            with ui.VStack(height=0):
                if self.label_nyokkey_status:
                    supported = NyokkeyActionDefinition.get(str(self.label_nyokkey_status))
                    if supported != None:
                        ui.Spacer(height=4)
                        ui.Label("Nyokkey is: ")
                        ui.Label(supported.get('currentTask') or '', style={"font_size": 16})
                        ui.Spacer(height=4)
                        ui.Label("Next task: ")
                        ui.Label(supported.get('nextTask') or '', style={"font_size": 16})
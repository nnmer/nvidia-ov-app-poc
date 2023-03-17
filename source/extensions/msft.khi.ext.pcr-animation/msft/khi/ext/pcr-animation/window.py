__all__ = ["MsftKhiAnimationWindow"]
import omni.ui as ui
from omni.kit.viewport.utility import get_active_viewport_window

import msft.ext.viewport_widgets_manager as ViewportWidgetsManager
from msft.ext.viewport_widgets_manager import WidgetAlignment, AlertWidgetProvider
from msft.ext.adt.messenger import Messenger
from msft.ext.adt.viewport_widget_twin_info import ViewportWidgetTwinInfo

from .alert_viewport_widget import *

class MsftKhiAnimationWindow(ui.Window):
    """MsftKhiAnimationWindow"""

    title = "MSFT KHI Animation"
    msg = None
    label_msg_adt = None
    label_msg_signalr = None
    # _widget_info_viewport1 = None
    # _widget_info_viewport2 = None
    _viewport_widget_window_list = []

    def __init__(self, **kwargs):
        super().__init__(MsftKhiAnimationWindow.title, **kwargs)
        self.adtListItemSelected = Messenger().subscribe_deffered(Messenger().EVENT_ADT_LIST_ITEM_SELECTED, self.process_adt_list_item_selected)

        # here you build the content of the window
        with self.frame:
            with ui.VStack(height=0):

                ui.Spacer()
                self.msg = ui.Label('Controlls TBD')
                self.btn = ui.Button('Show WidgetWindow Error',clicked_fn=self.create_alert_widget3)
                self.btn = ui.Button('Clean all WidgetWindow',clicked_fn=self.clean_WidgetWindow)
                # self.btn = ui.Button('Show Manipulator widget',clicked_fn=self.create_alert_widget1)
                ui.Spacer(height=20)
                self.label_msg_adt = ui.Label('')
                ui.Spacer(height=20)
                self.label_msg_signalr = ui.Label('',word_wrap=True)

    def process_adt_list_item_selected(self, event):
        for key in event.payload.get_keys():
            mesh_id = event.payload[key]['mesh_id']
            twin_data = event.payload[key]['twin_data']
            infoWidget = ViewportWidgetTwinInfo(twin_data)
            widget_id = ViewportWidgetsManager.add_widget(mesh_id, infoWidget, WidgetAlignment.CENTER)
            self._viewport_widget_window_list.append(widget_id)

    def clean_WidgetWindow(self):
        for item in self._viewport_widget_window_list:
            ViewportWidgetsManager.remove_widget(item)

    def create_alert_widget3(self):
        alertWidget = AlertWidgetProvider({'RS07N_for_ODP': {'twin_data': {'$dtId': 'RS07N_for_ODP', 'ang3j': 0, '$etag': 'W/"636763cc-e8a2-4144-8a35-b60161ac6e21"', 'Tags': 'Robot1', 'ID': 'RS07N_for_ODP', 'RobotStatus': 'TBD', 'ang1j': 0, 'ang2j': 0, 'ang4j': 0, 'ang5j': 0, 'ang6j': 0, 'Temperature': 0, 'LastErrorMessage': '', 'UnitScenarioRobotStop': False, '$metadata': {'Tags': {'lastUpdateTime': '2023-03-08T05:01:26.0229805Z'}, 'ID': {'lastUpdateTime': '2023-03-08T05:01:26.0229805Z'}, '$model': 'dtmi:KHI:PCR:RobotArm;1', 'ang2j': {'lastUpdateTime': '2023-03-08T05:01:26.0229805Z'}, '$lastUpdateTime': '2023-03-08T05:01:26.0229805Z', 'RobotStatus': {'lastUpdateTime': '2023-03-08T05:01:26.0229805Z'}, 'ang1j': {'lastUpdateTime': '2023-03-08T05:01:26.0229805Z'}, 'ang3j': {'lastUpdateTime': '2023-03-08T05:01:26.0229805Z'}, 'ang4j': {'lastUpdateTime': '2023-03-08T05:01:26.0229805Z'}, 'ang5j': {'lastUpdateTime': '2023-03-08T05:01:26.0229805Z'}, 'ang6j': {'lastUpdateTime': '2023-03-08T05:01:26.0229805Z'}, 'Temperature': {'lastUpdateTime': '2023-03-08T05:01:26.0229805Z'}, 'LastErrorMessage': {'lastUpdateTime': '2023-03-08T05:01:26.0229805Z'}, 'UnitScenarioRobotStop': {'lastUpdateTime': '2023-03-08T05:01:26.0229805Z'}}}, 'mesh_id': '/World/khi_rs007n_vac_UNIT1'}})
        widget_id = ViewportWidgetsManager.add_widget('/World/khi_rs007n_vac_UNIT1', alertWidget, WidgetAlignment.TOP)
        self._viewport_widget_window_list.append(widget_id)

        # infoWidget = RobotInfoWidgetProvider()
        # ViewportWidgetManager.add_widget('/World/khi_rs007n_vac_UNIT1', infoWidget, WidgetAlignment.CENTER)


        # alertWidget = RobotAlertWidgetProvider()
        # ViewportWidgetManager.add_widget('/World/khi_rs007n_vac_UNIT3', alertWidget, WidgetAlignment.TOP)

        # infoWidget = RobotInfoWidgetProvider()
        # ViewportWidgetManager.add_widget('/World/khi_rs007n_vac_UNIT3', infoWidget, WidgetAlignment.CENTER)


        # alertWidget = RobotAlertWidgetProvider()
        # ViewportWidgetManager.add_widget('/World/khi_rs007n_vac_UNIT4', alertWidget, WidgetAlignment.TOP)

        # infoWidget = RobotInfoWidgetProvider()
        # ViewportWidgetManager.add_widget('/World/khi_rs007n_vac_UNIT4', infoWidget, WidgetAlignment.CENTER)

    # def create_alert_widget1(self):
    #     # Get the active (which at startup is the default Viewport)
    #     viewport_window = get_active_viewport_window()

    #     # Issue an error if there is no Viewport
    #     if not viewport_window:
    #         carb.log_warn(f"No Viewport Window to add {'abc'} scene to")
    #         self._widget_info_viewport1 = None
    #         return

    #     # Build out the scene
    #     self._widget_info_viewport1 = AlertViewportWidget(viewport_window, 'abc', {
    #         '/World/khi_rs007n_vac_UNIT4',
    #         '/World/khi_rs007n_vac_UNIT3',
    #         '/World/khi_rs007n_vac_UNIT2',
    #         '/World/khi_rs007n_vac_UNIT1'
    #     })

    #     ctx = omni.usd.get_context()
    #     ctx.get_selection().set_selected_prim_paths(['/World/khi_rs007n_vac_UNIT3'], True)


    # def create_alert_widget1(self):
    #     ref_handler = self._widget_info_viewport1
    #     self.create_alert_widget(ref_handler, 'abc', ['/World/khi_rs007n_vac_UNIT3'])
    # def create_alert_widget2(self):
    #     ref_handler = self._widget_info_viewport2
    #     self.create_alert_widget(ref_handler, 'xyz', ['/World/khi_rs007n_vac_UNIT4'])

    # def create_alert_widget(self, ref_handler, ext_id, prim_path):
    #     # Get the active (which at startup is the default Viewport)
    #     viewport_window = get_active_viewport_window()

    #     # Issue an error if there is no Viewport
    #     if not viewport_window:
    #         carb.log_warn(f"No Viewport Window to add {ext_id} scene to")
    #         ref_handler = None
    #         return

    #     # Build out the scene
    #     ref_handler = AlertViewportWidget(viewport_window, ext_id, {
    #         '/World/khi_rs007n_vac_UNIT4',
    #         '/World/khi_rs007n_vac_UNIT3',
    #         '/World/khi_rs007n_vac_UNIT2',
    #         '/World/khi_rs007n_vac_UNIT1'
    #     })

    #     ctx = omni.usd.get_context()
    #     ctx.get_selection().set_selected_prim_paths(prim_path, True)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

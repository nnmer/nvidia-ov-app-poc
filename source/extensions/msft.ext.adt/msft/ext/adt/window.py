__all__ = ["MsftAdtWindow"]
import os
import copy
import carb
import omni.ext
import omni.usd
import omni.ui as ui
import asyncio
import threading
import time
from typing import List
from .style import *
from .adt_list import *
from .messenger import *
from .robotmotion import RobotMotion

from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
# from pxr import Sdf, Usd
# from .robotdata import getPose, RobotPose


class MsftAdtWindow(ui.Window):
    motions: List[RobotMotion] = [None, None, None, None]
    count = 0
    """MsftAdtWindow"""

    title = "MSFT ADT"

    _pulling_delay = int(os.environ['OV_ADT_PULLING_FREQUENCY']) # in seconds
    _pulling_handler = None

    # when twins are loaded dictionary key - $dtId, value - whole twin object data
    # Robot RS007 twin data:
    # {
    #     "$dtId": "RS07N_for_RPP",
    #     "$etag": "5c30dd8e-cebc-44f4-a2c4-d8393d47a4eb",
    #     "CommunicationStatus": True,
    #     "OperatingStatus": "No data",
    #     "NumberOfErrorInRangeTime": 0,
    #     "TimeRangeInMinute": 10,
    #     "MonthlyOccupancyRate": 0,
    #     "MTTR": 0,
    #     "M3": "LastError0Message": "",
    #     "LastError1Message": "",
    #     "LastError2Message": "",
    #     "LastError3Message": "",
    #     "LastError4Message": "",
    #     "RobotStatus": "TBD",
    #     "RobotOperationStatus": "TBD",
    #     "ang1j": 0,
    #     "ang2j": 0,
    #     "ang3j": 0,
    #     "ang4j": 0,
    #     "ang5j": 0,
    #     "ang6j": 0,
    #     "$metadata": {
    #         "$model": "dtmi:PCR:PCR_Container_System:RoboticArm;1",
    #         "$lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z",
    #         "CommunicationStatus": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "OperatingStatus": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "NumberOfErrorInRangeTime": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "TimeRangeInMinute": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "MonthlyOccupancyRate": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "MTTR": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "MTBF": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "LastError0Message": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "LastError1Message": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "LastError2Message": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "LastError3Message": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "LastError4Message": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "RobotStatus": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "RobotOperationStatus": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "ang1j": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "ang2j": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "ang3j": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "ang4j": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "ang5j": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         },
    #         "ang6j": {
    #             "lastUpdateTime": "2023-02-15T16: 20: 40.0247138Z"
    #         }
    #     }
    # }
    _twins_dict = None
    _adt_service_client = None
    _adt_tree_view_handler = None
    _adt_tree_view_data = None

    _ui_connection_status_frame = None
    _ui_twins_list_frame = None
    _ui_connection_btn = None

    _map_dt_id2mesh_id = {
        "RS07N_for_NAEP" : '/World/khi_rs007n_vac_UNIT4',
        "RS07N_for_RPP" : '/World/khi_rs007n_vac_UNIT3',
        "RS07N_for_PIP" : '/World/khi_rs007n_vac_UNIT2',
        "RS07N_for_ODP" : '/World/khi_rs007n_vac_UNIT1',
        # 'Slider_for_PIP' : '',
        # 'Agitator_for_NAEP' : '',
        # 'Lid_Control_Device_for_PIP' : '',
        # 'PCR_Instruments_for_PIP' : '',
        # 'PCR_Container_System' : '',
        # 'Freezer_for_RPP' : '',
        # 'Dispensing_Machine_for_NAEP' : '',
        # 'ID_Reader_for_ODP' : '',
        # 'Opening_Dispensing_Process' : '',
        # 'PCR_Inspection_Process' : '',
        # 'PLC_for_ODP' : '',
        # 'Warmer_for_NAEP' : '',
        # 'PLC_for_RPP' : '',
        # 'Tube_Feeder_for_RPP' : '',
        # 'PCR_Inspection_PC' : '',
        # 'Condenser_for_ODP' : '',
        # 'PLC_for_PIP' : '',
        # 'Reagent_Preparation_Process' : '',
        # 'Dispensing_Machine_for_ODP' : '',
        # 'Information_Integration_PC' : '',
        # 'PLC_for_NAEP' : '',
        # 'Nucleic_Acid_Extraction_Process' : '',
        # 'Overall_Control_PLC' : '',
    }

    def __init__(self, **kwargs):
        super().__init__(MsftAdtWindow.title, **kwargs)

        with self.frame:
            with ui.VStack(height=0,style=style):
                if os.environ["OV_DEFAULT_STAGE_LOAD"] and os.environ["OV_STAGE_AUTOLOAD"] == 'false':
                    ui.Button('Load stage', clicked_fn=self._load_and_setup_stage, style=style)
                ui.Button('Move', clicked_fn=self._move_click, style=style)
                self._ui_connection_status_frame = ui.Frame(name="connection_status_frame",style=style)
                self._ui_twins_list_frame = ui.ScrollingFrame(
                    name="twins_list_frame",
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    style_type_name_override="TreeView",
                    height=100,
                    style=style
                )

                self.redraw_ui()

                if os.environ["OV_STAGE_AUTOLOAD"] == 'true':
                    self._load_and_setup_stage()

                # omni.kit.commands.execute('CreateMeshPrimWithDefaultXform',prim_type='Cube')
                # omni.kit.commands.subscribe_on_change(self._event_triggered)

    def _load_and_setup_stage(self):

        # update_stream = omni.kit.app.get_app().get_update_event_stream()

        # def on_update(e: carb.events.IEvent):
        #     print(f"Update: {e.payload['dt']}")
        usd_ctx = omni.usd.get_context()

        def setup_layers(a, b):
            new_layer_id = 'origin'     # uuid.uuid4()
            stage = usd_ctx.get_stage()
            omni.kit.commands.execute("CreateSublayer",
                layer_identifier=stage.GetRootLayer().identifier,
                # This example prepends to the subLayers list
                sublayer_position=1,
                new_layer_path=rf"{os.environ['TEMP']}{os.sep}{new_layer_id}.usd",
                layer_name="Origin",
                transfer_root_content=True,
                # When True, it will create the layer file for you too.
                create_or_insert=True
            )

            new_layer_id = 'msft.khi.pcr.adt.animation-overlay'  #uuid.uuid4()
            omni.kit.commands.execute("CreateSublayer",
                layer_identifier=stage.GetRootLayer().identifier,
                # This example prepends to the subLayers list
                sublayer_position=0,
                new_layer_path=rf"{os.environ['TEMP']}{os.sep}{new_layer_id}.usd",
                layer_name="Animation",
                transfer_root_content=False,
                # When True, it will create the layer file for you too.
                create_or_insert=True
            )

            omni.kit.commands.execute('SetEditTarget',
                layer_identifier=f"{os.environ['TEMP']}{os.sep}{new_layer_id}.usd",
            )

        stage2load = os.environ["OV_DEFAULT_STAGE_LOAD"]
        if stage2load and len(stage2load) > 0 and (os.path.exists(stage2load) or stage2load.startswith('omniverse:')):
            usd_ctx.open_stage_with_callback(
                stage2load,
                on_finish_fn=setup_layers
            )

        # sub = update_stream.create_subscription_to_pop(on_update, name="My Subscription Name")

    def _move_click(self):
        # if self.motion is None:
        # self.motion = RobotMotion('/World/khi_rs007n_vac_UNIT1/world_003/base_link_003',
        #                           ['link1piv_003', 'link2piv_003', 'link3piv_003', 'link4piv_003',
        #                            'link5piv_003', 'link6piv_003'])

        if self.motions[0] is not None and self.motions[0].animating:
            self.motions[0].stopAnimating()
            self.motions[1].stopAnimating()
            self.motions[2].stopAnimating()
            self.motions[3].stopAnimating()
            return

        self.motions[0] = RobotMotion('/World/khi_rs007n_vac_UNIT3/world/base_link',
                                      ['link1piv', 'link2piv', 'link3piv', 'link4piv',
                                       'link5piv', 'link6piv'])
        self.motions[1] = RobotMotion('/World/khi_rs007n_vac_UNIT2/world_001/base_link_001',
                                      ['link1piv_001', 'link2piv_001', 'link3piv_001', 'link4piv_001',
                                       'link5piv_001', 'link6piv_001'])
        self.motions[2] = RobotMotion('/World/khi_rs007n_vac_UNIT4/world_002/base_link_002',
                                      ['link1piv_002', 'link2piv_002', 'link3piv_002', 'link4piv_002',
                                       'link5piv_002', 'link6piv_002'])
        self.motions[3] = RobotMotion('/World/khi_rs007n_vac_UNIT1/world_003/base_link_003',
                                      ['link1piv_003', 'link2piv_003', 'link3piv_003', 'link4piv_003',
                                       'link5piv_003', 'link6piv_003'])

        asyncio.ensure_future(self.motions[0].startAnimating())
        asyncio.ensure_future(self.motions[1].startAnimating())
        asyncio.ensure_future(self.motions[2].startAnimating())
        asyncio.ensure_future(self.motions[3].startAnimating())

        # allPoses = [
        #     RobotPose.zero, RobotPose.deg10, RobotPose.rest, RobotPose.fcartup, RobotPose.fcartdn, RobotPose.ecartup,
        #     RobotPose.ecartdn, RobotPose.key00up, RobotPose.key00dn, RobotPose.key01up, RobotPose.key01dn,
        #     RobotPose.key02up, RobotPose.key02dn, RobotPose.key03up, RobotPose.key03dn,
        #     RobotPose.zero, RobotPose.Pose099900, RobotPose.Pose090000, RobotPose.Pose099999,
        #     RobotPose.Pose099000, RobotPose.Pose099990, RobotPose.Pose999999]

        # print("Move " + str(self.count))
        # self.motion.setPose(getPose(allPoses[self.count]))
        # self.count = self.count + 1
        # if self.count >= len(allPoses):
        #     self.count = 0
        # self.motion.setPose([0, 0, 0, 0, 0, 0])
        # self.motion.setPose(getPose(RobotPose.rest))

    def _connection_status(self):
        with self._ui_connection_status_frame:
            with ui.VStack():
                self._ui_connection_btn = ui.Button(
                    "Disconnect" if self._adt_service_client != None  else "Connect",
                    name="disconnect" if self._adt_service_client != None  else "connect",
                    clicked_fn=self._pulling_toggle,
                    style=style
                    )
                #ui.Label(self._adt_service_client if self._adt_service_client else "")

    def redraw_ui(self):
        self._connection_status()
        with self._ui_twins_list_frame:
            pass

    def do_disconnect(self):
        self._pulling_handler = None
        self._adt_service_client = None

    def do_connect(self):
        self._service_client()
        self._pulling_handler = threading.Thread(target=asyncio.run, args=(self._while_connected_regularly_get_twins(),))
        self._pulling_handler.start()

    def _pulling_toggle(self):
        if self._adt_service_client != None:
            self.do_disconnect()
        else:
            self.do_connect()

        self.redraw_ui()

    def _service_client(self):
        if self._adt_service_client == None:
            self._adt_service_client = DigitalTwinsClient(credential=ClientSecretCredential(
                client_secret=os.environ["OV_AZURE_CLIENT_SECRET"],
                client_id=os.environ["OV_AZURE_CLIENT_ID"],
                tenant_id=os.environ["OV_AZURE_TENANT_ID"],
            ), endpoint=os.environ["OV_AZURE_DIGITALTWINS_ENDPOINT"], logging_enable=True)
        return self._adt_service_client

    # def _event_triggered(self):
    #     history = omni.kit.undo.get_history()
    #     for command in history.values():
    #         print(command.name)
    #         if command.name =="SelectPrimsCommand":
    #             for args in command.kwargs.items():
    #                 if args[0] == "new_selected_paths":
    #                     selected_item=" ".join(args[1])
    #                     print(selected_item)
    #                     if selected_item != "" and selected_item != "/World":
    #                         self._get_twin()
    #                     else:
    #                         pass
    #                         # self.label1.text="no object selected"
    #     omni.kit.undo.clear_history()

    def on_twin_selected_in_list(self, selected_keys):
        # stage = omni.usd.get_context().get_stage()
        # prim = stage.GetPrimAtPath(self._map_dt_id2mesh_id[key])
        ctx = omni.usd.get_context()
        paths = []
        payload_adt_list_selected = {}
        for key in selected_keys:
            k = repr(key)
            paths.append(self._map_dt_id2mesh_id[k])
            payload_adt_list_selected[k] = {
                "mesh_id": self._map_dt_id2mesh_id[k],
                "twin_data": self._twins_dict[k]
            }

        # print(f"selected twin push message {type(payload_adt_list_selected)}: {str(payload_adt_list_selected)}")

        if len(paths) > 0:
            ctx.get_selection().set_selected_prim_paths(paths, True)

        Messenger().push(event_type=Messenger().EVENT_ADT_LIST_ITEM_SELECTED, payload=payload_adt_list_selected)

    # def is_twin_changed(self, val1: dict, val2: dict):
    #     import copy
    #     """
    #     val1 = current twin values
    #     val2 = new twin values
    #     """
    #     val1 = copy.deepcopy(val1)
    #     val2 = copy.deepcopy(val2)
    #     if '$metadata' in val1:
    #         val1.pop('$metadata')
    #     if '$metadata' in val2:
    #         val2.pop('$metadata')
    #     changed = set(val2) - set(val1)

    #     return len(changed) > 0


    async def _while_connected_regularly_get_twins(self):

        while self._adt_service_client:
            try:
                #model = self._service_client().get_digital_twin(model_id)
                #query_expression = 'SELECT * FROM digitaltwins dt WHERE STARTSWITH(dt.$metadata.$model,\'dtmi:PCR:PCR_Container_System\')'
                query_expression = 'SELECT * FROM digitaltwins dt WHERE STARTSWITH(dt.$dtId,\'RS07N_\')'
                query_result = self._service_client().query_twins(query_expression)

                if self._twins_dict == None:
                    self._twins_dict = {}

                for twin in query_result:
                    # cur_twin = self._twins_dict.get(twin['$dtId'], {})
                    self._twins_dict[twin['$dtId']] = twin

                    # print(self.is_twin_changed(cur_twin, twin))
                    # if self.is_twin_changed(cur_twin, twin):
                    Messenger().push(event_type=Messenger().EVENT_ADT_MSG, payload=twin)

                    copy.copy(twin).pop('$metadata') # mutating the twin dict, we need it only to log into console for our reference
                    carb.log_info(f"[Twin pulled][{twin['$dtId']}] => {twin}")

                if self._adt_tree_view_data == None:
                    list_placeholder = []
                    for key in self._twins_dict:
                        # print (f"{key}---------{self._twins_dict[key]}")
                        list_placeholder.append(key)
                    self._adt_tree_view_data = ListModel(*list_placeholder)

                    with self._ui_twins_list_frame:
                        self._adt_tree_view_handler = ui.TreeView(
                            self._adt_tree_view_data,
                            root_visible=False,
                            header_visible=False,
                            style=style,
                            selection_changed_fn=self.on_twin_selected_in_list
                            # drop_between_items=True,
                        )

            except HttpResponseError as e:
                print("\n {0}".format(e.message))

            time.sleep(self._pulling_delay)

    # async def _send_message(self):
    #     uri = "ws://localhost:3000/67"
    #     async with websockets.connect(uri) as websocket:
    #         await websocket.send(self.label1.text)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

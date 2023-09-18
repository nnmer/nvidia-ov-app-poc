import threading
import os
import asyncio
from typing import Callable
from azure.digitaltwins.core import DigitalTwinsClient
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.core.exceptions import HttpResponseError as HRE

class HttpResponseError(HRE):
    pass


class ADT:

    pulling_delay = int(os.environ['OV_ADT_PULLING_FREQUENCY']) # in seconds

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

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ADT, cls).__new__(cls)
            cls._adt_service_client = None
        return cls.instance

    def dt_update_property(self, dt_id: str, prop_path: str, value):
        patch = [
            {
                "op": "replace",
                "path": prop_path,
                "value": value
            }
        ]

        self.service_client().update_digital_twin(dt_id, patch, logging_enable=bool(os.environ['OV_DEBUG']))

    def do_disconnect(self):
        self._adt_service_client = None

    def do_connect(self):
        self.service_client()

    def service_client(self) -> DigitalTwinsClient:
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
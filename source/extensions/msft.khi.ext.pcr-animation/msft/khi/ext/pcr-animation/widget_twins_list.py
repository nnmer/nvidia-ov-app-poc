import omni.ui as ui
import omni.usd
import os
import carb
import copy
from msft.ext.adt import MsftAdtWindow, ADT, AdtUtils, AdtPullingRegistry, Messenger, ListModel, HttpResponseError, ViewportUtils, style

class TwinsListWidget:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(TwinsListWidget, cls).__new__(cls)
            cls._adt_tree_view_handler = None
            cls._twins_dict = {}
            cls._adt_tree_view_data = None
            cls._ui_twins_list_frame = None
        return cls.instance

    @property
    def twins(self):
        return self._twins_dict

    def render(self):
        with ui.VStack():
            self._ui_twins_list_frame = ui.ScrollingFrame(
                name="twins_list_frame",
                horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                style_type_name_override="TreeView",
                height=100,
                style=style
            )

    def _re_draw(self):
        with self._ui_twins_list_frame:   
            pass

    def _register_adt_twins_pull_action(self):
        try:
            #model = self._service_client().get_digital_twin(model_id)
            #query_expression = 'SELECT * FROM digitaltwins dt WHERE STARTSWITH(dt.$metadata.$model,\'dtmi:PCR:PCR_Container_System\')'
            site = os.environ["OV_AZURE_DIGITALTWINS_ROOT_NODE_ID"]
            if bool(site) == False:
                carb.log_error('OV_AZURE_DIGITALTWINS_ROOT_NODE_ID environment variable should be set')
                return
            query_expression = f"SELECT RobotArm FROM DIGITALTWINS MATCH (Site)-[]-()-[]-()-[]-()-[]-(RobotArm) WHERE Site.$dtId = '{site}' and STARTSWITH(RobotArm.$dtId,'RS07N_')"
            query_result = ADT().service_client().query_twins(query_expression)

            for twin in query_result:
                twin = twin['RobotArm']
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

        self._re_draw()


    def on_twin_selected_in_list(self, selected_keys):
        paths = []
        for key in selected_keys:
            paths.append(AdtUtils.get_adt2prim_mapping(repr(key)))

        if len(paths) > 0:
            omni.usd.get_context().get_selection().set_selected_prim_paths(paths, True)
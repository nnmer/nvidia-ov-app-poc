
class AdtUtils:
    _map_dt_id2mesh_id = {
        # "RS07N_for_NAEP" : '/World/khi_rs007n_vac_UNIT2',
        # "RS07N_for_RPP" : '/World/khi_rs007n_vac_UNIT4',
        # "RS07N_for_PIP" : '/World/khi_rs007n_vac_UNIT3',
        # "RS07N_for_ODP" : '/World/khi_rs007n_vac_UNIT1',

        "RS07N_for_NAEP_Haneda" : '/World/khi_rs007n_vac_UNIT2',
        "RS07N_for_RPP_Haneda" : '/World/khi_rs007n_vac_UNIT4',
        "RS07N_for_PIP_Haneda" : '/World/khi_rs007n_vac_UNIT3',
        "RS07N_for_ODP_Haneda" : '/World/khi_rs007n_vac_UNIT1',
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

    @staticmethod
    def get_adt2prim_mapping(key: str = None):
        if key:
            return AdtUtils._map_dt_id2mesh_id[key]
        return AdtUtils._map_dt_id2mesh_id

    @staticmethod
    def find_dt_id_by_prim_from_map(prim_path: str):
        map = AdtUtils.get_adt2prim_mapping()
        target = None
        for k in map:
            # print(f"kkkk--->{k}")
            if prim_path.startswith(map[k]):
                target = k
                break

        return target
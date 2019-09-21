from ask_sdk_core.utils.request_util import get_slot


def get_slot_data(handler_input, slot_name):
    specific_slot_data_request = get_slot(handler_input, slot_name)
    specific_slot_data = specific_slot_data_request.resolutions.resolutions_per_authority[0]
    slot_data_dictionary = {}
    slot_data_dictionary['data'] = specific_slot_data
    slot_data_dictionary['status_code'] = specific_slot_data.status.code
    try:
        slot_data_dictionary['defined_value'] = specific_slot_data.values[0].value.name
        slot_data_dictionary['defined_value_id'] = specific_slot_data.values[0].value.id
    except:
        slot_data_dictionary['defined_value'] = None
    return slot_data_dictionary

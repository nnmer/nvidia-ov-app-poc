import carb.events
import omni.kit.app

class Messenger:
    """
    Omni app common event bus wrapper for current extension data flow events

    more about omni events @link https://docs.omniverse.nvidia.com/kit/docs/kit-manual/latest/guide/event_streams.html
    """

    EVENT_ADT_MSG = None
    EVENT_SIGNALR_MSG = None
    EVENT_ADT_LIST_ITEM_SELECTED = None
    EVENT_LOADING_COMPLETED = None
    bus = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Messenger, cls).__new__(cls)
            cls.bus = omni.kit.app.get_app().get_message_bus_event_stream()
            cls.EVENT_ADT_MSG = carb.events.type_from_string("msft.ext.adt.event.msg-adt")
            cls.EVENT_SIGNALR_MSG = carb.events.type_from_string("msft.ext.adt.event.msg-signalr")
            cls.EVENT_ADT_LIST_ITEM_SELECTED = carb.events.type_from_string("msft.ext.adt.event.adt-list-item-selected")
            cls.EVENT_LOADING_COMPLETED = carb.events.type_from_string("msft.ext.adt.event.loading-completed")
            """ fires when all needed preparation are done, i.e. stage have been setup, layers, connections etc."""
        return cls.instance

    def __init__(self, **kwargs):
        # Common event bus. It is event queue which is popped every update (frame).
        # self.bus = omni.kit.app.get_app().get_message_bus_event_stream()
        pass

    """
    on_event expected to be:

    def on_event(e: carb.events.IEvent):
        print(e.type)
        print(e.payload)
        if e.type == omni.kit.app.POST_QUIT_EVENT_TYPE:
            print("do your stuff...")
    """

    def subscribe_deffered(self, event_type: int, on_event):
        """
        return bus subscription handler carb.events.ISubscription
        """
        return self.bus.create_subscription_to_pop_by_type(event_type, on_event)

    def subscribe_immediate(self, event_type: int, on_event):
        """
        return bus subscription handler carb.events.ISubscription
        """
        return self.bus.create_subscription_to_push_by_type(event_type, on_event)

    def push(self, event_type: int, payload: dict = {}):
        self.bus.push(event_type, payload=payload)

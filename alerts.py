
class Alert:

    def __init__( self, name="", active=False, length=10, text=None, run=None ):

        self.name = name                # A name for the alert
        self.active = active            # Whether or not the alert is active
        self.length = length            # How often, in seconds, the alert runs
        self.text = text                # Text displayed when the alert is triggered
        self.timer = 0                  # Keeps track of time
        self.run = run                  # Function reference to run when the alert is triggered

    def setActive(self):
        self.active = True

    def setInactive(self):
        self.active = False

    def reset(self):
        self.timer = 0

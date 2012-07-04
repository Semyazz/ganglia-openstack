# -*- encoding: utf-8 -*-
__docformat__ = 'restructuredtext en'

from ceilometer import plugin

from jsonrpc2_zeromq import RPCNotificationServer
from jsonrpc2_zeromq import RPCNotifierClient

class JsonServer(RPCNotificationServer):

    _update_configuration = False

    def handle_update_stats_method(self, stats):
        """ New stats from Ganglia
        :param stats: new stats
        :type stats: Dict
        """
        print str(stats)

        if self._update_configuration:
            print "Sent rrd_rrotdir"
            return ["rrd_rootdir"]

        return None

    def handle_update_ganglia_configuration_method(self, configuration):
        print str(configuration)
        self._update_configuration = False
        self.cfg = configuration

    def update_ganglia_configuration(self):
        self._update_configuration = True

class GangliaPlugin(plugin.PollsterBase):
    """ Ganglia connector """

    def __init__(self):
        pass

    def init_queue(self):
        connection_address = "tcp://127.0.0.1:90000" #TODO move to confguration file
        self.receiver = JsonServer(connection_address)
        #self.receiver.handle_update_ganglia_configuration_notification = self.update_ganglia_configuration
        #self.receiver.handle_update_stats_method = self.received_stats_event
        try:
            self.receiver.start()
        except Exception as err:
            print err.message

    def get_rrds_directory(self):
        if not self.rrd_directory:
            self.rrd_directory = self.client.get_rrds_directory()

    def update_ganglia_configuration(self, configuration_json):
        """

        :param configuration_json: Json Ganglia's configuration
        :type configuration_json: Dict
        """
        self. rrd_directory = configuration_json.rrds_directory

    def received_stats_event(self, stats):
        """

        :param stats: Xml stats from Ganglia in Json array {"data" : "<xml data>"}
        :type stats: Dict
        """
        self.last_stats = stats.data
        self.notify_observer()

    def notify_observer(self):
        """
        Event. Notifies observer.
        """
        pass

    def get_counters(self, manager, context):

        if self.last_stats:
            return self.last_stats
        else:
            return None


if __name__ == "__main__":
    print "Starting"
    listener = GangliaPlugin()
    listener.init_queue()
    print "ops"
    listener.receiver.update_ganglia_configuration()


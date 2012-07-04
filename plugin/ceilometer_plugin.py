# -*- encoding: utf-8 -*-

__docformat__ = 'restructuredtext en'

import threading
import logging

from time import time
import time
from Gmetad import gmetad_plugin
#from jsonrpc2_zeromq import RPCNotifierClient
from jsonrpc2_zeromq import NotificationReceiverClient

from Gmetad.gmetad_plugin import GmetadPlugin
from Gmetad.gmetad_config import getConfig, GmetadConfig

def get_plugin():
    return CeilometerPlugin('ceilometer')

class CeilometerPlugin(GmetadPlugin):

    configuration = None

    CONNECTION_ADDRESS = 'connection_address'
    TIMEOUT = 'timeout'
    RRD_DIR = "rrd_rootdir"

    _cfgDefaults = {
        CONNECTION_ADDRESS : "tcp://127.0.0.1:99993",
        TIMEOUT : 1000,
        RRD_DIR : "/var/lib/ganglia/rrds"
    }

    def __init__(self, cfgid):
        self.cfg = None
        self.kwHandlers = None
        self._reset_config()

        try:
            self.rrdPlugin = gmetad_plugin._plugins
#            print str(self.rrdPlugin)

            GmetadPlugin.__init__(self, cfgid)
            self.ceilometer = NotificationReceiverClient(self.cfg[CeilometerPlugin.CONNECTION_ADDRESS])
            self.ceilometer.timeout = self.cfg[CeilometerPlugin.TIMEOUT]
            self._send_lock = threading.Lock()
            logging.info("Initialized notifier")
        except Exception, err:
            logging.error('Unable to start CeilometerPlugin. Cannot connect to ceilometer. Msg: %s', str(err))
            raise Exception()


    def _parseConfig(self, cfgdata):
        for kw,args in cfgdata:
            if self.kwHandlers.has_key(kw.lower()):
                self.kwHandlers[kw.lower()](args)

    def _parse_config(self, cfgdata):
        self._parseConfig(cfgdata)

    def _reset_config(self):
        self.cfg = CeilometerPlugin._cfgDefaults
        self.kwHandlers = {
                CeilometerPlugin.CONNECTION_ADDRESS : self._parse_connection_address,
            }
#        print str(self.kwHandlers)

    def _parse_connection_address(self, connection_address_string):
        self.cfg[CeilometerPlugin.CONNECTION_ADDRESS] = connection_address_string
        #TODO: Add connection string validation

    def _parse_reply(self, params):
#        logging.info("Get reply %s", str(params))
        if params is None:
            return

        answer = {}

        for demand in params:
            if self.cfg.has_key(demand):
                answer[demand] = self.cfg[demand]

        self.ceilometer.notify.update_ganglia_configuration(answer)

    def _get_message(self, clusterNode, metricNode):

        metricName = metricNode.getAttr('name')
        values = metricName.split('.',1)
        vmName = None

        if len(values) > 1:
            vmName = values[0]
            metricName = ".".join(values[1:])

        slope = metricNode.getAttr('slope')
        if slope.lower() == 'positive':
            dsType = 'COUNTER'
        else:
            dsType = 'GAUGE'

        processTime = clusterNode.getAttr('localtime')
        if processTime is None:
            processTime = int(time())

        heartbeat = 8

        args = {'time': processTime,
                'metricName': metricName,
                'value': metricNode.getAttr('val'),
                'units' : metricNode.getAttr('units'),
                'type' : metricNode.getAttr('type'),
            }

        if vmName is not None:
            args["instance_name"] = vmName
#        logging.info(args)
        return args


    def notify(self, clusterNode):

#        logging.error('CeilometerPlugin: ClusterNode')

        clusterPath = '%s' % (clusterNode.getAttr('name'))
        if 'GRID' == clusterNode.id:
            clusterPath = '%s/__SummaryInfo__'%clusterPath

        # We do not want to process grid data
        if 'GRID' == clusterNode.id:
            return None

        for hostNode in clusterNode:
            for metricNode in hostNode:
                # Don't update metrics that are numeric values.
                if metricNode.getAttr('type') in ['string', 'timestamp']:
                    continue
                hostPath = '%s/%s'%(clusterPath, hostNode.getAttr('name'))
#                metric_full_name = '%s/%s'%(hostPath, metricNode.getAttr('name'))
                msg = self._get_message(clusterNode, metricNode)
                msg["host"] = hostPath
                msg["clusterName"] = clusterNode.getAttr('name')

                if msg is not None:
                    with self._send_lock:
                        try:
                            reply = self.ceilometer.update_stats(msg)
                            self._parse_reply(reply)
                        except Exception, e:
                            logging.error("CeilometerPlugin: Error during notification. %s", str(e))


#        gmetadConfig = getConfig()
#
#        GmetadPlugin.notify(self, clusterNode)
#
#        if not clusterNode:
#            data = {"data": "<cpu_temp>72</cpu_temp>"}
#
#        with self._send_lock:
#            try:
#                reply = self.ceilometer.update_stats(clusterNode)
#                if reply:
#                    self.ceilometer.notify.update_ganglia_configuration(self.configuration)
#            except Exception as err:
#                print err.message

#        for hostNode in clusterNode:
#            for metricNode in hostNode:
#                if metricNode.getAttr('type') in ['string', 'timestamp']:
#                    continue
#
#                print metricNode

    def start(self):
        logging.info('CeilometerPlugin: Start')
        #self.cfg

    def stop(self):
        logging.info('CeilometerPlugin: Stop')



#    def ceilometer_isalive(self):
#
#        isalive_timeout = self.REQUEST_TIMEOUT
#
#        if self.ceilometer:
#            self.ceilometer.timeout = isalive_timeout
#
#        _ceilometer_alive = False
#        while not _ceilometer_alive:
#            self._counter += 1
#            error = None
#            reply = None
#
#            try:
#                reply = self.ceilometer.alive(self._counter)
#                assert _ceilometer_alive == False
#            except Exception as err:
#                error = err
#                _ceilometer_alive = False
#
#            if reply and int(reply) == self._counter:
#                _ceilometer_alive = True
#                assert self._ceilometer_alive == True
#                try:
#                    self.ceilometer.notify.update_ganglia_configuration(self.configuration)
#                except Exception as err:
#                    error = err
#                    _ceilometer_alive = False
#
#            if error == None:
#                assert _ceilometer_alive == True
#
#        self.ceilometer.timeout = self.REQUEST_TIMEOUT


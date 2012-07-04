ZeroMQ <-> ceilometer plugin.
============================

Configuration file
------------------
gmetad-plugin.conf copy to

    /etc/ganglia/gmetad-python.conf


Run
---

    python gmetad-python --conf=/etc/ganglia/gmetad-plugin.conf


Dependencies
------------
* jsonrpc2_zeromq
* rrdtool
* ganglia - http://ganglia.info - download and install Gmond. Run gmetad-python
* Host sFlow - http://host-sflow.sourceforge.net/

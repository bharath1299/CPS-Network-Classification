import time
from logfile import log_resource_utilization
try:
    from .flows import Flow
except:
    try:
        from flows import Flow
    except Exception as e:
        raise ValueError(e)

class FlowGenerator(object):
    """Generator for Flows from packets extraced using reader.Reader.read()"""

    def combine(self, packets):
        """Combine individual packets into a flow representation

            Parameters
            ----------
            packets : np.array of shape=(n_samples_packets, n_features_packets)
                Output from Reader.read

            Returns
            -------
            flows : dict
                Dictionary of flow_key -> Flow()
            """
        # Initialise result
        result = dict()
        start_time = time.time()
        data_processed=0

        # For each packet, add it to a flow
        for packet in packets:
            key = (packet[0], packet[1], packet[2])
            # Add packet to flow
            result[key] = result.get(key, Flow()).add(packet)
            data_processed +=1

        log_resource_utilization("After flow generation", data_processed=data_processed, start_time=start_time)

        # Return result
        return result

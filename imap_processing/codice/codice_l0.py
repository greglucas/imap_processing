"""Perform CoDICE L0 processing.

This module contains a function to decommutate CoDICE CCSDS packets using
XTCE packet definitions.

For more information on this process and the latest versions of the packet
definitions, see https://lasp.colorado.edu/galaxy/display/IMAP/CoDICE.

Use
---

    from imap_processing.codice.codice_l0 import decom_packets
    packet_file = '/path/to/raw_ccsds_20230822_122700Z_idle.bin'
    xtce_document = '/path/to/P_COD_NHK.xml'
    packet_list = decom_packets(packet_file, xtce_document)
"""

from imap_processing import decom


def decom_packets(packet_file: str, xtce_document) -> list:
    """Decom CoDICE data packets using CoDICE packet definition.

    Parameters
    ----------
    packet_file : str
        Path to data packet path with filename.
    xtce_document : str
        Path to the XTCE document file.

    Returns
    -------
    list : list
        all the unpacked data.
    """
    return decom.decom_packets(packet_file, xtce_document)

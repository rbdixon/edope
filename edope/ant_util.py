def is_ant(pkt):
    res = False

    if hasattr(pkt.content, 'data'):
        if len(pkt.content.data) > 0:
            if pkt.content.data[0] == 0xA4:
                res = True

    return res


def has_payload(pkt, cls):
    try:
        pkt[cls]
        return True
    except IndexError:
        return False

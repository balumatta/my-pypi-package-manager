import os
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def datetime_equals(date1, date2):
    if isinstance(date1, datetime):
        date1 = date1.strftime("%d/%m/%Y, %H:%M:%S")
    if isinstance(date2, datetime):
        date2 = date2.strftime("%d/%m/%Y, %H:%M:%S")

    if date1 == date2:
        return True

    return False


def convert_to_camel_case(str):
    res = [str[0].lower()]
    for c in str[1:]:
        if c in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
            res.append('_')
            res.append(c.lower())
        else:
            res.append(c)

    return ''.join(res)


if __name__ == '__main__':
    logger.info(convert_to_camel_case('NFRepCode'))

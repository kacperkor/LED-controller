import numpy as np
from requests import post, Timeout, Response
from datetime import datetime

from python_code.defaults import url, passwords


class ColorData:
    def __init__(self, brightness, **kwargs):
        self.directory = ''
        self.brightness = brightness


class PWM(ColorData):
    def __init__(self, r, g, b, c, w, brightness=0):
        super(PWM, self).__init__(brightness)
        self.directory = 'direct'
        self.__dataarray = np.array([r, g, b, c, w], dtype=np.uint16)

    def update(self, which: str, value: float):
        """r,g,b,c,w,value; 0-4095 range"""
        if which == 'r':
            self.__dataarray[0] = value
        elif which == 'g':
            self.__dataarray[1] = value
        elif which == 'b':
            self.__dataarray[2] = value
        elif which == 'c':
            self.__dataarray[3] = value
        elif which == 'w':
            self.__dataarray[4] = value
        else:
            raise AttributeError("invalid channel")

    def updateall(self, r, g, b, c, w, brightness):
        self.__dataarray = np.array([r, g, b, c, w], dtype=np.uint16)
        self.brightness = brightness

    def percent_data(self):
        return list(self.__dataarray/4.095)

    def raw_data(self):
        return list(self.__dataarray / 1.0124 * (self.brightness / 1000.) + 50)

    def ready_data(self, zone):
        zone -= 1
        plytka = zone // 3 + 1
        zone = zone % 3
        datadict = {"pwm": plytka, 'pwd': passwords[zone]}
        for i, channel in enumerate(self.raw_data()):
            datadict.update({zone*5+i: round(channel)})
        return datadict


class Colors(ColorData):
    def __init__(self, brightness=1000, **kwargs):
        super(Colors, self).__init__(brightness, **kwargs)
        self.__colorlist = []
        self.effect = ''

    def __str__(self):
        string = 'Colors stored:\n\tRed  \tGreen\tBlue '
        for i, color in enumerate(self.__colorlist):
            string += '\n' + str(i+1)
            for channel in color:
                string += '\t' + '%.4f' % channel

        return string

    def __getitem__(self, key):
        return self.__colorlist[key]

    def __setitem__(self, key, value):
        self.__colorlist[key] = value

    def __len__(self):
        return len(self.__colorlist)

    def append(self, data: list):
        if not isinstance(data, list):
            raise TypeError('Only a list can store RGB values')

        if len(data) < 3:
            for _ in range(0, 3 - len(data)):
                data.append(0)
        elif len(data) > 3:
            for _ in range(0, len(data) - 3):
                data.pop()

        for i, channel in enumerate(data):
            data[i] = float(channel)
            if channel > 1.:
                data[i] = 1.

        self.__colorlist.append(data)

    def pop(self, key):
        self.__colorlist.pop(key)

    def percent_data(self):
        return 'no percent data'

    def raw_data(self):
        return np.array(self.__colorlist) * 4095 * self.brightness / 1000

    def ready_data(self, zone):
        zone -= 1
        plytka = zone // 3 + 1
        zone = zone % 3
        datadict = {'pwm': plytka, 'pwd': passwords[zone], 'eff': self.effect}
        for i, color in enumerate(self.raw_data()):
            for j, channel in enumerate(color):
                datadict.update({i*3+j: round(channel)})
        return datadict


def handle_request(data, zone: int):
    print(data.percent_data(), zone, '\n', data.ready_data(zone))
    a = datetime.now()
    try:
        response = post(f'http://{url}/{data.directory}', data=data.ready_data(zone), timeout=1)
    except Timeout:
        response = Response()
        response.status_code = 408
        response._content = "Request timed out"
    except OSError:
        response = Response()
        response._content = "No internet connection"
    print((datetime.now() - a).microseconds // 1000 + (datetime.now()-a).seconds * 1000, 'ms',
          response, f'from {url}/{data.directory}:', response.content)

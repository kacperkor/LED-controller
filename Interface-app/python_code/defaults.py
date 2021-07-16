import json

try:
    inifile = open('main.ini', 'rt')
    length = len(inifile.readlines())
    inifile.seek(0)
    line = ''
    current = 0

    while line != '[general]\n':
        line = inifile.readline()
        current += 1
        if current > length:
            line = False

    if line is not False:
        general_defaults = inifile.readlines()[:2]
        url = general_defaults[0][len('url = '):-len('\n')]
        zone_number = int(general_defaults[1][len('zone_number = '):-len('\n')])
    else:
        url = '192.168.0.100'
        zone_number = 2

    inifile.close()
except FileNotFoundError:
    line = False
    url = '192.168.0.100'
    zone_number = 2


print('URL:', url)
print('Number of zones:', zone_number)


manuals = []
predefineds = []
passwords = []


def general_panel():
    dump = [
        {
          "type": "title",
          "title": "General settings"
        },
        {
          "type": "string",
          "title": "IP Adress",
          "desc": "Type the IP adress of the server",
          "section": "general",
          "key": "url"
        },
        {
          "type": "numeric",
          "title": "Number of zones",
          "desc": "Number of zones connected to the server",
          "section": "general",
          "key": "zone_number"
        }
    ]
    return json.dumps(dump)


def zone_panel():
    dump = []
    for i in range(1, zone_number + 1):
        single_dump = [
            {
                'type': 'title',
                'title': f'Zone {str(i)}'
            },
            {
                'type': 'string',
                'title': 'Password',
                'desc': f'Password to zone {str(i)}',
                'section': 'zone',
                'key': f'password_{i}'
            }
        ]
        dump.extend(single_dump)
    return json.dumps(dump)


def general():
    general_conf = {
        'url': url,
        'zone_number': zone_number
    }
    return general_conf


def zone():
    zone_conf = {}
    for i in range(1, zone_number + 1):
        zone_conf.update({
            f'password_{i}': 'qwerty'
        })
    return zone_conf

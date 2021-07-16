from requests import post, Timeout, Response

from python_code.classes import PWM
import datetime

url = ''


def direct(dane: PWM, strefa: int, directory: str):
    print(dane.percent_data(), strefa, '\n', dane.ready_data(strefa))
    a = datetime.datetime.now()
    try:
        response = post(f'http://{url}/{dane.directory}', data=dane.ready_data(strefa), timeout=1)
    except Timeout:
        response = Response()
        response.status_code = 408
        response._content = "Request timed out"
    except OSError:
        response = Response()
        response._content = "No internet connection"
    c = datetime.datetime.now() - a
    print(url, c.microseconds//1000, 'ms', response, response.content)


def predefined(dane, strefa: int):
    pass


"""
dane = PWM(100, 10, 50, 1, 100, 50)
print(dane.raw_data())



times = []

for i in range(50):
    a = datetime.datetime.now()
    response = post('http://192.168.1.107/direct', data=dane.ready_data(2))
    b = datetime.datetime.now()
    c = b-a
    times.append(c.microseconds//1000)
    print(response.status_code)

print(times)
timesr = np.array(times)
times.clear()

for i in range(50):
    a = datetime.datetime.now()
    req = request.Request('http://192.168.1.107/direct', data=parse.urlencode(dane.ready_data(2)).encode(),
                          method='POST')
    response = request.urlopen(req)
    b = datetime.datetime.now()
    c = b-a
    times.append(c.microseconds//1000)
    print(response.status)

print(times)
timesu = np.array(times)

print(f"\nRequests:\n"
      f"Average: {np.average(timesr)}\n"
      f"Max: {np.max(timesr)}\n"
      f"Min: {np.min(timesr)}\n"
      f"Deviation: {np.std(timesr)}")

print(f"\nurllib:\n"
      f"Average: {np.average(timesu)}\n"
      f"Max: {np.max(timesu)}\n"
      f"Min: {np.min(timesu)}\n"
      f"Deviation: {np.std(timesu)}")
"""
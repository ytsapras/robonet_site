import numpy as np
from sys import argv
from . import utilities

def romecheck(radeg, decdeg):
    lhalf = 0.220833333333  # 26.5/(120.)
    field, rate = -1, -1
    fields = [[267.835895375, -30.0608178195, 64.0],
              [269.636745458, -27.9782661111, 49.0],
              [268.000049542, -28.8195573333, 46.0],
              [268.180171708, -29.27851275, 58.0],
              [268.35435, -30.2578356389, 64.0],
              [268.356124833, -29.7729819283, 90.0],
              [268.529571333, -28.6937071111, 72.0],
              [268.709737083, -29.1867251944, 83.0],
              [268.881108542, -29.7704673333, 83.0],
              [269.048498333, -28.6440675, 75.0],
              [269.23883225, -29.2716684211, 70.0],
              [269.39478875, -30.0992361667, 42.0],
              [269.563719375, -28.4422328996, 49.0],
              [269.758843, -29.1796030365, 67.0],
              [269.78359875, -29.63940425, 61.0],
              [270.074981708, -28.5375585833, 61.0],
              [270.81, -28.0978333333, -99.0],
              [270.290886667, -27.9986032778, 52.0],
              [270.312763708, -29.0084241944, 48.0],
              [270.83674125, -28.8431573889, 49.0]]

    for idx in range(len(fields)):
        if radeg < fields[idx][0] + lhalf and\
           radeg > fields[idx][0] - lhalf and\
           decdeg < fields[idx][1] + lhalf and\
           decdeg > fields[idx][1] - lhalf:
            return idx, fields[idx][2]

    return field, rate

if __name__ == '__main__':

    if len(argv) == 1:
        print('Useage:')
        print('>python field_check.py target_ra target_dec [sexigesimal format]')
        exit()

    ra = argv[1]
    dec = argv[2]

    (radeg, decdeg) = utilities.sex2decdeg(ra,dec)

    (field, rate) = romecheck(radeg, decdeg)
    print (field)

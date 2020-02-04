import csv
import random

from classes import CellType, TerrainCell

def dump_room(terrain, file='./room.csv'):
    add_row = []
    with open(file, 'w') as f:
        writer = csv.writer(f, delimiter=',')
        for row in terrain:
            for col in row:
                add_row.append(col.cell_type.value)
            writer.writerow(add_row)
            add_row = []


def load_room(file='./room.csv'):
    terrain = []
    add_row = []
    with open(file, 'r') as f:
        reader = csv.reader(f, delimiter=',')
        for i, row in enumerate(reader):
            for j, obj in enumerate(row):
                add_row.append(TerrainCell(i, j, cell_type=CellType[obj], dirt=random.randint(0, 6)))
            terrain.append(add_row)
            add_row = []
    return terrain

import datetime

class Plant:

    def __init__(self, name, soil_type='soil'):
        self.name = name
        self.soil_type = soil_type

    def plant(self, pot, soil, **kwargs):
        self.pot = pot
        self.soil = soil
        return f'Planting {self.name} in {pot} with {soil}'


if __name__ == '__main__':
    cactus = Plant('prickly')
    cactus.plant('pot1', 'soilmix1')
    cactus.water(datetime.timedelta(minutes=15))

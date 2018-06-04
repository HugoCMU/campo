import datetime
import uuid
from pathlib import Path
import pandas as pd


class Campo:
    """
        Campo (Field) holds methods for adding/removing new plants and looking up information
        regarding plants.
    """
    # Directory locations for logging
    root_dir = Path.cwd()
    img_dir = root_dir / 'local' / 'images'
    log_dir = root_dir / 'local' / 'logs'
    campo_file = log_dir / 'plants.csv'

    # Bare minimum columns for a campo dataframe
    cols = ['name', 'id', 'soil_type', 'seed_type', 'pot']

    def __init__(self):
        if not self.campo_file.exists():
            campo = pd.DataFrame(columns=self.cols)
            campo.to_csv(str(self.campo_file))
        # Load campo csv file into memory
        self.campo = pd.read_csv(str(self.campo_file))

    def new_plant(self, **kwargs):
        # Make sure kwargs contains bare minimum columns, fill empties with -
        plant_attributes = kwargs
        for col in self.cols:
            if not kwargs.get(col, None):
                plant_attributes[col] = '-'

        # Unique identifier string per plant
        plant_attributes['id'] = uuid.uuid4()

        # Create entry in plants csv with this new plant
        new_row = pd.DataFrame(plant_attributes, index=[1])
        pd.concat([self.campo, new_row], sort=False).to_csv(str(self.campo_file))

    def lookup_plant(self, name):
        row = self.campo[self.campo['name'] == name]
        print(row)


if __name__ == '__main__':
    autogrow1 = Campo()
    autogrow1.new_plant(name='cactus', seed_type='pumpkin', last_name='joe')
    autogrow1.lookup_plant('cactus')

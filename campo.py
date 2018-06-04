import uuid
from pathlib import Path
import pandas as pd


def check_if_csv(filename):
    if filename[:-4] != '.csv':
        return filename + '.csv'
    return filename


def load_csv(filename, dir, default_cols):
    filename = check_if_csv(filename)
    file = dir / filename
    if not file.exists():
        pd.DataFrame(columns=default_cols).to_csv(str(file), index=False)
    return pd.read_csv(str(file))


class Campo:
    """
        Campo (Field) holds methods for adding/removing new plants and looking up information
        regarding plants.
    """
    # Directory locations for logging
    root_dir = Path.cwd()
    img_dir = root_dir / 'local' / 'images'
    log_dir = root_dir / 'local' / 'logs'

    # Bare minimum columns for a campo dataframe
    cols = ['name', 'id', 'soil_type', 'seed_type', 'pot']

    def __init__(self, filename=None):
        assert filename, 'Please provide a campo file'
        self.campo = load_csv(filename, self.log_dir, self.cols)

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
        self.campo.append(new_row, ignore_index=True, sort=False).to_csv(str(self.campo_file), index=False)

    def list_plants(self):
        return self.campo['name', 'id'].unique()

    def lookup_plant(self, name=None, id=None):
        assert not all([name, id]), 'name or id must be provided'
        row = self.campo[self.campo['name'] == name]
        assert len(row) <= 1, 'Multiple plants have the same name'
        return row


if __name__ == '__main__':
    autogrow1 = Campo(filename='test.csv')
    autogrow1.new_plant(name='cactus', seed_type='pumpkin', last_name='joe')
    autogrow1.lookup_plant('cactus')

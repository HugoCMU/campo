import uuid
# Repo specific imports
import util

class Campo:
    """
        Campo (Field) holds methods for adding/removing new plants and looking up information
        regarding plants.
    """

    # Bare minimum columns for a campo dataframe
    cols = ['name', 'id', 'soil_type', 'seed_type', 'pot']

    def __init__(self, filename=None):
        assert filename, 'Please provide the filename of campo when creating campo object'
        self.campo_filename = filename
        self.campo = util.load_csv(filename, cols=self.cols)

    def new_plant(self, **kwargs):
        # Make sure kwargs contains bare minimum columns, fill empties with -
        plant_attributes = kwargs
        for col in self.cols:
            if not kwargs.get(col, None):
                plant_attributes[col] = '-'
        # Unique identifier string per plant
        plant_attributes['id'] = uuid.uuid4()
        # Create entry in plants csv with this new plant
        self.campo = util.save_row(self.campo_filename, plant_attributes, df=self.campo)

    def list_plants(self):
        return list(self.campo.id.unique())

    def lookup_plant(self, name=None, id=None):
        assert not all([name, id]), 'name or id must be provided'
        row = self.campo[self.campo['name'] == name]
        assert len(row) <= 1, 'Multiple plants have the same name'
        return row


if __name__ == '__main__':
    print('Running tests for campo.py')
    c = Campo(filename='test_campo.csv')
    c.new_plant(name='cactus', seed_type='pumpkin', last_name='joe')
    print(c.lookup_plant('cactus'))
    print(c.list_plants())

import datetime
from pathlib import Path
import re
import tensorflow as tf
import tensorflow_hub as hub

# Enable eager execution
tf.enable_eager_execution()
tfe = tf.contrib.eager

# Load datasets (USE tf.data API)
root_dir = Path.cwd()
data_dir = root_dir / 'data' / 'images_and_annotations'
train_dir = data_dir / 'PSI_Tray031' / 'tv'
test_dir = data_dir / 'PSI_Tray032' / 'tv'
model_dir = root_dir / 'model'
PLANT_START_DATE = datetime.datetime(2015, 12, 14, hour=12, minute=54, second=51)
PLANT_AGE_MULT = 1.5 * 2592000  # Age of plant in seconds for normalizing


def plant_age_from_filename(filename):
    # Sample filename: PSI_Tray031_2015-12-26--17-38-25_top.png
    filename_regex = re.search(r'(201\d)-(\d+)-(\d+)--(\d+)-(\d+)-(\d+)', str(filename))
    year, month, day, hour, min, sec = (int(_) for _ in filename_regex.groups())
    date = datetime.datetime(year, month, day, hour=hour, minute=min, second=sec)
    plant_age = date - PLANT_START_DATE
    # Normalize age between 0 and 1
    return plant_age.total_seconds() / PLANT_AGE_MULT


def _parse_single(filename, label):
    # Decode and convert image to appropriate type
    image = tf.image.decode_png(tf.read_file(filename))
    image = tf.image.convert_image_dtype(image, tf.float32)  # Also scales from [0, 255] to [0, 1)
    # Resize according to module requirements
    image = tf.image.resize_images(image, [224, 224])
    return image, label


class AgeModel(tf.keras.Model):
    def __init__(self):
        super(AgeModel, self).__init__()
        self.encoder = tf.keras.applications.resnet50.ResNet50(include_top=False,
                                                               weights='imagenet',
                                                               pooling='avg',
                                                               )
        self.bn1 = tf.keras.layers.BatchNormalization()
        self.bn2 = tf.keras.layers.BatchNormalization()
        self.head_1 = tf.keras.layers.Dense(128, kernel_initializer='normal', activation='relu')
        self.head_2 = tf.keras.layers.Dense(1, kernel_initializer='normal')  # , activation='softmax')

    def predict(self, inputs):
        result = self.encoder(inputs)
        result = self.bn1(result)
        result = self.head_1(result)
        result = self.bn2(result)
        result = self.head_2(result)
        return result


def loss(model, input, target):
    output = model.predict(input)
    error = output - target
    # print(f'    inside loss. output = {output}, target = {target}, error = {error}')
    return tf.reduce_mean(tf.square(error))


def grad(model, input, target):
    with tfe.GradientTape() as tape:
        loss_value = loss(model, input, target)
        tf.contrib.summary.scalar('loss', loss_value)
    return tape.gradient(loss_value, model.variables)


SHUFFLE_BUFFER = 1
NUM_EPOCHS = 10
LEARNING_RATE = 0.0001
BATCH_SIZE = 8
LOG_EVERY_N_STEPS = 3

# Create a constants with filenames and plant age labels
filenames = tf.constant(list(str(file) for file in train_dir.glob('*.png')))
plant_ages = list(map(plant_age_from_filename, train_dir.glob('*.png')))
labels = tf.constant(plant_ages)
dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))

dataset = dataset.map(lambda filename, label: _parse_single(filename, label))
dataset = dataset.shuffle(SHUFFLE_BUFFER).repeat(NUM_EPOCHS).batch(BATCH_SIZE)

model = AgeModel()
optimizer = tf.train.AdamOptimizer(learning_rate=LEARNING_RATE)

# Tensorboard summary writer
writer = tf.contrib.summary.create_file_writer(str(model_dir))
global_step = tf.train.get_or_create_global_step()
writer.set_as_default()

for (i, (image, target)) in enumerate(tfe.Iterator(dataset)):
    global_step.assign_add(1)
    with tf.contrib.summary.record_summaries_every_n_global_steps(LOG_EVERY_N_STEPS):
        grads = grad(model, image, target)
        optimizer.apply_gradients(zip(grads, model.variables), global_step=global_step)
        if i % LOG_EVERY_N_STEPS == 0:  # nan errors on the losses after this point
            print(f'Step {i} Loss is {loss(model, image, target)}')

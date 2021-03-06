import datetime
from pathlib import Path
import re
import tensorflow as tf
# Repo specific imports
from model import PlantAgeModel

# Enable eager execution
tfe = tf.contrib.eager
tf.enable_eager_execution(device_policy=tfe.DEVICE_PLACEMENT_SILENT)

# Dataset/Model specific parameters
TRAIN_PATH = 'PSI_Tray031/tv'

# Training parameters
MODEL_CKPT = 'model.ckpt'
IMAGE_SIZE = [160, 160]
SHUFFLE_BUFFER = 1
NUM_EPOCHS = 10
LEARNING_RATE = 0.0001
BATCH_SIZE = 1
LOG_EVERY_N_STEPS = 3
SAVE_EVERY_N_STEPS = 5

# Directories
root_dir = Path.cwd()
data_dir = root_dir / 'data' / 'images_and_annotations'
train_dir = data_dir / TRAIN_PATH
model_dir = root_dir / 'model'
log_dir = root_dir / 'log'


def _plant_age_from_filename(filename):
    """
    Gets the plant age (0, 1) from image filename using regex. Dataset specific.
    :param filename: (str) image filename
    :return: (float) plant age (0, 1)
    """
    # Dataset specific constants
    PLANT_START_DATE = datetime.datetime(2015, 12, 14, hour=12, minute=54, second=51)
    PLANT_AGE_MULT = 1.5 * 2592000  # Age of plant in seconds for normalizing
    # Sample filename: PSI_Tray031_2015-12-26--17-38-25_top.png
    filename_regex = re.search(r'(201\d)-(\d+)-(\d+)--(\d+)-(\d+)-(\d+)', str(filename))
    year, month, day, hour, min, sec = (int(_) for _ in filename_regex.groups())
    date = datetime.datetime(year, month, day, hour=hour, minute=min, second=sec)
    plant_age = date - PLANT_START_DATE
    # Normalize age between 0 and 1
    return plant_age.total_seconds() / PLANT_AGE_MULT


def _parse_single(filename, label, image_size=IMAGE_SIZE):
    """
    Parse single data point (image, label)
    :param filename: (str) image filename
    :return: image, label
    """
    # Decode and convert image to appropriate type
    image = tf.image.decode_png(tf.read_file(filename))
    image = tf.image.convert_image_dtype(image, tf.float32)  # Also scales from [0, 255] to [0, 1)
    # Resize according to module requirements
    image = tf.image.resize_images(image, image_size)
    return image, label


def load_dataset(train_dir, shuffle_buffer=SHUFFLE_BUFFER, num_epochs=NUM_EPOCHS, batch_size=BATCH_SIZE):
    """
    Creates dataset object from a directory containing images
    :param train_dir: (Path) training data location
    :param shuffle_buffer: (int)
    :param num_epochs: (int)
    :param batch_size: (int)
    :return:
    """
    # Dataset creation from images (target is in filename)
    filenames = tf.constant(list(str(file) for file in train_dir.glob('*.png')))
    plant_ages = list(map(_plant_age_from_filename, train_dir.glob('*.png')))
    labels = tf.constant(plant_ages)
    dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))
    dataset = dataset.map(lambda filename, label: _parse_single(filename, label))
    dataset = dataset.shuffle(shuffle_buffer).repeat(num_epochs).batch(batch_size)
    # dataset = dataset.apply(tf.contrib.data.prefetch_to_device('/gpu:0'))
    return dataset


if __name__ == '__main__':

    model = PlantAgeModel()
    optimizer = tf.train.AdamOptimizer(learning_rate=LEARNING_RATE)

    # Tensorboard summary writer
    writer = tf.contrib.summary.create_file_writer(str(log_dir))
    writer.set_as_default()

    # Checkpoint model saver
    ckpt_file = str(model_dir / MODEL_CKPT)
    latest_ckpt = tf.train.latest_checkpoint(str(model_dir))  # Will return None if no checkpoint found
    if latest_ckpt:
        print(f'Restoring from checkpoint found at {latest_ckpt}')
    ckpt = tfe.Checkpoint(optimizer=optimizer, model=model, optimizer_step=tf.train.get_or_create_global_step())
    ckpt.restore(latest_ckpt)

    # Load dataset
    dataset = load_dataset(train_dir)

    # Train
    with tf.device('/gpu:0'):
        for (i, (image, target)) in enumerate(tfe.Iterator(dataset)):
            tf.assign_add(tf.train.get_or_create_global_step(), 1)
            with tf.contrib.summary.record_summaries_every_n_global_steps(LOG_EVERY_N_STEPS):
                grads, loss = model.grad(image, target)
                optimizer.apply_gradients(zip(grads, model.variables), global_step=tf.train.get_or_create_global_step())
                if i % LOG_EVERY_N_STEPS == 0:
                    print(f'Step {tf.train.get_or_create_global_step().numpy()} Loss is {loss}')
                if i % SAVE_EVERY_N_STEPS == 0:
                    print(f' ----- Saving model at {ckpt_file}')
                    ckpt.save(file_prefix=ckpt_file)  # , session=tf.get_default_session())

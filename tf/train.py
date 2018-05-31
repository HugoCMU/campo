import datetime
from pathlib import Path
import re
import tensorflow as tf
import tensorflow_hub as hub

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


def _parse_single(filename, label, train=True):
    # Decode and convert image to appropriate type
    image = tf.image.decode_png(tf.read_file(filename))
    # image = tf.image.convert_image_dtype(image, tf.float32)  # general image convention for modules
    # Resize according to module requirements
    image = tf.image.resize_images(image, [224, 224])
    # Augmentation in training
    if train:
        pass
        # image = tf.image.random_contrast(image)
        # image = tf.image.random_brightness(image)
    # return image, label
    return {'image': image}, label


def input_fn(image_dir, train=True, shuffle_buffer=10, num_epochs=4, batch_size=2):
    # Create a constants with filenames and plant age labels
    filenames = tf.constant(list(str(file) for file in image_dir.glob('*.png')))
    plant_ages = list(map(plant_age_from_filename, image_dir.glob('*.png')))
    labels = tf.constant(plant_ages)

    # dataset = tf.data.Dataset.list_files(str(image_dir / '*.png'))
    dataset = tf.data.Dataset.from_tensor_slices((filenames, labels))
    # Shuffle/Repeat data together for speed
    dataset = dataset.apply(
        tf.contrib.data.shuffle_and_repeat(shuffle_buffer, num_epochs))

    # Map function will be different on train and evaluation
    dataset = dataset.apply(
        tf.contrib.data.map_and_batch(lambda filename, label: _parse_single(filename, label, train), batch_size))

    # Use GPU prefetch to speed up training
    # dataset = dataset.apply(tf.contrib.data.prefetch_to_device('/gpu:0'))

    # Make iterator, and yield the next batch
    iterator = dataset.make_one_shot_iterator()
    features = iterator.get_next()
    return features
    # image, labels = iterator.get_next()
    # features = {'image': image}
    # return features, labels


# feature encoder is taken from tf hub
image_features = hub.image_embedding_column('image', 'https://tfhub.dev/google/imagenet/resnet_v1_50/feature_vector/1')

# Set up a run config
run_config = tf.estimator.RunConfig(
    save_checkpoints_steps=1,
    model_dir=str(model_dir),
)

# Build model (regression model on top of image features)
plant_model = tf.estimator.DNNRegressor(feature_columns=[image_features],
                                        hidden_units=[256, 128, 64],
                                        config=run_config)

# Train and evaluate
train_spec = tf.estimator.TrainSpec(input_fn=lambda: input_fn(train_dir))
eval_spec = tf.estimator.EvalSpec(input_fn=lambda: input_fn(test_dir, train=False))
tf.estimator.train_and_evaluate(plant_model, train_spec, eval_spec)

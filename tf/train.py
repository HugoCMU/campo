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
PLANT_START_DATE = datetime.datetime(2015, 12, 14, hour=12, minute=54, second=51)
PLANT_AGE_MULT = 1.5 * 2592000 # Age of plant in seconds for normalizing

# feature encoder is taken from tf hub
image_features = hub.image_embedding_column('plant-photo',
                                            'https://tfhub.dev/google/imagenet/nasnet_large/feature_vector/1')

# Build model (regression model on top of image features)
plant_model = tf.estimator.DNNRegressor(feature_columns=image_features,
                                        hidden_units=[256, 128, 64])


def parse_single_image(filename, train=True):
    # Decode and convert image to appropriate type
    image = tf.image.decode_png(tf.read_file(filename))
    image = tf.image.convert_image_dtype(image, tf.float32)  # general image convention for modules
    # Resize according to module requirements
    image = tf.image.resize_images(image, [331, 331])
    # Augmentation in training
    if train:
        image = tf.image.random_contrast(image)
        image = tf.image.random_brightness(image)
    # TODO: Use regex to extract target from filename
    # Sample filename: PSI_Tray031_2015-12-26--17-38-25_top.png
    filename_regex = re.search(r'(201\d)-(\d+)-(\d+)--(\d+)-(\d+)-(\d+)', filename)
    year, month, day, hour, min, sec = (int(_) for _ in filename_regex.groups())
    date = datetime.datetime(year, month, day, hour=hour, minute=min, second=sec)
    plant_age = date - PLANT_START_DATE
    # Normalize age between 0 and 1
    target = plant_age.total_seconds() / PLANT_AGE_MULT
    return image, target


def input_fn(image_dir,
             train=True,
             shuffle_buffer=600,
             num_epochs=20,
             batch_size=32):
    # Extract files
    files = tf.data.Dataset.list_files(image_dir)
    dataset = tf.data.TFRecordDataset(files)

    # Shuffle/Repeat data together for speed
    dataset = dataset.apply(
        tf.contrib.data.shuffle_and_repeat(shuffle_buffer, num_epochs))

    # Map function will be different on train and evaluation
    dataset = dataset.apply(
        tf.contrib.data.map_and_batch(lambda x: parse_single_image(x, train),
                                      batch_size))

    # Use GPU prefetch to speed up training
    dataset = dataset.apply(tf.contrib.data.prefetch_to_device('/gpu:0'))

    # Make iterator as final return type
    iterator = dataset.make_one_shot_iterator()
    features = iterator.get_next()

    # TODO:  Return must include feature vectors defined through hub encoder
    return ({'plant-photo':}, features)


# Train and evaluate
train_spec = tf.estimator.TrainSpec(input_fn=lambda: input_fn(str(train_dir)))
eval_spec = tf.estimator.EvalSpec(input_fn=lambda: input_fn(str(test_dir), train=False))
tf.estimator.train_and_evaluate(plant_model, train_spec, eval_spec)

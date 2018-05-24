from pathlib import Path
import re
import tensorflow as tf
import tensorflow_hub as hub

# Load datasets (USE tf.data API)
DATASET_NAME = 'bleh'
root_dir = Path.cwd()
train_dir = root_dir / 'data' / DATASET_NAME / 'train'
test_dir = root_dir / 'data' / DATASET_NAME / 'test'

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
    filename_regex = re.search(r'(201\d)-(\d++)-(\d++)--(\d++)-(\d++)-(\d++)', filename).group()
    date =
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

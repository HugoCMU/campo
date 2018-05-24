import tensorflow as tf
import tensorflow_hub as hub

# Load datasets (USE tf.data API)

# feature encoder is taken from tf hub
image_features = hub.image_embedding_column('plant-photo',
                                            'https://tfhub.dev/google/imagenet/nasnet_large/feature_vector/1')

# Build model (regression model on top of image features)
plant_model = tf.estimator.DNNRegressor(feature_columns=image_features,
                                        hidden_units=[256, 128, 64])


def input_fn(image_files):
    # Return must include feature vectors defined through hub encoder
    return ({'plant-photo':},)


# Train and evaluate
train_spec = tf.estimator.TrainSpec(input_fn=lambda: input_fn(TRAIN_FILES))
eval_spec = tf.estimator.EvalSpec(input_fn=lambda: input_fn(VAL_FILES))
tf.estimator.train_and_evaluate(plant_model, train_spec, eval_spec)

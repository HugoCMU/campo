import tensorflow as tf


class FarmerModel(tf.keras.Model):

    # This model should output daily schedules based on previous experience

    # Some important properties: Time series, long term memory important
    # Potential image input?
    # What is it trying to maximize? Plant age score? subjective human score?

    # Could schedules be described as a graph? If so what are the edges and the nodes?
    # (edges, nodes, global attribute)

    # One possible solution (looking at Box 3 in Relational NN paper)
    # Node: Action
    # Node Attributes: type (water, light, etc), type specific params (veg vs flower, pump, etc).
    # Edge: Start and end times? (Acting on it's own Node)
    # Edge Attributes: Start Time, Duration
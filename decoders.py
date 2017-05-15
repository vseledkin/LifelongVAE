import tensorflow as tf
import tensorflow.contrib.slim as slim
from encoders import _get_normalizer


class CNNDecoder(object):
    def __init__(self, sess, latent_size, input_size, is_training,
                 activation=tf.nn.elu, use_bn=False, use_ln=False,
                 scope="cnn_decoder"):
        self.sess = sess
        self.layer_type = "cnn"
        self.input_size = input_size
        self.latent_size = latent_size
        self.activation = activation
        self.use_bn = use_bn
        self.use_ln = use_ln
        self.scope = scope
        self.is_training = is_training

    def get_info(self):
        return {'activation': self.activation.__name__,
                'sizes': str(['128x3x3', '64x5x5',
                              '32x5x5', '1x5x5']),
                'use_bn': str(self.use_bn),
                'use_ln': str(self.use_ln)}

    def get_sizing(self):
        return str(['128x3x3', '64x5x5',
                    '32x5x5', '1x5x5', str(self.input_size)])

    def get_model(self, z):
        # get the normalizer function and parameters
        normalizer_fn, normalizer_params = _get_normalizer(self.is_training,
                                                           self.use_bn,
                                                           self.use_ln)

        winit = tf.contrib.layers.xavier_initializer_conv2d()
        # winit = tf.truncated_normal_initializer(stddev=0.01)
        with tf.variable_scope(self.scope):
            with slim.arg_scope([slim.conv2d_transpose],
                                activation_fn=self.activation,
                                weights_initializer=winit,
                                biases_initializer=tf.constant_initializer(0),
                                normalizer_fn=normalizer_fn,
                                normalizer_params=normalizer_params):
                # zshp = z.get_shape().as_list()
                z_flat = tf.reshape(z, [-1, 1, 1, self.latent_size])
                h0 = slim.conv2d_transpose(z_flat, num_outputs=128,
                                           kernel_size=[3, 3],
                                           padding='VALID')
                h1 = slim.conv2d_transpose(h0, num_outputs=64,
                                           kernel_size=[5, 5],
                                           padding='VALID')
                h2 = slim.conv2d_transpose(h1, num_outputs=32,
                                           kernel_size=[5, 5],
                                           stride=[2, 2], padding='SAME')

                h3 = slim.conv2d_transpose(h2, num_outputs=1, kernel_size=[5, 5],
                                           stride=[2, 2], padding='SAME',
                                           normalizer_fn=None, normalizer_params=None,
                                           activation_fn=None)
                return slim.flatten(h3)

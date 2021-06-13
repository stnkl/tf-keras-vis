from contextlib import contextmanager

import numpy as np
import pytest
import tensorflow as tf
from tensorflow.keras import backend as K
from tensorflow.keras.layers import Conv2D, Dense, GlobalAveragePooling2D, Input
from tensorflow.keras.models import Model

from ..activation_maximization.callbacks import Callback
from ..activation_maximization.input_modifiers import InputModifier
from ..activation_maximization.regularizers import Regularizer


def mock_dense_model():
    inputs = Input((8, ), name='input_1')
    x = Dense(6, activation='relu', name='dense_1')(inputs)
    x = Dense(2, activation='softmax', name='dense_2')(x)
    return Model(inputs=inputs, outputs=x)


def mock_conv_model_with_sigmoid_output():
    inputs = Input((8, 8, 3), name='input_1')
    x = Conv2D(6, 3, activation='relu', name='conv_1')(inputs)
    x = GlobalAveragePooling2D()(x)
    x = Dense(1, activation='sigmoid', name='dense_1')(x)
    return Model(inputs=inputs, outputs=x)


def mock_conv_model():
    inputs = Input((8, 8, 3), name='input_1')
    x = Conv2D(6, 3, activation='relu', name='conv_1')(inputs)
    x = GlobalAveragePooling2D()(x)
    x = Dense(2, activation='softmax', name='dense_1')(x)
    return Model(inputs=inputs, outputs=x)


def mock_multiple_inputs_model():
    input_1 = Input((8, 8, 3), name='input_1')
    input_2 = Input((10, 10, 3), name='input_2')
    x1 = Conv2D(6, 3, padding='same', activation='relu', name='conv_1')(input_1)
    x2 = Conv2D(6, 3, activation='relu', name='conv_2')(input_2)
    x = K.concatenate([x1, x2], axis=-1)
    x = GlobalAveragePooling2D()(x)
    x = Dense(2, activation='softmax', name='dense_1')(x)
    return Model(inputs=[input_1, input_2], outputs=x)


def mock_multiple_outputs_model():
    inputs = Input((8, 8, 3), name='input_1')
    x = Conv2D(6, 3, activation='relu', name='conv_1')(inputs)
    x = GlobalAveragePooling2D()(x)
    x1 = Dense(2, activation='softmax', name='dense_1')(x)
    x2 = Dense(1, activation='sigmoid', name='dense_2')(x)
    return Model(inputs=inputs, outputs=[x1, x2])


def mock_multiple_io_model():
    input_1 = Input((8, 8, 3), name='input_1')
    input_2 = Input((10, 10, 3), name='input_2')
    x1 = Conv2D(6, 3, padding='same', activation='relu', name='conv_1')(input_1)
    x2 = Conv2D(6, 3, activation='relu', name='conv_2')(input_2)
    x = K.concatenate([x1, x2], axis=-1)
    x = GlobalAveragePooling2D()(x)
    x1 = Dense(2, activation='softmax', name='dense_1')(x)
    x2 = Dense(1, activation='sigmoid', name='dense_2')(x)
    return Model(inputs=[input_1, input_2], outputs=[x1, x2])


def mock_conv_model_with_float32_output():
    inputs = Input((8, 8, 3), name='input_1')
    x = Conv2D(6, 3, activation='relu', name='conv_1')(inputs)
    x = GlobalAveragePooling2D()(x)
    x = Dense(2, dtype=tf.float32, activation='softmax', name='dense_1')(x)
    return Model(inputs=inputs, outputs=x)


def dummy_sample(shape, dtype=np.float32):
    length = np.prod(shape)
    values = np.array(list(range(length)))
    values = np.reshape(values, shape)
    values = values.astype(dtype)
    return values


def score_with_tuple(output):
    return tuple(o[0] for o in output)


def score_with_list(output):
    return list(o[0] for o in output)


NO_ERROR = 'NO_ERROR'


@contextmanager
def _does_not_raise():
    yield


def assert_error(e):
    if e is NO_ERROR:
        return _does_not_raise()
    else:
        return pytest.raises(e)


class MockCallback(Callback):
    def __init__(self,
                 raise_error_on_begin=False,
                 raise_error_on_call=False,
                 raise_error_on_end=False):
        self.on_begin_was_called = False
        self.on_call_was_called = False
        self.on_end_was_called = False
        self.raise_error_on_begin = raise_error_on_begin
        self.raise_error_on_call = raise_error_on_call
        self.raise_error_on_end = raise_error_on_end

    def on_begin(self, **kwargs):
        self.on_begin_was_called = True
        self.kwargs = kwargs
        if self.raise_error_on_begin:
            raise ValueError('Test')

    def __call__(self, *args):
        self.on_call_was_called = True
        self.args = args
        if self.raise_error_on_call:
            raise ValueError('Test')

    def on_end(self):
        self.on_end_was_called = True
        if self.raise_error_on_end:
            raise ValueError('Test')


class MockInputModifier(InputModifier):
    def __init__(self):
        self.seed_input = None

    def __call__(self, seed_input):
        self.seed_input = seed_input
        return seed_input


class MockRegularizer(Regularizer):
    def __init__(self, name='MockRegularizer'):
        self.name = name
        self.inputs = None

    def __call__(self, inputs):
        self.inputs = inputs
        return inputs


class MockGradientModifier():
    def __init__(self):
        self.gradients = None

    def __call__(self, gradients):
        self.gradients = gradients
        return gradients

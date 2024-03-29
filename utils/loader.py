# Ensure you have downloaded the OxPet dataset and unzipped it to datasets folder
# Images are 256x256x3
import h5py
import os
import tensorflow as tf


class Generator:
    ''' 
        Generator yields inputs from file efficiently. File is opened once
        and yields until outputs are exhausted without loading entire ds into memory.
    '''

    def __init__(self, path, batch_size):
        self.path = path
        self.batch_size = batch_size

    def __call__(self): # We are allowed to pre-shuffle and load which could be faster and a better fix
        with h5py.File(self.path, 'r') as f:  # With scope for safe file exit incase memleaks
            d_name = list(f.keys())[0]
            num_images = len(f[d_name])
            hp = int(num_images*0.5372)  # Weird fix :)

            for i in range(self.batch_size//2, num_images//2, self.batch_size//2):
                yield tf.concat([tf.cast(f[d_name][i-(self.batch_size//2):i], tf.float32), tf.cast(f[d_name][hp+i-(self.batch_size//2):hp+i], tf.float32)], axis=0)


class DataLoader:
    def __init__(self, batch_size):
        # Paths relative to working directory
        self.img_path = r'images.h5'
        self.mask_path = r'masks.h5'
        self.bbox_path = r'bboxes.h5'
        self.bin_path = r'binary.h5'
        self.train_path = r'datasets/train'
        self.val_path = r'datasets/val'

        # Configs
        self.batch_size = batch_size

    def load_ds_generator(self, path, val=False):
        ''' 
            Loads and returns batched tf.Dataset generator object from passed path. 
            If val: loads validation set. 
        '''
        ds = tf.data.Dataset.from_generator(
            Generator(os.path.join(
                self.train_path if not val else self.val_path, path), self.batch_size),
            tf.float32)

        return ds

    def get_image_ds(self, val=False):
        ''' Returns batched tf.Dataset generator object for images.h5 dataset '''
        return self.load_ds_generator(self.img_path, val=val)

    def get_mask_ds(self, val=False):
        ''' Returns batched tf.Dataset generator object for masks.h5 dataset '''
        return self.load_ds_generator(self.mask_path, val=val)

    def get_binary_ds(self, val=False):
        ''' Returns batched tf.Dataset generator object for binary.h5 dataset '''
        return self.load_ds_generator(self.bin_path, val=val)

    def get_bboxes_ds(self, val=False):
        ''' Returns batched tf.Dataset generator object for bbox.h5 dataset '''
        return self.load_ds_generator(self.bbox_path, val=val)

import os, shutil
from uuid import uuid4
from fastapi import File, UploadFile, HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError
from typing import Optional, List, IO

class SingleImageRequired:
    def __init__(self,max_file_size: int, allow_file_ext: List[str]):
        self.allow_file_ext = allow_file_ext
        self.max_file_size = max_file_size
        self.max_file_size_mb = max_file_size * 1024 * 1024  # convert to Mb

    def __call__(self,file: UploadFile = File(...)):
        # validation image
        try:
            with Image.open(file.file) as img:
                if img.format.lower() not in self.allow_file_ext and img.mode != 'RGB':
                    msg = "Image must be between {}.".format(', '.join(self.allow_file_ext))
                    raise HTTPException(status_code=422,detail=msg)
        except UnidentifiedImageError:
            msg = "Cannot identify the image."
            raise HTTPException(status_code=422,detail=msg)

        # validation size image
        size = file.file
        size.seek(0,os.SEEK_END)
        if size.tell() > self.max_file_size_mb:
            msg_size = f"An image cannot greater than {self.max_file_size} Mb."
            raise HTTPException(status_code=413,detail=msg_size)
        size.seek(0)

        return file

class SingleImageOptional:
    def __init__(self,max_file_size: int, allow_file_ext: List[str]):
        self.allow_file_ext = allow_file_ext
        self.max_file_size = max_file_size
        self.max_file_size_mb = max_file_size * 1024 * 1024  # convert to Mb

    def __call__(self,file: Optional[UploadFile] = File(None)):
        if not file: return

        # validation image
        try:
            with Image.open(file.file) as img:
                if img.format.lower() not in self.allow_file_ext and img.mode != 'RGB':
                    msg = "Image must be between {}.".format(', '.join(self.allow_file_ext))
                    raise HTTPException(status_code=422,detail=msg)
        except UnidentifiedImageError:
            msg = "Cannot identify the image."
            raise HTTPException(status_code=422,detail=msg)

        # validation size image
        size = file.file
        size.seek(0,os.SEEK_END)
        if size.tell() > self.max_file_size_mb:
            msg_size = f"An image cannot greater than {self.max_file_size} Mb."
            raise HTTPException(status_code=413,detail=msg_size)
        size.seek(0)

        return file

class MagicImage:
    base_dir: str = os.path.join(os.path.dirname(__file__),'../static/')
    file_name: str = None

    def __init__(self,square: Optional[bool] = False, **kwargs):
        self.square = square
        self.file = kwargs['file']
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.path_upload = kwargs['path_upload']

    def save_image(self) -> 'MagicImage':
        self.file_name = self._save_image_to_storage(self.file)

    def _save_image_to_storage(self,file: IO) -> str:
        """
        Save an image and manipulate the image base on the user setting

        :param file: File-like object
        :return: Filename
        """
        try:
            with Image.open(file) as img:
                filename = uuid4().hex + '.' + img.format.lower()  # set filename

                if not self.square:
                    img = self._resize_thumbnail(img,self.width,self.height)
                else:
                    img = self._crop_max_square(img).resize((self.width, self.height), Image.LANCZOS)

                img = ImageOps.exif_transpose(img)
                # save image to directory path
                img.save(os.path.join(self.base_dir,self.path_upload,filename))

            return filename
        except AttributeError:
            raise ValueError("The file must be file-like object.")

    def _crop_center(self,pil_img: IO, crop_width: int, crop_height: int) -> IO:
        img_width, img_height = pil_img.size
        return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))

    def _crop_max_square(self,pil_img: IO) -> IO:
        return self._crop_center(pil_img, min(pil_img.size), min(pil_img.size))

    def _resize_thumbnail(self,image: IO, width: int, height: int) -> IO:
        """
        Resizes to the largest size that preserves the aspect ratio, not exceed the original image,
        and does not exceed the size specified in the arguments of thumbnail

        :param image: File-like object
        :param width: width of an image
        :param height: height of an image

        :return: File-like object
        """
        img_format = image.format
        img = image.copy()
        img.thumbnail((width, height), Image.LANCZOS)
        img.format = img_format
        return img

    @classmethod
    def delete_image(cls,file: str, path_delete: str) -> None:
        path = os.path.join(cls.base_dir,path_delete,file or ' ')
        if os.path.exists(path):
            os.remove(path)

    @classmethod
    def rename_folder(cls,old_name: str, new_name: str, path_update: str) -> None:
        path = os.path.join(cls.base_dir,path_update,old_name or ' ')
        if os.path.exists(path):
            os.rename(path,os.path.join(cls.base_dir,path_update,new_name))

    @classmethod
    def delete_folder(cls,name_folder: str, path_delete: str) -> None:
        path = os.path.join(cls.base_dir,path_delete,name_folder or ' ')
        if os.path.exists(path):
            shutil.rmtree(path)

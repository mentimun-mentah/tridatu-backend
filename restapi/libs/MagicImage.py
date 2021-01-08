import os, shutil, dhash
from uuid import uuid4
from fastapi import File, UploadFile, HTTPException
from PIL import Image, ImageOps, UnidentifiedImageError
from typing import Optional, List, IO

def validate_multiple_upload_images(
    images: List[UploadFile],
    allow_file_ext: List[str],
    max_file_size: int,
    max_file_in_list: Optional[int] = None,
    min_file_in_list: Optional[int] = None
) -> List[UploadFile]:
    max_file_size_mb = max_file_size * 1024 * 1024  # convert to Mb

    # for detect duplicate image
    image_hash = list()

    for index, image in enumerate(images, 1):
        # validation image
        try:
            with Image.open(image.file) as img:
                # extract hash image for detect duplicate image
                row_hash, col_hash = dhash.dhash_row_col(img,size=17)
                image_hash.append(dhash.format_hex(row_hash,col_hash))

                if img.format.lower() not in allow_file_ext and img.mode != 'RGB':
                    msg = "The image at index {} must be between {}.".format(index,', '.join(allow_file_ext))
                    raise HTTPException(status_code=422,detail=msg)
        except UnidentifiedImageError:
            msg = f"Cannot identify the image at index {index}."
            raise HTTPException(status_code=422,detail=msg)

        # validation size image
        size = image.file
        size.seek(0,os.SEEK_END)
        if size.tell() > max_file_size_mb:
            msg_size = f"An image at index {index} cannot greater than {max_file_size} Mb."
            raise HTTPException(status_code=413,detail=msg_size)
        size.seek(0)

    # image must be unique in a list of images
    if len(set(image_hash)) != len(image_hash):
        raise HTTPException(status_code=409,detail="Each image must be unique.")

    # check minimum or maximum image in list
    if min_file_in_list and len(images) < min_file_in_list:
        msg_min_file = f"At least {min_file_in_list} image must be upload."
        raise HTTPException(status_code=422,detail=msg_min_file)

    if max_file_in_list and len(images) > max_file_in_list:
        msg_max_file = f"Maximal {max_file_in_list} images to be upload."
        raise HTTPException(status_code=422,detail=msg_max_file)

    return images

def validate_single_upload_image(
    image: UploadFile,
    allow_file_ext: List[str],
    max_file_size: int
) -> UploadFile:
    max_file_size_mb = max_file_size * 1024 * 1024  # convert to Mb

    # validation image
    try:
        with Image.open(image.file) as img:
            if img.format.lower() not in allow_file_ext and img.mode != 'RGB':
                msg = "Image must be between {}.".format(', '.join(allow_file_ext))
                raise HTTPException(status_code=422,detail=msg)
    except UnidentifiedImageError:
        msg = "Cannot identify the image."
        raise HTTPException(status_code=422,detail=msg)

    # validation size image
    size = image.file
    size.seek(0,os.SEEK_END)
    if size.tell() > max_file_size_mb:
        msg_size = f"An image cannot greater than {max_file_size} Mb."
        raise HTTPException(status_code=413,detail=msg_size)
    size.seek(0)

    return image

class SingleImageRequired:
    def __init__(self,max_file_size: int, allow_file_ext: List[str]):
        self.allow_file_ext = allow_file_ext
        self.max_file_size = max_file_size

    def __call__(self,file: UploadFile = File(...)):
        return validate_single_upload_image(
            image=file,
            allow_file_ext=self.allow_file_ext,
            max_file_size=self.max_file_size
        )

class SingleImageOptional:
    def __init__(self,max_file_size: int, allow_file_ext: List[str]):
        self.allow_file_ext = allow_file_ext
        self.max_file_size = max_file_size

    def __call__(self,file: Optional[UploadFile] = File(None)):
        if not file: return

        return validate_single_upload_image(
            image=file,
            allow_file_ext=self.allow_file_ext,
            max_file_size=self.max_file_size
        )

class MagicImage:
    base_dir: str = os.path.join(os.path.dirname(__file__),'../static/')
    file_name: str = None

    def __init__(self,square: Optional[bool] = False, **kwargs):
        self.square = square
        self.file = kwargs['file']
        self.width = kwargs['width']
        self.height = kwargs['height']
        self.path_upload = kwargs['path_upload']
        if 'dir_name' in kwargs:
            self.dir_name = kwargs['dir_name']

    def save_image(self) -> 'MagicImage':
        if isinstance(self.file,list):
            files_name = dict()
            for index, image in enumerate(self.file):
                filename = self._save_image_to_storage(image.file)
                files_name[index] = filename
            self.file_name = files_name
        else:
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
                if hasattr(self,'dir_name'):
                    # create directory if file isn't exists
                    path = os.path.join(self.base_dir,self.path_upload,self.dir_name)
                    if not os.path.exists(path):
                        os.mkdir(path)
                    img.save(os.path.join(path,filename))
                else:
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

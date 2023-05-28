import os
from functools import wraps


def delete_old_photo(photo_path):
    """Delete the old photo file if it exists."""
    if os.path.exists(photo_path):
        os.remove(photo_path)


def delete_old_photo_on_save(original_save_func):
    """Decorator function to delete the old profile picture on save."""
    @wraps(original_save_func)
    def wrapper(self, *args, **kwargs):
        """Wrapper function that handles the save operation."""
        if self.pk:
            UserProfile = self.__class__
            old_instance = UserProfile.objects.get(pk=self.pk)
            if old_instance.profile_picture != self.profile_picture:
                delete_old_photo(old_instance.profile_picture.path)
        return original_save_func(self, *args, **kwargs)

    return wrapper


def delete_old_cover_on_save(original_save_func):
    """Decorator function to delete the old cover photo on save."""
    @wraps(original_save_func)
    def wrapper(self, *args, **kwargs):
        """Wrapper function that handles the save operation."""
        if self.pk:
            UserProfile = self.__class__
            old_instance = UserProfile.objects.get(pk=self.pk)
            if old_instance.cover_photo != self.cover_photo:
                delete_old_photo(old_instance.cover_photo.path)
        return original_save_func(self, *args, **kwargs)

    return wrapper


# def delete_old_license_on_save(original_save_func):
#     """Decorator function to delete the old cover photo on save."""
#     @wraps(original_save_func)
#     def wrapper(self, *args, **kwargs):
#         """Wrapper function that handles the save operation."""
#         if self.pk:
#             Vendor = self.__class__
#             old_instance = Vendor.objects.get(pk=self.pk)
#             if old_instance.vendor_license != self.vendor_license:
#                 delete_old_photo(old_instance.vendor_license.path)
#
#     return wrapper

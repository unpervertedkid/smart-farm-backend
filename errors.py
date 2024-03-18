class UnsupportedCropError(Exception):
    """Exception raised for unsupported crop.

    Attributes:
        crop -- crop which caused the error
        message -- explanation of the error
    """

    def __init__(self, crop, message="Crop is not supported"):
        self.crop = crop
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.crop} -> {self.message}'
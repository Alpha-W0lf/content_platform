# ImageGenerator interface
class ImageGenerator:
    def generate_image(self, prompt: str) -> str:
        raise NotImplementedError("This method should be overridden by subclasses")

# VideoClipGenerator interface
class VideoClipGenerator:
    def generate_video_clip(self, image_path: str) -> str:
        raise NotImplementedError("This method should be overridden by subclasses")

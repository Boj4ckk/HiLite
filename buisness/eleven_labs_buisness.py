from moviepy.editor import VideoFileClip
import tempfile
import os 


class ElevenLabsBuisness:


    @staticmethod
    def extract_audio_bytes_from_video(video_path):
        video = VideoFileClip(video_path)
        audio_bytes = b""

        # Créer un fichier temporaire utilisable par ffmpeg sur Windows
        tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp.close()  # fermer le fichier pour que ffmpeg puisse l'écrire

        try:
            video.audio.write_audiofile(tmp.name)
            with open(tmp.name, "rb") as f:
                audio_bytes = f.read()
        finally:
            os.remove(tmp.name)  # supprimer le fichier temporaire

        video.close()
        if video.audio:
            video.audio.close()

        return audio_bytes

    @staticmethod
    def write_transcription_in_file(transcription):
        with open("test.txt", "w") as f:
            f.write(transcription)
    




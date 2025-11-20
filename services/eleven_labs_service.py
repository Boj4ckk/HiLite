from elevenlabs.client import ElevenLabs
from buisness.eleven_labs_buisness import ElevenLabsBuisness


class ElevenLabsService:

    def __init__(self,api_key):
        self.api_key = api_key
        self.eleven_labs_client = ElevenLabs(
            api_key=self.api_key
        )
    

    def speach_to_text(self,video_path,model_id,tag_audio_events,language_code,diarize):
        eleven_labs_business = ElevenLabsBuisness()
        audio_data = eleven_labs_business.extract_audio_bytes_from_video(video_path)

        transcription = self.eleven_labs_client.speech_to_text.convert(
            file=audio_data,
            model_id=model_id, # model to use
            tag_audio_events=tag_audio_events, #Tag audio event (laugh,applause,etc)
            language_code=language_code,#language of the audio file
            diarize=diarize # Wheter to annotate who is speaking
        )
       
        return transcription


    

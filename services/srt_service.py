from elevenlabs import types

from buisness.srt_buisness import SrtBuisness
class SrtService:
    def __init__(self,transcription : types.speech_to_text_chunk_response_model):
        self.transcription = transcription
        self.str_buisness = SrtBuisness()


 

    def convert_transcription_into_srt(self,srt_output_file):
        words = self.transcription.words
        index = 1

        with open(srt_output_file,"w", encoding="utf-8") as f:

            for index,word in enumerate(words,start=1):
                text = word.text
                start = self.str_buisness.seconds_to_srt_time(word.start)
                end = self.str_buisness.seconds_to_srt_time(word.end)

                f.write(f"{index}\n")
                f.write(f"{start} -->  {end}\n")
                f.write(f"{text}\n\n")
        f.close()
        return srt_output_file


                

        


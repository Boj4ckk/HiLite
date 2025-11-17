

class TwitchBuisness:

    @staticmethod
    def extract_clips_ids(clips_obj):
        clips_ids = []
        for clip in clips_obj:
            clips_ids.append(clip["id"])
        return clips_ids
    @staticmethod
    def extract_clips_url(clip_obj):
        clips_url  = []
     
        for clip in clip_obj:
            
            clips_url.append(clip["url"])
        return clips_url
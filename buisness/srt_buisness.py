class SrtBuisness:
    @staticmethod
    def seconds_to_srt_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    @staticmethod
    def transcription_to_srt_lines(words):
        lines = []
        for index, word in enumerate(words, start=1):
            start = SrtBuisness.seconds_to_srt_time(word.start)
            end = SrtBuisness.seconds_to_srt_time(word.end)
            lines.append(f"{index}\n{start} --> {end}\n{word.text}\n")
        return lines

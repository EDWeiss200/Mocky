import asyncio
from pathlib import Path

async def convert_ogg_to_mp3(file_path: str):
    mp3_path = Path(file_path).with_suffix(".mp3")
    try:
        process = await asyncio.create_subprocess_exec(
            "ffmpeg", "-y", "-i", file_path, "-codec:a", "libmp3lame", "-q:a", "2", str(mp3_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            print(f"FFMPEG ERROR: {stderr.decode()}")
            return None
        return str(mp3_path)
    except FileNotFoundError:
        print("FFMPEG не найден. Установите ffmpeg и добавьте его в PATH.")
        return None
    except Exception as e:
        print(f"Ошибка FFMPEG: {e}")
        return None
    return str(mp3_path)
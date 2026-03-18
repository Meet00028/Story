import asyncio
import edge_tts

async def test_tts():
    text = "Hello world"
    voice = "en-US-ChristopherNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("test_tts.mp3")
    print("TTS Success")

if __name__ == "__main__":
    asyncio.run(test_tts())

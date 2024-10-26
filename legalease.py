from os import environ
from dotenv import load_dotenv
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI as OpenAILLM

if __name__ == "__main__":
    
    load_dotenv()

    OPENAI_API_KEY = environ["OPENAI_API_KEY"]

    # Create an llm object to use for the QueryEngine and the ReActAgent
    llm = OpenAILLM(model="gpt-4o-mini")

    # Add files to different storage contexts and load the indexes
    try:
        storage_context = StorageContext.from_defaults(
            persist_dir="./storage/lyft"
        )
        lyft_index = load_index_from_storage(storage_context)

        storage_context = StorageContext.from_defaults(
            persist_dir="./storage/uber"
        )
        uber_index = load_index_from_storage(storage_context)

        index_loaded = True
    except:
        index_loaded = False

    if not index_loaded:
        # load data
        lyft_docs = SimpleDirectoryReader(
            input_files=["./10k/lyft_2021.pdf"]
        ).load_data()
        uber_docs = SimpleDirectoryReader(
            input_files=["./10k/uber_2021.pdf"]
        ).load_data()

        # build index
        lyft_index = VectorStoreIndex.from_documents(lyft_docs, show_progress=True)
        uber_index = VectorStoreIndex.from_documents(uber_docs, swow_progress=True)
        VectorStoreIndex

        # persist index
        lyft_index.storage_context.persist(persist_dir="./storage/lyft")
        uber_index.storage_context.persist(persist_dir="./storage/uber")

    # Change these to city ordinance things
    lyft_engine = lyft_index.as_query_engine(similarity_top_k=3, llm=llm)
    uber_engine = uber_index.as_query_engine(similarity_top_k=3, llm=llm)

    # define engine tools and their uses
    query_engine_tools = [
        QueryEngineTool(
            query_engine=lyft_engine,
            metadata=ToolMetadata(
                name="lyft_10k",
                description=(
                    "Provides information about Lyft financials for year 2021. "
                    "Use a detailed plain text question as input to the tool."
                ),
            ),
        ),
        QueryEngineTool(
            query_engine=uber_engine,
            metadata=ToolMetadata(
                name="uber_10k",
                description=(
                    "Provides information about Uber financials for year 2021. "
                    "Use a detailed plain text question as input to the tool."
                ),
            ),
        ),
    ]

    # Define the agent
    agent = ReActAgent.from_tools(
        query_engine_tools,
        llm=llm,
        verbose=True,
        max_turns=10,
    )
    from openai import OpenAI

    def transcribe_audio(file_path, api_key, language=None):
        """
        Transcribe an audio file using OpenAI's Whisper model.
    
        Args:
            file_path (str): Path to the audio file
            api_key (str): OpenAI API key
            language (str, optional): Language code (e.g., 'en', 'es', 'fr')
    
        Returns:
            str: Transcribed text
        """
        try:
            client = OpenAI(api_key=api_key)
        
            with open(file_path, "rb") as audio_file:
                # Create transcription request
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="text"
                )
            
            return response
        
        except Exception as e:
            print(f"Error during transcription: {str(e)}")
            return None

    file_path = "./input.mp3"

    input("Press enter to ask your question...")

    import sounddevice as sd
    from scipy.io.wavfile import write

    fs = 44100  # Sample rate
    seconds = 5  # Duration of recording

    myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=1)
    sd.wait()  # Wait until recording is finished
    write(file_path, fs, myrecording)  # Save as WAV file

    # Optional: specify language
    transcription = transcribe_audio(file_path, OPENAI_API_KEY, language="en")

    if transcription:
        print("Transcription:", transcription)
    rag_response = agent.chat(message=transcription)
    print(str(rag_response))

    # Text to speech

    speech_file_path = "./output.wav"
    client = OpenAI(api_key=OPENAI_API_KEY)
    tts_response = client.audio.speech.create(
      model="tts-1",
      voice="alloy",
      input=str(rag_response)
    )

    tts_response.write_to_file(speech_file_path)

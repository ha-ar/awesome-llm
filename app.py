import gradio as gr
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import torch
from mishkal.tashkeel import TashkeelClass # Still need to import the class
import numpy as np
from quran_checker import QuranMistakeChecker

# Load the QURAN-SPECIFIC Whisper model ONCE at startup
# Using the deepdml/whisper-large-v3-turbo-ar-quran-mix model fine-tuned on Quran datasets
try:
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
    
    model_id = "deepdml/whisper-large-v3-turbo-ar-quran-mix"
    
    print(f"Loading Quran-specific model: {model_id}")
    print(f"Using device: {device}")
    
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True
    )
    model.to(device)
    
    processor = AutoProcessor.from_pretrained(model_id)
    
    # Create a pipeline for easier use
    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        torch_dtype=torch_dtype,
        device=device,
    )
    
    print("Quran-specific Whisper model loaded successfully!")
except Exception as e:
    print(f"Failed to load Whisper model: {str(e)}")
    raise

# Initialize Quran mistake checker
try:
    mistake_checker = QuranMistakeChecker()
    print("Quran mistake checker initialized!")
except Exception as e:
    print(f"Failed to initialize mistake checker: {str(e)}")
    mistake_checker = None

# Global variable for accumulated audio.
audio_buffer = np.array([])
# Whisper expects 16kHz audio - this is optimal for both mobile and laptop
WHISPER_SAMPLE_RATE = 16000
accumulated_text = ""  # Store all transcribed text 

def transcribe_streaming_audio(audio_chunk, new_sample_rate):
    global audio_buffer, accumulated_text

    # Initialize TashkeelClass here to ensure it's created and used in the same thread
    # This is safe because mishkal is relatively lightweight to load repeatedly
    try:
        tashkeel_instance = TashkeelClass() 
    except Exception as e:
        # If mishkal itself fails to load, handle gracefully
        print(f"Error initializing TashkeelClass: {e}")
        return accumulated_text, "", f"Error: Failed to load diacritizer ({str(e)})"


    if audio_chunk is None:
        return accumulated_text, "", "Waiting for audio..."

    current_sample_rate_from_gradio, audio_data = audio_chunk
    
    if audio_data is None or len(audio_data) == 0:
        return accumulated_text, "", "No audio data..."
    
    # Resample audio if needed to 16kHz (Whisper's expected sample rate)
    if current_sample_rate_from_gradio != WHISPER_SAMPLE_RATE:
        # Simple resampling - for production, consider using librosa or scipy
        import scipy.signal
        num_samples = int(len(audio_data) * WHISPER_SAMPLE_RATE / current_sample_rate_from_gradio)
        audio_data = np.array(scipy.signal.resample(audio_data, num_samples))
    
    # Ensure audio_data is a numpy array
    audio_data = np.array(audio_data)
    
    # Normalize audio to [-1, 1] range if needed
    if audio_data.dtype != np.float32:
        audio_data = audio_data.astype(np.float32)
    if np.abs(audio_data).max() > 1.0:
        audio_data = audio_data / np.abs(audio_data).max()
    
    audio_buffer = np.concatenate((audio_buffer, audio_data))
    
    # Reduced minimum chunk size for faster response - 0.5 seconds minimum
    min_audio_length_seconds = 0.5
    if len(audio_buffer) / WHISPER_SAMPLE_RATE < min_audio_length_seconds:
        return accumulated_text, "", "Collecting audio..."

    try:
        audio_data_for_whisper = audio_buffer.astype(np.float32)

        # Transcribe using the Quran-specific model pipeline
        result = pipe(
            audio_data_for_whisper,
            generate_kwargs={
                "language": "arabic",
                "task": "transcribe",
            },
            return_timestamps=False,
        )
        
        # Extract transcription from result
        new_transcription = result["text"].strip() if result and "text" in result else ""

        if new_transcription:
            # For Quran recitation, the model already outputs with good accuracy
            # We can still use mishkal for additional diacritization if needed
            diacritized_text = tashkeel_instance.tashkeel(new_transcription)
            
            # Ensure diacritized_text is a string
            if isinstance(diacritized_text, list):
                diacritized_text = " ".join(diacritized_text)
            diacritized_text = str(diacritized_text).strip()
            
            # Append to accumulated text
            if accumulated_text:
                accumulated_text += " " + diacritized_text
            else:
                accumulated_text = diacritized_text
            
            # Debug: Print to console
            print(f"New transcription: {new_transcription}")
            print(f"Diacritized: {diacritized_text}")
            print(f"Accumulated: {accumulated_text[:100]}...")  # First 100 chars
        
        # Keep only last 3 seconds in buffer for overlap (better context)
        max_buffer_seconds = 3.0
        max_buffer_samples = int(max_buffer_seconds * WHISPER_SAMPLE_RATE)
        if len(audio_buffer) > max_buffer_samples:
            audio_buffer = audio_buffer[-max_buffer_samples:]
        else:
            audio_buffer = np.array([])  # Clear if not keeping overlap

        detected_language = "ar"  # Arabic
        processing_status = f"Transcribed {len(audio_data_for_whisper) / WHISPER_SAMPLE_RATE:.2f}s audio | Total words: {len(accumulated_text.split())}"

        return accumulated_text, detected_language, processing_status
    
    except Exception as e:
        print(f"Error during streaming transcription: {e}")
        import traceback
        traceback.print_exc()
        # Don't clear accumulated text on error
        return accumulated_text, "", f"Error: {str(e)}"

def reset_audio_buffer():
    global audio_buffer, accumulated_text
    audio_buffer = np.array([])
    accumulated_text = ""
    return "", "", "Ready for new audio. Press 'Start Audio Input'.", "", ""

def check_mistakes(recited_text: str, expected_verse: str = ""):
    """
    Check the recited text for mistakes against Quran.
    
    Args:
        recited_text: The transcribed recitation
        expected_verse: Optional verse reference like "1:1" for Al-Fatiha verse 1
    
    Returns:
        highlighted_html, report_text, accuracy_score
    """
    if not recited_text or not recited_text.strip():
        return "", "No text to check", "N/A"
    
    if not mistake_checker:
        return recited_text, "Mistake checker not available", "N/A"
    
    try:
        # Check recitation
        result = mistake_checker.check_recitation(
            recited_text, 
            expected_verse if expected_verse else None
        )
        
        if not result['found']:
            return recited_text, result.get('message', 'No matching verse found'), "N/A"
        
        # Return highlighted HTML, report, and accuracy
        highlighted = result['highlighted_html']
        report = result['report']
        accuracy = f"{result['accuracy']:.1f}%"
        
        return highlighted, report, accuracy
        
    except Exception as e:
        print(f"Error checking mistakes: {e}")
        import traceback
        traceback.print_exc()
        return recited_text, f"Error: {str(e)}", "N/A"

# Create the Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# 🕌 Quran Recitation Live Transcriber & Mistake Checker")
    gr.Markdown("### Powered by Whisper-Large-V3-Turbo fine-tuned on Quran datasets")
    gr.Markdown("Click 'Start Audio Input' and recite Quran verses. The transcription will appear as you speak.")
    gr.Markdown("**Features:** ✅ Real-time transcription | ❌ Mistake detection | 📊 Accuracy scoring")
    gr.Markdown("**Model:** Fine-tuned on tarteel-ai Quran datasets for optimal Quranic Arabic recognition")

    with gr.Row():
        with gr.Column():
            live_audio_input = gr.Audio(
                sources=["microphone"], 
                streaming=True, 
                label="🎤 Live Audio Input",
                waveform_options=gr.WaveformOptions(
                    skip_length=0.5,  # Process every 0.5 seconds for faster response
                )
            )
            
            with gr.Row():
                clear_button = gr.Button("🔄 Clear All", variant="secondary")
                check_button = gr.Button("✅ Check for Mistakes", variant="primary")
            
            expected_verse_input = gr.Textbox(
                label="Expected Verse (Optional)",
                placeholder="e.g., 1:1 for Al-Fatiha verse 1",
                info="Leave empty for auto-detection"
            )

        with gr.Column():
            output_diacritized = gr.Textbox(
                label="📝 Transcribed Text", 
                interactive=False,
                rtl=True,  # Enable right-to-left text direction for Arabic
                lines=5,
                max_lines=10
            )
            output_language = gr.Textbox(label="🌐 Detected Language", interactive=False)
            output_status = gr.Textbox(label="⚡ Status", interactive=False, value="Ready")
    
    # Mistake checking section
    gr.Markdown("---")
    gr.Markdown("## 🔍 Mistake Analysis")
    
    with gr.Row():
        with gr.Column():
            mistake_highlighted = gr.HTML(
                label="Highlighted Text",
                value="<div style='padding: 20px; text-align: center; color: #666;'>Click 'Check for Mistakes' to analyze your recitation</div>"
            )
            gr.Markdown("""
            **Color Legend:**
            - 🟢 **Green**: Correct words
            - 🔴 **Red**: Wrong words (hover to see correction)
            - 🟡 **Yellow**: Missing words
            - 🟠 **Orange**: Extra words (should be removed)
            """)
        
        with gr.Column():
            accuracy_score = gr.Textbox(
                label="📊 Accuracy Score",
                value="N/A",
                interactive=False
            )
            mistake_report = gr.Textbox(
                label="📋 Detailed Report",
                lines=15,
                max_lines=20,
                interactive=False
            )

    live_audio_input.stream(
        fn=transcribe_streaming_audio,
        inputs=[live_audio_input, gr.State(WHISPER_SAMPLE_RATE)], 
        outputs=[output_diacritized, output_language, output_status],
    )

    clear_button.click(
        fn=reset_audio_buffer,
        inputs=[],
        outputs=[output_diacritized, output_language, output_status, mistake_highlighted, mistake_report]
    )
    
    check_button.click(
        fn=check_mistakes,
        inputs=[output_diacritized, expected_verse_input],
        outputs=[mistake_highlighted, mistake_report, accuracy_score]
    )

if __name__ == "__main__":
    demo.launch()
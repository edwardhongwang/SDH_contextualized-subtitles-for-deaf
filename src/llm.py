import openai
import os
import dotenv

dotenv.load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

def proofread(transcript_path):
    # Read the entire SRT file
    with open(transcript_path, 'r', encoding='utf-8') as f:
        srt_content = f.read()

    # Prepare the system prompt
    system_prompt = (
        "You are a professional proofreader and editor specializing in transcripts formatted in SRT (SubRip Subtitle) files. "
        "Your primary task is to correct grammatical errors, improve readability, and ensure technical accuracy while preserving "
        "the original SRT numbering, timestamps, and formatting. Follow all provided guidelines meticulously, and do not alter "
        "the original meaning or introduce new content. Maintain the style and tone of the original transcript throughout your edits. "
        "Please pay close attention to the detailed instructions and examples provided. Ensure all corrections align with these guidelines. "
        "Note that your knowledge is up to September 2023. If you are unsure about specific factual information, focus on correcting grammatical "
        "and typographical errors without altering factual content."
    )


    # Prepare the prompt
    prompt = (
        """
**Updated Proofreading and Editing Instructions:**

Please perform a thorough proofreading and editing of the provided transcript. Your goal is to produce a clean, accurate, and well-formatted version that is faithful to the original content but free of errors and inconsistencies. Address the following issues:

1. **Numerical Values:**
   - Correct any mis-transcribed numerical values.
   - Ensure numbers are formatted correctly (e.g., use commas in large numbers like "250,000" instead of "250000").
   - Maintain consistency in units of measurement (e.g., miles, kilometers, feet) and provide conversions if appropriate.

2. **Misinterpretation of Words:**
   - Correct words that have been misinterpreted due to similar sounds (e.g., "can" vs. "can't," "wales" vs. "whales," "weather" vs. "whether").
   - Pay special attention to homophones and context to choose the correct word.

3. **Technical Terms and Terminology:**
   - Correct any misheard or misspelled technical terms, jargon, or names.
   - Ensure consistency in the spelling of names, places, and technical terms throughout the transcript.
   - Verify the correct spelling of specific terms (e.g., "Atigun Pass," "Prudhoe Bay").

4. **Punctuation and Grammar:**
   - Add missing punctuation marks where necessary (commas, periods, apostrophes, etc.).
   - Correct grammatical errors and improve sentence structure for clarity.
   - Ensure proper capitalization of proper nouns (e.g., names of people, places, and landmarks).

5. **Dialogue Formatting:**
   - Combine dialogue lines that are broken awkwardly for better flow.
   - Focus on making the dialogue clear and natural without adding quotation marks.
   - Ensure that the conversation flows smoothly, even without speaker identification.
   - **Do not add quotation marks around dialogue unless necessary for clarity.**

6. **Number Recognition and Formatting:**
   - Improve the recognition and transcription of numbers (e.g., correct "1,000 of dollars" to "thousands of dollars").
   - Ensure numerical expressions are accurate and make sense in context.

7. **Contextual Understanding:**
   - Use context to interpret and correct ambiguous or unclear phrases.
   - Ensure that the transcript accurately reflects the intended meaning.

8. **Consistency Checks:**
   - Maintain consistency in the use of names, technical terms, and units throughout the transcript.
   - Ensure consistent formatting styles (e.g., capitalization, numbering, bullet points).

9. **Subtitle Numbering and Timecodes:**
   - Ensure subtitle numbering is sequential and without gaps.
   - Correct any overlapping or incorrect timecodes to maintain proper synchronization.

10. **Formatting for Readability:**
    - Keep subtitle lines to an appropriate length (aim for a maximum of 42 characters per line).
    - Split or combine lines where necessary to improve readability.
    - Ensure that subtitles are synchronized with the spoken content.

11. **Spelling and Typos:**
    - Correct all spelling mistakes and typos.
    - Double-check commonly confused words and ensure correct usage.

12. **Clarity and Readability:**
    - Improve sentence structure and flow for better comprehension.
    - Avoid run-on sentences and awkward phrasing.
    - Break up long sentences where appropriate.

13. **Units of Measurement:**
    - Ensure consistent use of units (e.g., miles, kilometers) and provide conversions if helpful.
    - Use appropriate abbreviations (e.g., "ft" for feet, "mi" for miles").

14. **Language Usage:**
    - Use appropriate language and tone suitable for the intended audience.
    - Correct any inappropriate language or profanity, considering the context.

15. **Technical Accuracy:**
    - Verify facts, figures, and technical information for accuracy.
    - Use reliable sources if necessary to confirm details.

16. **Homophones and Similar-Sounding Words:**
    - Be cautious with words that sound alike but have different meanings.
    - Use context to determine the correct word (e.g., "toes" vs. "tows").

17. **Misheard Words and Corrections:**
    - Identify and correct misheard words, especially technical terms and proper nouns.
    - Ensure that the terminology used is appropriate for the subject matter.

18. **Subtitle Timing and Synchronization:**
    - Adjust subtitle timing to match the pacing of the spoken content.
    - Ensure that subtitles appear on screen long enough to be read comfortably.

19. **Additional Considerations:**
    - Do not alter the original meaning or introduce new content.
    - Preserve the style and tone of the original speakers as much as possible.
    - Ensure the final transcript is professional, clear, and accurate.

**Note:** Since the input transcript does not have speaker identification, you do not need to add speaker labels. Focus on making the dialogue as clear as possible, using quotation marks to indicate spoken words, and ensuring that the conversation flows naturally.

---

**Example Corrections to Apply:**

- Correct "toes" to "tows" when referring to towing vehicles.
- Standardize place names and capitalize properly (e.g., "Beaver Slide," "Roller Coaster").
- Use "Atigun Pass" consistently instead of variations like "Adagan Pass."
- Correct numerical expressions (e.g., "a quarter of a 1000000" to "a quarter of a million").
- Correct misheard words such as "tehcnical" to "technical" and "terminology" when appropriate.
- Ensure consistency in names (e.g., confirm whether "Luis" or "Luisa" is correct and use it consistently).
- Correct homophones based on context (e.g., "can" vs. "can't," "weather" vs. "whether").

---

Please proceed to apply these guidelines to the transcript below, ensuring that the final version is polished, accurate, and easy to understand.

**Transcript to Proofread:**

"""
        + srt_content
    )



    client = openai.OpenAI(api_key=openai.api_key)
    # Proceed with the API call
    try:
        response = client.chat.completions.create(
            model="o1-preview-2024-09-12",  
            messages=[
                
                {"role": "user", "content": system_prompt + "\n\n" + prompt},
            ]
        )

        # Get the edited transcript
        edited_srt_content = response.choices[0].message.content

        # Determine the output path
        transcript_dir = os.path.dirname(transcript_path)
        transcript_filename = os.path.basename(transcript_path)
        proofread_filename = f"proofread_{transcript_filename}"
        proofread_transcript_path = os.path.join(transcript_dir, proofread_filename)

        # Save the edited transcript
        with open(proofread_transcript_path, 'w', encoding='utf-8') as f:
            f.write(edited_srt_content)

        # Return the output file path
        return proofread_transcript_path

    except openai.OpenAIError as e:
        print(f"OpenAI API error: {e}")
        return None

if __name__ == "__main__":
    proofread_transcript_path = proofread("data/OceanXplorers Giants of the Deep with James Cameron Full Episode  National Geographic_1QeMXEm-BNQ/transcript_nova-2_audio_OceanXplorers Giants of the Deep with James Cameron Full Episode  National Geographic_1QeMXEm-BNQ.srt")
    print(proofread_transcript_path)

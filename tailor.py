import anthropic
import pathlib

client = anthropic.Anthropic()

resume = pathlib.Path("resume.txt").read_text()
jd = pathlib.Path("jd.txt").read_text()

msg = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=2000,
    messages=[{
        "role": "user",
        "content": f"Rewrite this resume to align with the job description. Keep all facts truthful. Reorder and reword to match keywords.\n\nRESUME:\n{resume}\n\nJD:\n{jd}"
    }]
)

output = msg.content[0].text
pathlib.Path("tailored_resume.md").write_text(output)
print("Done! Check tailored_resume.md")
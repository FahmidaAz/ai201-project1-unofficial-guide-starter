"""
app.py — Milestone 5: Gradio Interface
Run:  python app.py
Open: http://localhost:7860
"""

import gradio as gr
from query import ask


def handle_query(question):
    """Called by Gradio on every button click or Enter press."""
    if not question.strip():
        return "Please enter a question.", ""

    result  = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


# ── UI ────────────────────────────────────────────────────────────────────────

with gr.Blocks(title="Tech Career Advisor — Unofficial Guide") as demo:

    gr.Markdown(
        """
        ## Tech Career Advisor — The Unofficial Guide
        Ask anything about **job searching, interviews, salary negotiation, referrals, or bootcamps**.
        Answers are grounded in curated documents — not general AI knowledge.
        """
    )

    with gr.Row():
        inp = gr.Textbox(
            label       = "Your question",
            placeholder = "e.g. How do I negotiate a higher salary offer?",
            lines       = 2,
            scale       = 4,
        )

    btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer = gr.Textbox(
            label       = "Answer",
            lines       = 10,
            interactive = False,
            scale       = 3,
        )
        sources = gr.Textbox(
            label       = "Retrieved from",
            lines       = 10,
            interactive = False,
            scale       = 1,
        )

    gr.Examples(
        examples = [
            ["What should I put on my resume if I have no experience?"],
            ["How do I negotiate a higher salary offer?"],
            ["How many LeetCode problems do I need before interviews?"],
            ["Is a coding bootcamp worth it for getting a tech job?"],
            ["How do I get a referral at a big tech company?"],
        ],
        inputs = inp,
    )

    # Wire up both button click and pressing Enter in the text box
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])


if __name__ == "__main__":
    demo.launch()